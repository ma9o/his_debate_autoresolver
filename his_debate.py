#!/usr/bin/env python3

import sys
import random
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, 
    QHBoxLayout, QCheckBox, QSpinBox, QTextEdit, QFormLayout, QComboBox
)
from PyQt5.QtCore import Qt

##################################################
# 1. DEBATERS DICTIONARY
##################################################

DEBATERS = {
    "Protestant": {
        "Luther":   {"rating": 5, "zones": ["German"],  "leading_figure": True},
        "Calvin":   {"rating": 4, "zones": ["French"],  "leading_figure": True},
        "Zwingli":  {"rating": 3, "zones": ["German"],  "leading_figure": False},
        "Bucer":    {"rating": 3, "zones": ["German"],  "leading_figure": False}
        # Add more if desired...
    },
    "Catholic": {
        "Cajetan":  {"rating": 4, "zones": ["German", "Italian"], "leading_figure": True},
        "Eck":      {"rating": 4, "zones": ["German"],            "leading_figure": True},
        "Aleander": {"rating": 3, "zones": ["German", "Italian"], "leading_figure": False},
        "Carafa":   {"rating": 3, "zones": ["Italian"],           "leading_figure": False}
        # Add more if desired...
    }
}

##################################################
# 2. HELPER FUNCTIONS
##################################################

def roll_dice(num_dice: int) -> int:
    """
    Roll 'num_dice' six-sided dice and return the number of hits (rolls of 5 or 6).
    """
    hits = 0
    for _ in range(num_dice):
        die_roll = random.randint(1, 6)
        if die_roll >= 5:
            hits += 1
    return hits

def reroll_hits_based_on_condition(original_dice: int, hits: int, condition: bool) -> int:
    """
    Example re-roll logic (house rule): If 'condition' is True, 
    re-roll 1 die per 2 hits. (E.g., 'Printing Press' or 'Jesuit University' effect).
    """
    if not condition or hits == 0:
        return 0  # No re-rolls if condition is False or if no hits at all

    rerolls_allowed = hits // 2
    additional_hits = 0
    for _ in range(rerolls_allowed):
        die_roll = random.randint(1, 6)
        if die_roll >= 5:
            additional_hits += 1
    return additional_hits

def resolve_debate(
    protestant_rating: int,
    catholic_rating: int,
    protestant_debater: str = "Protestant Debater",
    catholic_debater: str = "Catholic Debater",
    protestant_modifier: int = 0,
    catholic_modifier: int = 0,
    printing_press: bool = False,
    jesuit_university: bool = False,
    adjacency_bonus_protestant: int = 0,
    adjacency_bonus_catholic: int = 0,
    is_protestant_leading_figure: bool = False,
    is_catholic_leading_figure: bool = False,
    burn_threshold: int = 2,
    zero_hits_auto_burn: bool = False,
    flip_threshold: int = 2
) -> dict:
    """
    Resolves a debate between a Protestant and a Catholic debater.
    """
    # 1. Determine dice pools
    protestant_dice = max(0, protestant_rating + protestant_modifier + adjacency_bonus_protestant)
    catholic_dice   = max(0, catholic_rating   + catholic_modifier   + adjacency_bonus_catholic)

    # Optional +1 if printing_press/jesuit_university
    if printing_press:
        protestant_dice += 1
    if jesuit_university:
        catholic_dice += 1

    # 2. Roll dice
    protestant_initial_hits = roll_dice(protestant_dice)
    catholic_initial_hits   = roll_dice(catholic_dice)

    # 3. Re-roll logic (house rule example)
    protestant_reroll_hits = reroll_hits_based_on_condition(
        protestant_dice, protestant_initial_hits, condition=printing_press
    )
    catholic_reroll_hits = reroll_hits_based_on_condition(
        catholic_dice, catholic_initial_hits, condition=jesuit_university
    )

    protestant_hits = protestant_initial_hits + protestant_reroll_hits
    catholic_hits   = catholic_initial_hits   + catholic_reroll_hits

    # 4. Compare hits
    if protestant_hits > catholic_hits:
        winner = "Protestant"
        loser  = "Catholic"
        winning_debater = protestant_debater
        losing_debater  = catholic_debater
        winning_hits    = protestant_hits
        losing_hits     = catholic_hits
        losing_leading_figure = is_catholic_leading_figure
    elif catholic_hits > protestant_hits:
        winner = "Catholic"
        loser  = "Protestant"
        winning_debater = catholic_debater
        losing_debater  = protestant_debater
        winning_hits    = catholic_hits
        losing_hits     = protestant_hits
        losing_leading_figure = is_protestant_leading_figure
    else:
        # Tie
        return {
            "winner": None,
            "loser": None,
            "protestant_hits": protestant_hits,
            "catholic_hits": catholic_hits,
            "burned": False,
            "flips_triggered": False,
            "summary": f"Stand-off (tie): {protestant_debater} and {catholic_debater} are equally matched."
        }

    # 5. Burning & flips
    burn_result = False
    if (winning_hits - losing_hits) >= burn_threshold:
        burn_result = True
    if zero_hits_auto_burn and (losing_hits == 0):
        burn_result = True

    flips_triggered = False
    if (winning_hits - losing_hits) >= flip_threshold:
        flips_triggered = True

    # 6. Summary
    summary_pieces = []
    summary_pieces.append(f"{winning_debater} ({winner}) wins the debate!")
    if burn_result:
        summary_pieces.append(f"{losing_debater} ({loser}) is burned at the stake!")
        if losing_leading_figure:
            summary_pieces.append(f"*** {losing_debater} was a leading figure! Major consequences! ***")
    if flips_triggered:
        summary_pieces.append("Some religious spaces are flipped due to a decisive victory!")

    summary = " ".join(summary_pieces)

    return {
        "winner": winner,
        "loser": loser,
        "winning_debater": winning_debater,
        "losing_debater": losing_debater,
        "protestant_hits": protestant_hits,
        "catholic_hits": catholic_hits,
        "burned": burn_result,
        "flips_triggered": flips_triggered,
        "summary": summary
    }

##################################################
# 3. PYQT GUI
##################################################

from PyQt5.QtWidgets import QLineEdit  # If needed, but we'll mainly use QComboBox here.

class DebateWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Here I Stand - Auto Debate (PyQt, With Language Zones & Debaters)")
        
        form_layout = QFormLayout()

        # --- Language Zone combo ---
        self.language_zone_combo = QComboBox()
        # For demonstration, let's define a few possible zones:
        # You can expand this list as needed.
        zones = ["German", "French", "English", "Italian", "Spanish", "Other"]
        self.language_zone_combo.addItems(zones)
        form_layout.addRow("Debate Language Zone:", self.language_zone_combo)

        # --- Protestant Debater combo ---
        self.protestant_combo = QComboBox()
        # Populate with keys from DEBATERS["Protestant"]
        self.protestant_combo.addItems(DEBATERS["Protestant"].keys())
        form_layout.addRow("Select Protestant Debater:", self.protestant_combo)

        # --- Catholic Debater combo ---
        self.catholic_combo = QComboBox()
        # Populate with keys from DEBATERS["Catholic"]
        self.catholic_combo.addItems(DEBATERS["Catholic"].keys())
        form_layout.addRow("Select Catholic Debater:", self.catholic_combo)

        # --- SpinBoxes / CheckBoxes for modifiers ---
        self.protestant_mod_spin = QSpinBox()
        self.protestant_mod_spin.setRange(-5, 5)
        self.protestant_mod_spin.setValue(0)
        form_layout.addRow("Protestant Modifier:", self.protestant_mod_spin)

        self.catholic_mod_spin = QSpinBox()
        self.catholic_mod_spin.setRange(-5, 5)
        self.catholic_mod_spin.setValue(0)
        form_layout.addRow("Catholic Modifier:", self.catholic_mod_spin)

        self.adj_bonus_prot_spin = QSpinBox()
        self.adj_bonus_prot_spin.setRange(-5, 5)
        self.adj_bonus_prot_spin.setValue(0)
        form_layout.addRow("Prot. Adjacency Bonus:", self.adj_bonus_prot_spin)

        self.adj_bonus_cath_spin = QSpinBox()
        self.adj_bonus_cath_spin.setRange(-5, 5)
        self.adj_bonus_cath_spin.setValue(0)
        form_layout.addRow("Cath. Adjacency Bonus:", self.adj_bonus_cath_spin)

        self.burn_threshold_spin = QSpinBox()
        self.burn_threshold_spin.setRange(1, 5)
        self.burn_threshold_spin.setValue(2)
        form_layout.addRow("Burn Threshold:", self.burn_threshold_spin)

        self.flip_threshold_spin = QSpinBox()
        self.flip_threshold_spin.setRange(1, 5)
        self.flip_threshold_spin.setValue(2)
        form_layout.addRow("Flip Threshold:", self.flip_threshold_spin)

        self.printing_press_check = QCheckBox("Printing Press (Protestant bonus)")
        self.jesuit_uni_check     = QCheckBox("Jesuit University (Catholic bonus)")
        self.zero_hits_check      = QCheckBox("Zero-Hits Auto Burn")

        form_layout.addRow(self.printing_press_check)
        form_layout.addRow(self.jesuit_uni_check)
        form_layout.addRow(self.zero_hits_check)

        # --- Resolve button + results display ---
        self.resolve_button = QPushButton("Resolve Debate")
        self.result_text    = QTextEdit()
        self.result_text.setReadOnly(True)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.resolve_button)

        main_layout = QVBoxLayout()
        main_layout.addLayout(form_layout)
        main_layout.addLayout(button_layout)
        main_layout.addWidget(self.result_text)

        self.setLayout(main_layout)

        # Connect signals
        self.resolve_button.clicked.connect(self.on_resolve_clicked)

    def on_resolve_clicked(self):
        # Gather inputs
        chosen_zone = self.language_zone_combo.currentText()

        selected_protestant = self.protestant_combo.currentText()
        selected_catholic   = self.catholic_combo.currentText()

        # Pull data from the DEBATERS dictionary
        protestant_data = DEBATERS["Protestant"][selected_protestant]
        catholic_data   = DEBATERS["Catholic"][selected_catholic]

        protestant_rating  = protestant_data["rating"]
        catholic_rating    = catholic_data["rating"]

        is_protestant_leading_figure = protestant_data.get("leading_figure", False)
        is_catholic_leading_figure   = catholic_data.get("leading_figure", False)

        # Check if each side can debate in the chosen language zone:
        if chosen_zone not in protestant_data["zones"]:
            self.result_text.setText(
                f"ERROR: {selected_protestant} cannot debate in the {chosen_zone} zone!"
            )
            return

        if chosen_zone not in catholic_data["zones"]:
            self.result_text.setText(
                f"ERROR: {selected_catholic} cannot debate in the {chosen_zone} zone!"
            )
            return

        # Modifiers
        protestant_modifier = self.protestant_mod_spin.value()
        catholic_modifier   = self.catholic_mod_spin.value()

        adjacency_bonus_protestant = self.adj_bonus_prot_spin.value()
        adjacency_bonus_catholic   = self.adj_bonus_cath_spin.value()

        burn_threshold = self.burn_threshold_spin.value()
        flip_threshold = self.flip_threshold_spin.value()

        printing_press       = self.printing_press_check.isChecked()
        jesuit_university    = self.jesuit_uni_check.isChecked()
        zero_hits_auto_burn  = self.zero_hits_check.isChecked()

        # Resolve debate
        result = resolve_debate(
            protestant_rating=protestant_rating,
            catholic_rating=catholic_rating,
            protestant_debater=selected_protestant,
            catholic_debater=selected_catholic,
            protestant_modifier=protestant_modifier,
            catholic_modifier=catholic_modifier,
            printing_press=printing_press,
            jesuit_university=jesuit_university,
            adjacency_bonus_protestant=adjacency_bonus_protestant,
            adjacency_bonus_catholic=adjacency_bonus_catholic,
            is_protestant_leading_figure=is_protestant_leading_figure,
            is_catholic_leading_figure=is_catholic_leading_figure,
            burn_threshold=burn_threshold,
            zero_hits_auto_burn=zero_hits_auto_burn,
            flip_threshold=flip_threshold
        )

        # Display results
        self.result_text.clear()
        self.result_text.append(f"Protestant hits: {result['protestant_hits']} | Catholic hits: {result['catholic_hits']}")
        self.result_text.append(result["summary"])

        if result["burned"]:
            self.result_text.append(
                f"*** {result['losing_debater']} ({result['loser']}) is removed from play! ***"
            )
        if result["flips_triggered"]:
            self.result_text.append("*** Some religious spaces have flipped! ***")


def main():
    app = QApplication(sys.argv)
    window = DebateWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
