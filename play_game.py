import argparse
import os
import random
import pygame
import requests
from io import BytesIO
from PIL import Image


CARD_W, CARD_H = 120, 170
COLS, ROWS = 13, 4
SUITS = ['C', 'D', 'H', 'S']
VALUES = ['A', '2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K'] # T = 10, no JOKERS


def generate_sprite_sheet():
    os.makedirs("assets", exist_ok=True)
    target_path = "assets/cards_spritesheet.png"
    
    if os.path.exists(target_path):
        return target_path

    sheet = Image.new("RGBA", ((COLS + 1) * CARD_W, ROWS * CARD_H), (0, 0, 0, 0))

    face_url = "https://raw.githubusercontent.com/Xadeck/xCards/master/png/face/{val}{suit}@1x.png"
    back_url = "https://raw.githubusercontent.com/Xadeck/xCards/master/png/back/bicycle_blue@1x.png"
    
    print("Executing HTTP GET requests for asset pipeline...")
    for suit_idx, suit in enumerate(SUITS):
        for val_idx, val in enumerate(VALUES):
            try:
                url = face_url.format(suit=suit.upper(), val=val.upper())
                print(url)
                response = requests.get(url)
                img = Image.open(BytesIO(response.content)) 
                
                img = img.resize((CARD_W, CARD_H), Image.Resampling.LANCZOS)
                x_coord = val_idx * CARD_W
                y_coord = suit_idx * CARD_H
                sheet.paste(img, (x_coord, y_coord))
            except Exception as e:
                print(f"Failed to fetch {url}. Error: {e}")
                pass
    
    try:
        print(back_url)
        response = requests.get(back_url)
        img = Image.open(BytesIO(response.content))
        
        img = img.resize((CARD_W, CARD_H), Image.Resampling.LANCZOS)
        x_coord = val_idx * CARD_W
        y_coord = suit_idx * CARD_H
        sheet.paste(img, (13 * CARD_W, 0))
    except Exception as e:
        print(f"Error downloading card back: {e}")
        pass
                
    sheet.save(target_path)
    print(f"Sprite sheet successfully saved to {target_path}")
    return target_path

class Hand:
    def __init__(self, bet=0):
        self.cards = []
        self.bet = bet
        self.is_standing = False
        self.is_busted = False
        
    def add_card(self, card):
        self.cards.append(card)
        
    def score(self):
        total = 0
        aces = 0
        for card in self.cards:
            val = card['value']
            if val in ['J', 'Q', 'K']:
                total += 10
            elif val == 'A':
                aces += 1
                total += 11
            else:
                total += int(val) if val is not "T" else 10
                
        while total > 21 and aces > 0:
            total -= 10
            aces -= 1
            
        if total > 21:
            self.is_busted = True
            self.is_standing = True
            
        return total

class Shoe:
    def __init__(self, num_decks=1):
        self.num_decks = num_decks
        self.initial_size = num_decks * 52
        self.cards = []
        self.build_shoe()
        
    def build_shoe(self):
        self.cards = [{'suit': s, 'value': v} for _ in range(self.num_decks) for s in SUITS for v in VALUES]
        random.shuffle(self.cards)
        
    def draw(self):
        if not self.cards: return None
        return self.cards.pop()
        
    def validate_refill(self):
        threshold_limit = self.initial_size / 3
        if len(self.cards) <= threshold_limit:
            if random.random() <= 0.20:
                self.build_shoe()

class GameManager:
    def __init__(self):
        self.shoe = Shoe(num_decks=6)
        self.player_hands = [Hand(bet=10)]
        self.dealer_hand = Hand()
        self.active_hand_idx = 0
        self.game_over = False
        self.result_message = ""
        
    def execute_deal(self):
        self.player_hands = [Hand(bet=10)]
        self.dealer_hand = Hand()
        self.active_hand_idx = 0
        self.game_over = False
        self.result_message = ""
        
        for _ in range(2):
            self.player_hands[0].add_card(self.shoe.draw())
            self.dealer_hand.add_card(self.shoe.draw())

        if self.player_hands[0].score() == 21:
            self.player_hands[0].is_standing = True
            self.resolve_dealer()

    def resolve_dealer(self):
        self.game_over = True

        while self.dealer_hand.score() < 17:
            self.dealer_hand.add_card(self.shoe.draw())
        
        self.process_payouts()
            
    def process_payouts(self):
        dealer_score = self.dealer_hand.score()
        for hand in self.player_hands:
            score = hand.score()
            if hand.is_busted:
                self.result_message = "Player Bust. Wager forfeited."
            elif dealer_score > 21:
                self.result_message = "Dealer Bust. Player wins 1:1."
            elif score == 21 and len(hand.cards) == 2:
                self.result_message = "Natural Blackjack. Payout at 3:2 odds."
            elif score > dealer_score:
                self.result_message = "High Score. Player wins 1:1."
            elif score == dealer_score:
                self.result_message = "Push State. Wager returned."
            else:
                self.result_message = "Dealer Wins. Wager forfeited."
        self.shoe.validate_refill()

def get_card_rect(card):
    suit_idx = SUITS.index(card['suit'])
    val_idx = VALUES.index(card['value'])
    return pygame.Rect(val_idx * CARD_W, suit_idx * CARD_H, CARD_W, CARD_H)

def main():
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Blackjack Simulator")

    pygame.font.init()
    font_large = pygame.font.SysFont(None, 48)
    font_small = pygame.font.SysFont(None, 24)
    
    sprite_path = generate_sprite_sheet()
    sprite_sheet = pygame.image.load(sprite_path).convert_alpha()
    
    manager = GameManager()
    manager.execute_deal()
    
    running = True
    while running:
        active_hand = manager.player_hands[manager.active_hand_idx]

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                
                if event.key == pygame.K_r:
                    manager = GameManager()
                    manager.execute_deal()
                    
                elif event.key == pygame.K_SPACE and manager.game_over:
                    manager.execute_deal()
                    

                elif not manager.game_over:
                    if event.key == pygame.K_h and not active_hand.is_standing:
                        active_hand.add_card(manager.shoe.draw())
                        if active_hand.score() >= 21: 
                            active_hand.is_standing = True
                            manager.resolve_dealer()
                            
                    elif event.key == pygame.K_s:
                        active_hand.is_standing = True
                        manager.resolve_dealer()
                        
                    elif event.key == pygame.K_d and len(active_hand.cards) == 2:
                        active_hand.bet *= 2
                        active_hand.add_card(manager.shoe.draw())
                        active_hand.is_standing = True
                        manager.resolve_dealer()
                        
        screen.fill((35, 100, 35))
        
        controls_text = font_small.render("H: Hit | S: Stand | D: Double | R: Reset Game | SPACE: Next Hand", True, (200, 200, 200))
        screen.blit(controls_text, (10, 560))

        dealer_label = font_small.render(f"Dealer Score: {'?' if not manager.game_over else manager.dealer_hand.score()}", True, (255, 255, 255))
        screen.blit(dealer_label, (330, 20))
        
        for i, card in enumerate(manager.dealer_hand.cards):
            x, y = 330 + (i * 50), 50
            if i == 1 and not manager.game_over:
                rect = pygame.Rect(13 * CARD_W, 0 * CARD_H, CARD_W, CARD_H)
                screen.blit(sprite_sheet, (x, y), area=rect)
                pygame.draw.rect(screen, (0, 0, 0), (x, y, CARD_W, CARD_H), 2)

            else:
                rect = get_card_rect(card)
                screen.blit(sprite_sheet, (x, y), area=rect)
                pygame.draw.rect(screen, (0, 0, 0), (x, y, CARD_W, CARD_H), 2)

        for h_idx, hand in enumerate(manager.player_hands):
            player_label = font_small.render(f"Player Score: {hand.score()} | Bet: ${hand.bet}", True, (255, 255, 255))
            screen.blit(player_label, (310, 300 + (h_idx * 200)))
            
            for c_idx, card in enumerate(hand.cards):
                x, y = 330 + (c_idx * 50), 330 + (h_idx * 200)
                rect = get_card_rect(card)
                screen.blit(sprite_sheet, (x, y), area=rect)
                pygame.draw.rect(screen, (0, 0, 0), (x, y, CARD_W, CARD_H), 2)

        if manager.game_over:
            result_display = font_large.render(manager.result_message, True, (255, 215, 0))
            screen.blit(result_display, (400 - result_display.get_width() // 2, 250))

        pygame.display.flip()
        
    pygame.quit()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="A script with simulated and online flags."
    )

    group = parser.add_mutually_exclusive_group(required=True)

    group.add_argument(
        "-s",
        "--simulated",
        action="store_true",
        help="Enable simulated mode (default: False)",
    )

    group.add_argument(
        "-o",
        "--online",
        action="store_true",
        help="Enable online mode (default: False)",
    )
    args = parser.parse_args()

    if args.simulated:
        main()
    else:
        pass
        # online_environment()