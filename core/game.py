from core.game_state import GameState
from core.deck import Deck
from core.pot import Pot
from players.player import Player
from core.betting_round import BettingRound
from players.ai_easy import EasyAI
from core.hand_evaluator import evaluate_7cards
from PySide6.QtCore import QTimer


class HoldemGame:
    def __init__(self, human_action):
        self.players = [
            Player("Human"),
            Player("AI", ai=EasyAI())
        ]

        self.gui = None
        self.human_action = human_action
        self.waiting_for_human = False
        self.deck = Deck()
        self.pot = Pot()
        self.community_cards = []
        self.timer = QTimer()
        self.timer.timeout.connect(self.game_loop)
        self.small_blind = 10
        self.big_blind = 20

        self.dealer_index = 0

    def start(self):
        self.state = GameState.NEW_HAND
        self.waiting_for_human = False
        self.timer.start(500)   # 0.5초마다 game_loop 실행
    # ==================================================
    # 🔁 GAME LOOP
    # ==================================================
    def card_to_str(self, card):
        rank_map = {11:"J",12:"Q",13:"K",14:"A"}
        r = rank_map.get(card.rank, str(card.rank))
        return f"{r}{card.suit}"
    

    def game_loop(self):
        if self.state == GameState.NEW_HAND:
            self.new_hand()

        elif self.state == GameState.POST_BLINDS:
            self.post_blinds()

        elif self.state == GameState.DEAL_HOLE_CARDS:
            self.deal_hole_cards()

        elif self.state == GameState.BETTING_PREFLOP:
            if self.betting_action():
                self.state = GameState.DEAL_FLOP

        elif self.state == GameState.DEAL_FLOP:
            self.deal_flop()
            self.state = GameState.BETTING_FLOP

        elif self.state == GameState.BETTING_FLOP:
            if self.betting_action():
                self.state = GameState.DEAL_TURN

        elif self.state == GameState.DEAL_TURN:
            self.deal_turn()
            self.state = GameState.BETTING_TURN

        elif self.state == GameState.BETTING_TURN:
            if self.betting_action():
                self.state = GameState.DEAL_RIVER

        elif self.state == GameState.DEAL_RIVER:
            self.deal_river()
            self.state = GameState.BETTING_RIVER

        elif self.state == GameState.BETTING_RIVER:
            if self.betting_action():
                self.state = GameState.SHOWDOWN

        elif self.state == GameState.SHOWDOWN:
            self.showdown()
            self.state = GameState.END_HAND

        elif self.state == GameState.END_HAND:
            print("=== HAND END ===\n")
            self.dealer_index = (self.dealer_index + 1) % len(self.players)
            self.state = GameState.NEW_HAND
        
        for p in self.players:
            if p.chips <= 0:
                winner = self.players[1] if p == self.players[0] else self.players[0]
                if self.gui:
                    self.timer.stop()  # 루프 중지
                    self.gui.poker_screen.show_game_over(winner.name)
                return
    # ==================================================
    # 🆕 HAND START
    # ==================================================

    def new_hand(self):
        print("\n=== NEW HAND ===")

        self.deck.reset()
        self.deck.shuffle()
        self.community_cards.clear()
        self.pot.reset()

        for p in self.players:
            p.reset_for_new_hand()
        self.human_action.reset()
        self.waiting_for_human = False

        self.state = GameState.POST_BLINDS

        if self.gui:
            self.gui.poker_screen.update_chips(self.players[0].chips, self.players[1].chips)
            self.gui.poker_screen.update_bets(to_call=0, pot=self.pot.total)

    # ==================================================
    # 💰 BLINDS
    # ==================================================

    def post_blinds(self):
        print("Posting blinds...")

        sb = self.players[(self.dealer_index + 1) % len(self.players)]
        bb = self.players[(self.dealer_index + 2) % len(self.players)]

        sb_amt = min(self.small_blind, sb.chips)
        bb_amt = min(self.big_blind, bb.chips)

        sb.chips -= sb_amt
        bb.chips -= bb_amt

        sb.current_bet = sb_amt
        bb.current_bet = bb_amt

        self.pot.add_bet(sb, sb_amt)
        self.pot.add_bet(bb, bb_amt)

        print(f"{sb.name} posts SB {sb_amt}")
        print(f"{bb.name} posts BB {bb_amt}")

        self.betting = BettingRound(
            players=self.players,
            start_index=(self.dealer_index + 3) % len(self.players),
            big_blind=self.big_blind
        )
        self.betting.current_bet = self.big_blind
        self.betting.acted = {p: False for p in self.players}

        self.state = GameState.DEAL_HOLE_CARDS

    # ==================================================
    # 🃏 DEALING
    # ==================================================

    def deal_hole_cards(self):
        print("Dealing hole cards...")
        for _ in range(2):
            for p in self.players:
                p.hole_cards.append(self.deck.draw())

        for p in self.players:
            print(f"{p.name} hand: {[(c.rank, c.suit) for c in p.hole_cards]}")
        
        # GUI 업데이트
        if self.gui:
            self.gui.update_cards(self.players, self.community_cards, reveal_ai=False)
            
        self.state = GameState.BETTING_PREFLOP

    def deal_flop(self):
        print("Dealing FLOP...")
        self.deck.burn()
        for _ in range(3):
            self.community_cards.append(self.deck.draw())
        print("Community:", self.community_cards)
        if self.gui:
            self.gui.update_cards(self.players, self.community_cards, reveal_ai=False)
            
        self.state = GameState.BETTING_FLOP

    def deal_turn(self):
        print("Dealing TURN...")
        self.deck.burn()
        self.community_cards.append(self.deck.draw())
        print("Community:", self.community_cards)
        if self.gui:
            self.gui.update_cards(self.players, self.community_cards, reveal_ai=False)
        self.state = GameState.BETTING_TURN

    def deal_river(self):
        print("Dealing RIVER...")
        self.deck.burn()
        self.community_cards.append(self.deck.draw())
        print("Community:", self.community_cards)
        if self.gui:
            self.gui.update_cards(self.players, self.community_cards, reveal_ai=False)
        self.state = GameState.BETTING_RIVER

    # ==================================================
    # 🎯 BETTING
    # ==================================================

    def betting_action(self):
        br = self.betting
        player = self.players[br.turn_index]

        # 베팅 라운드 종료
        if br.all_acted_or_all_in():
            print("Betting round finished\n")
            for p in self.players:
                p.current_bet = 0
                self.waiting_for_human = False
            return True
        
        # 폴드 / 올인 플레이어 스킵
        if player.folded or player.all_in:
            br.next_player()
            return False

        to_call = br.current_bet - player.current_bet

        # 🤖 AI
        if player.ai:
            action, amount = player.ai.decide(
                player=player,
                to_call=to_call,
                big_blind=self.big_blind
            )

            if action == "fold":
                print(f"{player.name} FOLDS")
                player.folded = True
                br.mark_acted(player)

            elif action == "check":
                print(f"{player.name} CHECKS")
                br.mark_acted(player)

            elif action == "call":
                print(f"{player.name} CALLS {to_call}")
                self.place_bet(player, to_call)  # place_bet이 mark_acted 처리함

            elif action == "raise":
                print(f"{player.name} RAISES to {amount}")
                self.place_bet(player, amount)   # place_bet이 reset_acted_except까지 처리함

            br.next_player()
            return False

        
        # 👤 Human
        if not player.ai:
            if not self.waiting_for_human:
                self.waiting_for_human = True
                print(f"\n{player.name}'s TURN")
                print(f"Chips: {player.chips}")
                print(f"To call: {to_call}")
                self.waiting_for_human = True

            # GUI 입력 아직 없음 → 프레임 종료
            if not self.human_action.ready():
                return False

            # 입력 확정
            action = self.human_action.action
            amount = self.human_action.amount

            self.human_action.reset()
            self.waiting_for_human = False

            self.apply_action(player, action, amount)
            self.betting.next_player()
            return False
        
    def apply_action(self, player, action, amount):
        br = self.betting
        to_call = br.current_bet - player.current_bet

        if action == "fold":
            print(f"{player.name} FOLDS")
            player.folded = True
            br.mark_acted(player)
            return

        if action == "call":
            print(f"{player.name} CALLS {to_call}")
            self.place_bet(player, to_call)
            return

        if action == "check":
            print(f"{player.name} CHECKS")
            br.mark_acted(player)
            return

        if action == "raise":
            # raise는 "추가 금액" 기준
            total = to_call + amount
            print(f"{player.name} RAISES by {amount} (total {total})")
            self.place_bet(player, total)
            return


    def place_bet(self, player, amount):
        br = self.betting

        before_round_bet = br.current_bet
        before_player_bet = player.current_bet

        real = min(amount, player.chips)
        player.chips -= real
        player.current_bet += real

        self.pot.add_bet(player, real)

        # ✅ acted 처리
        br.mark_acted(player)

        # ✅ 라운드 최고 베팅 갱신 + 레이즈면 acted 리셋
        if player.current_bet > before_round_bet:
            raise_size = player.current_bet - before_round_bet
            br.min_raise = max(br.min_raise, raise_size)
            br.current_bet = player.current_bet
            br.last_raiser = player
            br.reset_acted_except(player)
        else:
            br.current_bet = max(br.current_bet, player.current_bet)

        if player.chips == 0:
            player.all_in = True

        if self.gui:
            self.gui.poker_screen.update_chips(self.players[0].chips, self.players[1].chips)

            # to_call/pot UI도 같이 갱신해주는게 좋음
            human = self.players[0]
            to_call = br.current_bet - human.current_bet
            # pot 총액은 너 Pot 구현에 맞춰 수정
            self.gui.poker_screen.update_bets(to_call=to_call, pot=self.pot.total)

    # ==================================================
    # 🏆 SHOWDOWN
    # ==================================================

    def showdown(self):
        print("\n=== SHOWDOWN ===")

        active = [p for p in self.players if not p.folded]
        scores = {}

        for p in active:
            score = evaluate_7cards(p.hole_cards + self.community_cards)
            scores[p] = score
            print(f"{p.name} score: {score}")

        pots = self.pot.build_pots()
        if self.gui:
            self.gui.poker_screen.update_chips(self.players[0].chips, self.players[1].chips)

        for pot_amount, eligible in pots:
            contenders = [p for p in eligible if not p.folded]
            best = max(scores[p] for p in contenders)
            winners = [p for p in contenders if scores[p] == best]

            share = pot_amount // len(winners)
            for w in winners:
                w.chips += share
                print(f"{w.name} wins {share}")
        if self.gui:
            self.gui.update_cards(self.players, self.community_cards, reveal_ai=True)

        self.pot.reset()
