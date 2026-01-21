# core/game.py
from __future__ import annotations

from core.game_state import GameState
from core.deck import Deck
from core.pot import Pot
from players.player import Player
from core.betting_round import BettingRound
from players.ai_easy import EasyAI
from players.ai_normal import NormalAI
from players.ai_hard import HardAI
from core.hand_evaluator import evaluate_7cards
from PySide6.QtCore import QTimer


class HoldemGame:
    def __init__(self, human_action):
        self.gui = None
        self.human_action = human_action
        self.waiting_for_human = False

        self.deck = Deck()
        self.pot = Pot()
        self.community_cards = []

        self.small_blind = 10
        self.big_blind = 20
        self.dealer_index = 0

        self.timer = QTimer()
        self.timer.timeout.connect(self.game_loop)

        self.players: list[Player] = []
        self.state = GameState.NEW_HAND

        # ✅ 런아웃/공개 플래그
        self.runout_mode = False          # 올인/베팅 불가면 True
        self.reveal_ai = False            # UI에서 AI 카드 공개 여부(딜레이 포함)
        self._waiting_next_hand = False   # 3초 대기 중

        # ✅ 기본값: Normal / 1000 / BB=20 (SB=10)
        self.configure(ai_count=1, difficulty="Normal", start_chips=1000, bb=20)

    def stop(self):
        if hasattr(self, "timer") and self.timer.isActive():
            self.timer.stop()

    def _make_ai(self, difficulty: str):
        d = (difficulty or "Normal").lower()
        if d == "normal" and NormalAI is not None:
            return NormalAI()
        if d == "hard" and HardAI is not None:
            return HardAI()
        return EasyAI()

    def _emit(self, msg: str):
        print(msg)
        if self.gui:
            self.gui.show_action(msg)

    def _sync_ui(self, to_call: int = 0):
        if not self.gui:
            return
        self.gui.poker_screen.update_bets(
            to_call=max(0, int(to_call)),
            pot=self.pot.total,
            sb=self.small_blind,
            bb=self.big_blind
        )

    def _refresh_ui(self, to_call: int = 0):
        if not self.gui:
            return
        self.gui.update_cards(self.players, self.community_cards, reveal_ai=self.reveal_ai)
        self._sync_ui(to_call=to_call)

    # ✅ Home/Window와 포맷 완전 일치
    def configure(self, ai_count: int, difficulty: str, start_chips: int, bb: int):
        ai_count = max(1, min(4, int(ai_count)))
        start_chips = max(1, int(start_chips))
        bb = max(2, int(bb))
        if bb % 2 != 0:
            bb += 1

        sb = max(1, bb // 2)
        self.small_blind = sb
        self.big_blind = bb

        self.stop()

        self.players = [Player("Human", chips=start_chips)]
        for i in range(ai_count):
            self.players.append(Player(f"AI{i+1}", chips=start_chips, ai=self._make_ai(difficulty)))

        self.dealer_index = 0
        self.state = GameState.NEW_HAND
        self.waiting_for_human = False
        self.human_action.reset()

        self.runout_mode = False
        self.reveal_ai = False
        self._waiting_next_hand = False

    def start(self):
        self.state = GameState.NEW_HAND
        self.waiting_for_human = False
        self.human_action.reset()

        self.runout_mode = False
        self.reveal_ai = False
        self._waiting_next_hand = False

        if self.timer.isActive():
            self.timer.stop()
        self.timer.start(250)

    # ==================================================
    # GAME LOOP
    # ==================================================
    def game_loop(self):
        if self._waiting_next_hand:
            return

        if self.state == GameState.NEW_HAND:
            self.new_hand()
            return

        if self.state == GameState.POST_BLINDS:
            self.post_blinds()
            return

        if self.state == GameState.DEAL_HOLE_CARDS:
            self.deal_hole_cards()
            return

        if self.state == GameState.BETTING_PREFLOP:
            if self.betting_action():
                self.state = GameState.DEAL_FLOP
            return

        if self.state == GameState.DEAL_FLOP:
            self.deal_flop()
            if self.runout_mode:
                self.state = GameState.DEAL_TURN
            else:
                self._start_betting_round_postflop()
                self.state = GameState.BETTING_FLOP
            return

        if self.state == GameState.BETTING_FLOP:
            if self.betting_action():
                self.state = GameState.DEAL_TURN
            return

        if self.state == GameState.DEAL_TURN:
            self.deal_turn()
            if self.runout_mode:
                self.state = GameState.DEAL_RIVER
            else:
                self._start_betting_round_postflop()
                self.state = GameState.BETTING_TURN
            return

        if self.state == GameState.BETTING_TURN:
            if self.betting_action():
                self.state = GameState.DEAL_RIVER
            return

        if self.state == GameState.DEAL_RIVER:
            self.deal_river()
            if self.runout_mode:
                self.state = GameState.SHOWDOWN
            else:
                self._start_betting_round_postflop()
                self.state = GameState.BETTING_RIVER
            return

        if self.state == GameState.BETTING_RIVER:
            if self.betting_action():
                self.state = GameState.SHOWDOWN
            return

        if self.state == GameState.SHOWDOWN:
            self.showdown()
            self.state = GameState.END_HAND
            return

        if self.state == GameState.END_HAND:
            self.end_hand()
            return

    # ==================================================
    # HAND FLOW
    # ==================================================
    def new_hand(self):
        self.runout_mode = False
        self.reveal_ai = False

        self.deck.reset()
        self.deck.shuffle()
        self.community_cards.clear()
        self.pot.reset()

        for p in self.players:
            p.reset_for_new_hand()

        self.human_action.reset()
        self.waiting_for_human = False
        self.state = GameState.POST_BLINDS

        self._refresh_ui(to_call=0)

    def post_blinds(self):
        n = len(self.players)
        if n == 2:
            sb_index = self.dealer_index
            bb_index = (self.dealer_index + 1) % n
            first_to_act = sb_index
        else:
            sb_index = (self.dealer_index + 1) % n
            bb_index = (self.dealer_index + 2) % n
            first_to_act = (self.dealer_index + 3) % n

        sbp = self.players[sb_index]
        bbp = self.players[bb_index]

        sb_amt = min(self.small_blind, sbp.chips)
        bb_amt = min(self.big_blind, bbp.chips)

        sbp.chips -= sb_amt
        bbp.chips -= bb_amt

        sbp.current_bet = sb_amt
        bbp.current_bet = bb_amt

        self.pot.add_bet(sbp, sb_amt)
        self.pot.add_bet(bbp, bb_amt)

        self._emit(f"{sbp.name} POSTS SB {sb_amt}")
        self._emit(f"{bbp.name} POSTS BB {bb_amt}")

        self.betting = BettingRound(players=self.players, start_index=first_to_act, big_blind=self.big_blind)
        self.betting.current_bet = bb_amt  # 실제 BB

        human = self.players[0]
        self._refresh_ui(to_call=max(0, self.betting.current_bet - human.current_bet))
        if self.gui:
            self.gui.poker_screen.highlight_current_seat(self.players[first_to_act].name)

        self.state = GameState.DEAL_HOLE_CARDS

    def deal_hole_cards(self):
        for _ in range(2):
            for p in self.players:
                p.hole_cards.append(self.deck.draw())
        self._refresh_ui(to_call=0)
        self.state = GameState.BETTING_PREFLOP

    def deal_flop(self):
        self.deck.burn()
        for _ in range(3):
            self.community_cards.append(self.deck.draw())
        self._refresh_ui(to_call=0)

    def deal_turn(self):
        self.deck.burn()
        self.community_cards.append(self.deck.draw())
        self._refresh_ui(to_call=0)

    def deal_river(self):
        self.deck.burn()
        self.community_cards.append(self.deck.draw())
        self._refresh_ui(to_call=0)

    def _start_betting_round_postflop(self):
        n = len(self.players)

        for p in self.players:
            p.current_bet = 0

        # HU: BB가 먼저 / 3+ : SB(딜러 왼쪽) 먼저
        start_index = (self.dealer_index + 1) % n
        self.betting = BettingRound(players=self.players, start_index=start_index, big_blind=self.big_blind)
        self.betting.current_bet = 0

        self.human_action.reset()
        self.waiting_for_human = False

        if self.gui:
            self.gui.poker_screen.highlight_current_seat(self.players[start_index].name)

    # ==================================================
    # RUNOUT
    # ==================================================
    def _no_more_betting_possible(self) -> bool:
        alive = [p for p in self.players if not p.folded]
        if len(alive) <= 1:
            return False
        can_bet = [p for p in alive if (not p.all_in) and p.chips > 0]
        return len(can_bet) <= 1

    def _enter_runout_mode(self):
        if self.runout_mode:
            return
        self.runout_mode = True
        self.reveal_ai = True
        if self.gui:
            self.gui.poker_screen.set_actions_enabled(False)
            self.gui.poker_screen.set_status_text("ALL-IN → Running out…")
        self._emit("ALL-IN / No more betting → Running out board")
        self._refresh_ui(to_call=0)

    # ==================================================
    # BETTING
    # ==================================================
    def betting_action(self) -> bool:
        br = self.betting

        # 승리(폴드로 1명 남음)
        alive = [p for p in self.players if not p.folded]
        if len(alive) == 1:
            winner = alive[0]
            win_amount = self.pot.total
            winner.chips += win_amount
            self.pot.reset()

            self.reveal_ai = True
            self._emit(f"{winner.name} wins (everyone folded) +{win_amount}")
            self._refresh_ui(to_call=0)

            self.state = GameState.END_HAND
            return False

        # 라운드 종료
        if br.all_acted_or_all_in():
            # 다음 스트리트로 넘어갈 때 bet 리셋
            for p in self.players:
                p.current_bet = 0
            self.waiting_for_human = False

            if self._no_more_betting_possible():
                self._enter_runout_mode()

            self._refresh_ui(to_call=0)
            return True

        player = self.players[br.turn_index]
        if self.gui:
            self.gui.poker_screen.highlight_current_seat(player.name)

        # 폴드/올인 스킵
        if player.folded or player.all_in:
            br.next_player()
            return False

        to_call = br.current_bet - player.current_bet
        human = self.players[0]

        # AI
        if player.ai:
            if self.gui:
                self.gui.poker_screen.set_actions_enabled(False)
                self.gui.poker_screen.set_status_text("AI thinking…")

            action, amount = player.ai.decide(player=player, to_call=to_call, big_blind=self.big_blind)

            if action == "fold":
                player.folded = True
                br.mark_acted(player)
                self._emit(f"{player.name} FOLDS")

            elif action == "check":
                br.mark_acted(player)
                self._emit(f"{player.name} CHECKS")

            elif action == "call":
                self.place_bet(player, to_call)
                self._emit(f"{player.name} CALLS {to_call}")

            elif action == "raise":
                # amount는 "이번 턴에 넣을 칩"(콜 포함)로 취급
                self.place_bet(player, int(amount))
                self._emit(f"{player.name} RAISES TO {br.current_bet}")

            br.next_player()

            # 다음 플레이어 기준 to_call 갱신
            next_to_call = max(0, br.current_bet - human.current_bet)
            self._refresh_ui(to_call=next_to_call)
            return False

        # Human
        if not self.waiting_for_human:
            self.waiting_for_human = True
            if self.gui:
                self.gui.poker_screen.set_actions_enabled(True)
                self.gui.poker_screen.set_status_text("Your turn")
            self._refresh_ui(to_call=to_call)

        if not self.human_action.ready():
            return False

        action = self.human_action.action
        amount = int(self.human_action.amount or 0)
        self.human_action.reset()
        self.waiting_for_human = False

        self.apply_action(player, action, amount)

        if self.gui:
            self.gui.poker_screen.set_actions_enabled(False)

        br.next_player()
        next_to_call = max(0, br.current_bet - human.current_bet)
        self._refresh_ui(to_call=next_to_call)
        return False

    def apply_action(self, player, action, amount):
        br = self.betting
        to_call = br.current_bet - player.current_bet

        if action == "fold":
            player.folded = True
            br.mark_acted(player)
            self._emit(f"{player.name} FOLDS")
            return

        if action == "check":
            br.mark_acted(player)
            self._emit(f"{player.name} CHECKS")
            return

        if action == "call":
            self.place_bet(player, to_call)
            self._emit(f"{player.name} CALLS {to_call}")
            return

        if action == "raise":
            # amount는 "이번 턴에 넣을 칩"(콜 포함)로 취급
            if amount <= to_call:
                self.place_bet(player, to_call)
                self._emit(f"{player.name} CALLS {to_call}")
                return

            self.place_bet(player, amount)
            self._emit(f"{player.name} RAISES TO {br.current_bet}")
            return

    def place_bet(self, player, amount):
        br = self.betting

        before_round_bet = br.current_bet

        real = min(int(amount), player.chips)
        player.chips -= real
        player.current_bet += real
        self.pot.add_bet(player, real)

        br.mark_acted(player)

        # 라운드 최고 베팅 갱신
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

        if self._no_more_betting_possible():
            self._enter_runout_mode()

    # ==================================================
    # SHOWDOWN / END
    # ==================================================
    def showdown(self):
        active = [p for p in self.players if not p.folded]
        scores = {p: evaluate_7cards(p.hole_cards + self.community_cards) for p in active}

        pots = self.pot.build_pots()
        for pot_amount, eligible in pots:
            contenders = [p for p in eligible if not p.folded]
            best = max(scores[p] for p in contenders)
            winners = [p for p in contenders if scores[p] == best]
            share = pot_amount // len(winners)
            for w in winners:
                w.chips += share
                self._emit(f"{w.name} wins {share}")

        self.pot.reset()
        self.reveal_ai = True
        if self.gui:
            self.gui.poker_screen.set_status_text("Showdown")
        self._refresh_ui(to_call=0)

    def end_hand(self):
        # ✅ 여기서 "카드 공개 유지" + "3초 대기"
        if self.gui:
            self.gui.poker_screen.set_actions_enabled(False)
            self.gui.poker_screen.set_status_text("Next hand in 3s…")

        # bust 처리(토너먼트식)
        human = self.players[0]
        if human.chips <= 0:
            self.stop()
            if self.gui:
                self.gui.poker_screen.show_game_over("AI")
            return

        survivors = [human] + [p for p in self.players[1:] if p.chips > 0]
        self.players = survivors

        if len(self.players) == 1:
            self.stop()
            if self.gui:
                self.gui.poker_screen.show_game_over("Human")
            return

        self.dealer_index = (self.dealer_index + 1) % len(self.players)

        # ✅ 딜레이 동안 상태 고정(공개 유지)
        self._schedule_next_hand(delay_ms=3000)

    def _schedule_next_hand(self, delay_ms=3000):
        self._waiting_next_hand = True
        self.stop()

        QTimer.singleShot(int(delay_ms), self._start_next_hand)

    def _start_next_hand(self):
        self._waiting_next_hand = False
        self.runout_mode = False
        self.reveal_ai = False
        self.state = GameState.NEW_HAND
        self.timer.start(250)
