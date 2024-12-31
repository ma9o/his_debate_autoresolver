import sys
import random
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QCheckBox, QSpinBox, QPushButton, QTextEdit, QComboBox,
    QTableWidget, QTableWidgetItem, QAbstractItemView, QHeaderView, QSizePolicy
)
from PyQt6.QtCore import Qt

from debaters import CATHOLIC, ENGLISH, FRENCH, GERMAN, debaters

class DebateResolverWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Here I Stand - Auto-Resolve Debates")
        self.resize(900, 600)

        # Top-level container
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout()
        main_widget.setLayout(main_layout)

        # ---------------------------------------
        # 1) Language Zone Selection
        # ---------------------------------------
        self.language_combo = QComboBox()
        self.language_combo.addItems(["All", GERMAN, ENGLISH, CATHOLIC, FRENCH])
        self.language_combo.currentIndexChanged.connect(self.filter_debaters_table)

        # If you want to consider the game "turn" in filtering:
        self.current_turn_spin = QSpinBox()
        self.current_turn_spin.setRange(0, 50)
        self.current_turn_spin.setValue(1)
        self.current_turn_spin.valueChanged.connect(self.filter_debaters_table)

        # Layout for top controls
        top_controls_layout = QHBoxLayout()
        top_controls_layout.addWidget(QLabel("Select Language Zone:"))
        top_controls_layout.addWidget(self.language_combo)
        top_controls_layout.addWidget(QLabel("Current Turn:"))
        top_controls_layout.addWidget(self.current_turn_spin)
        main_layout.addLayout(top_controls_layout)

        self.reset_committed_btn = QPushButton("Reset All Committed")
        self.reset_committed_btn.clicked.connect(self.reset_all_committed)
        main_layout.addWidget(self.reset_committed_btn)


        # ---------------------------------------
        # 2) Debaters Table
        # ---------------------------------------
        self.debaters_table = QTableWidget()
        self.debaters_table.setColumnCount(7)
        self.debaters_table.setHorizontalHeaderLabels(
            ["Name", "Language", "Turn", "Value", "Optional?", "Use Optional?", "Available"]
        )
        self.debaters_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.debaters_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.debaters_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        # Set table to expand
        self.debaters_table.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        main_layout.addWidget(self.debaters_table, stretch=1)

        # Populate once, then filter in place
        self.populate_debaters_table()
        self.filter_debaters_table()

        # ---------------------------------------
        # 3) Random Selection & Checkboxes (Events)
        # ---------------------------------------
        self.select_attacker_protestant = QPushButton("Select Protestant as Attacker")
        self.select_attacker_papal = QPushButton("Select Papal as Attacker")

        self.select_attacker_protestant.clicked.connect(lambda: self.select_attacker(True))
        self.select_attacker_papal.clicked.connect(lambda: self.select_attacker(False))

        random_select_layout = QHBoxLayout()
        random_select_layout.addWidget(self.select_attacker_protestant)
        random_select_layout.addWidget(self.select_attacker_papal)
        main_layout.addLayout(random_select_layout)

        # Event checkboxes
        self.augsburg_cb = QCheckBox("Augsburg Confession (Papal -1 die)")
        self.mary_cb = QCheckBox("Mary I Ruler (Double Papal Value in English zone)")
        self.thomas_more_cb = QCheckBox("Thomas More event (+1 Papal die)")
        self.papal_inq_cb = QCheckBox("Papal Inquisition (+1 Papal die)")
        self.eck_gardiner_bonus_cb = QCheckBox("Eck/Gardiner bonus (+1 Papal die)")

        event_layout = QHBoxLayout()
        event_layout.addWidget(self.augsburg_cb)
        event_layout.addWidget(self.mary_cb)
        event_layout.addWidget(self.thomas_more_cb)
        event_layout.addWidget(self.papal_inq_cb)
        event_layout.addWidget(self.eck_gardiner_bonus_cb)

        main_layout.addLayout(event_layout)

        # ---------------------------------------
        # 4) Spin Boxes for Extra Dice
        # ---------------------------------------
        spin_layout = QHBoxLayout()
        self.protestant_bonus_spin = QSpinBox()
        self.papal_bonus_spin = QSpinBox()
        self.protestant_bonus_spin.setRange(0, 10)
        self.papal_bonus_spin.setRange(0, 10)
        spin_layout.addWidget(QLabel("Protestant Bonus Dice"))
        spin_layout.addWidget(self.protestant_bonus_spin)
        spin_layout.addWidget(QLabel("Papal Bonus Dice"))
        spin_layout.addWidget(self.papal_bonus_spin)
        main_layout.addLayout(spin_layout)

        # ---------------------------------------
        # 5) Resolve Button & Output
        # ---------------------------------------
        self.resolve_button = QPushButton("Resolve Debate")
        self.resolve_button.clicked.connect(self.resolve_debate)
        main_layout.addWidget(self.resolve_button)

        self.output_box = QTextEdit()
        self.output_box.setReadOnly(True)
        # Make output box smaller relative to table
        self.output_box.setMaximumHeight(150)
        main_layout.addWidget(self.output_box)

        # Keep track of the currently chosen debaters
        self.selected_protestant_debater = None
        self.selected_papal_debater = None

        # Add a new instance variable to track who is attacking
        self.is_protestant_attacking = None

    # -------------------------------------------------------------------------
    # Populate the table with all debaters
    # -------------------------------------------------------------------------
    def populate_debaters_table(self):
        """
        Put all debaters in the QTableWidget. 
        We'll store them row-by-row, but won't filter yet.
        """
        self.debaters_table.setRowCount(len(debaters))
        # Update column count and headers to add Committed
        self.debaters_table.setColumnCount(6)
        self.debaters_table.setHorizontalHeaderLabels(
            ["Name", "Language", "Turn", "Value", "Available", "Committed"]
        )

        for row, d in enumerate(debaters):
            # Name
            item_name = QTableWidgetItem(d.name)
            # Language
            item_language = QTableWidgetItem(d.language_zone)
            # Turn
            item_turn = QTableWidgetItem(str(d.turn))
            # Value
            item_value = QTableWidgetItem(str(d.debate_value))

            # Available checkbox - set initially unavailable if optional
            available_checkbox = QCheckBox()
            available_checkbox.setChecked(not d.optional)  # False if optional, True otherwise

            # Add Committed checkbox
            committed_checkbox = QCheckBox()
            committed_checkbox.setChecked(False)  # Initially not committed

            # Place items in row
            self.debaters_table.setItem(row, 0, item_name)
            self.debaters_table.setItem(row, 1, item_language)
            self.debaters_table.setItem(row, 2, item_turn)
            self.debaters_table.setItem(row, 3, item_value)
            self.debaters_table.setCellWidget(row, 4, available_checkbox)
            self.debaters_table.setCellWidget(row, 5, committed_checkbox)

        self.debaters_table.resizeRowsToContents()

    # -------------------------------------------------------------------------
    # Filter the table based on language zone and turn
    # -------------------------------------------------------------------------
    def filter_debaters_table(self):
        selected_zone = self.language_combo.currentText()
        current_turn = self.current_turn_spin.value()

        for row in range(self.debaters_table.rowCount()):
            name_item = self.debaters_table.item(row, 0)
            turn_item = self.debaters_table.item(row, 2)
            value_item = self.debaters_table.item(row, 3)

            if not name_item or not turn_item or not value_item:
                self.debaters_table.setRowHidden(row, True)
                continue

            d_name = name_item.text()
            d_turn = int(turn_item.text())

            # Find the matching Debater from your list 
            debater_obj = next((db for db in debaters if db.name == d_name), None)
            if not debater_obj:
                self.debaters_table.setRowHidden(row, True)
                continue

            # Check turn and language
            turn_ok = (d_turn <= current_turn)
            # Always show Catholic (papal) debaters, otherwise check zone
            zone_ok = (
                debater_obj.language_zone == CATHOLIC or  # Always show papal debaters
                selected_zone == "All" or
                debater_obj.language_zone == selected_zone
            )

            # If both are true, show row; else hide row
            self.debaters_table.setRowHidden(row, not (turn_ok and zone_ok))

    # -------------------------------------------------------------------------
    # Randomly pick a debater from the filtered rows
    # -------------------------------------------------------------------------
    def select_random_debater(self, is_protestant):
        """
        Select a random debater based on type.
        Args:
            is_protestant (bool): True to select Protestant, False to select Papal
        """
        valid_rows = []
        for row in range(self.debaters_table.rowCount()):
            if self.debaters_table.isRowHidden(row):
                continue
            
            name_item = self.debaters_table.item(row, 0)
            if not name_item:
                continue
            
            # Check if debater is available
            available_checkbox = self.debaters_table.cellWidget(row, 4)  # Updated index
            if not available_checkbox.isChecked():
                continue
            
            d_name = name_item.text()
            debater_obj = next((db for db in debaters if db.name == d_name), None)
            if not debater_obj:
                continue
            
            # Check if debater matches requested type
            is_debater_protestant = (debater_obj.language_zone != CATHOLIC)
            if is_debater_protestant == is_protestant:
                valid_rows.append(row)

        if not valid_rows:
            self.output_box.append(f"No valid {'Protestant' if is_protestant else 'Papal'} debater found!")
            return

        chosen_row = random.choice(valid_rows)
        chosen_name = self.debaters_table.item(chosen_row, 0).text()
        chosen_debater = next((db for db in debaters if db.name == chosen_name), None)

        if is_protestant:
            self.selected_protestant_debater = chosen_debater
        else:
            self.selected_papal_debater = chosen_debater

        self.output_box.append(f"Selected {'Protestant' if is_protestant else 'Papal'} Debater: {chosen_debater.name} ({chosen_debater.debate_value})")

    def select_attacker(self, is_protestant_attacker):
        """
        Select an attacker and automatically select a defender of the opposite side.
        Args:
            is_protestant_attacker (bool): True if Protestant is attacking, False if Papal is attacking
        """
        # Store who is attacking
        self.is_protestant_attacking = is_protestant_attacker
        
        # First select the attacker (must be uncommitted)
        valid_rows = []
        for row in range(self.debaters_table.rowCount()):
            if self.debaters_table.isRowHidden(row):
                continue
            
            name_item = self.debaters_table.item(row, 0)
            if not name_item:
                continue
            
            # Check if debater is available and uncommitted
            available_checkbox = self.debaters_table.cellWidget(row, 4)
            committed_checkbox = self.debaters_table.cellWidget(row, 5)
            if not available_checkbox.isChecked() or committed_checkbox.isChecked():
                continue
            
            d_name = name_item.text()
            debater_obj = next((db for db in debaters if db.name == d_name), None)
            if not debater_obj:
                continue
            
            # Check if debater matches requested attacker type
            is_debater_protestant = (debater_obj.language_zone != CATHOLIC)
            if is_debater_protestant == is_protestant_attacker:
                valid_rows.append(row)

        if not valid_rows:
            self.output_box.append(f"No valid uncommitted {'Protestant' if is_protestant_attacker else 'Papal'} attacker found!")
            return

        # Select attacker
        chosen_row = random.choice(valid_rows)
        chosen_name = self.debaters_table.item(chosen_row, 0).text()
        chosen_debater = next((db for db in debaters if db.name == chosen_name), None)

        # Store the selected debater and note they are attacker
        if is_protestant_attacker:
            self.selected_protestant_debater = chosen_debater
            self.output_box.append(f"Selected Protestant Attacker: {chosen_debater.name} ({chosen_debater.debate_value})")
            # Now select a Papal defender
            self.select_random_debater(False)
        else:
            self.selected_papal_debater = chosen_debater
            self.output_box.append(f"Selected Papal Attacker: {chosen_debater.name} ({chosen_debater.debate_value})")
            # Now select a Protestant defender
            self.select_random_debater(True)

    # -------------------------------------------------------------------------
    # Resolve the debate with the chosen Protestant/Papal debaters
    # -------------------------------------------------------------------------
    def resolve_debate(self):
        self.output_box.append("=== Resolving Debate ===")

        if not self.selected_protestant_debater or not self.selected_papal_debater:
            self.output_box.append("Please select BOTH a Protestant and Papal debater first!")
            return

        if self.is_protestant_attacking is None:
            self.output_box.append("Please select an attacker first!")
            return

        # --------------------------------------------------------
        # 1) Base Dice - Using stored attacker status
        # --------------------------------------------------------
        protestant_dice = self.selected_protestant_debater.debate_value
        papal_dice = self.selected_papal_debater.debate_value

        if self.is_protestant_attacking:
            protestant_dice += 3  # Attacker bonus
            # Check committed status of the PAPAL debater (defender)
            committed_checkbox = None
            for row in range(self.debaters_table.rowCount()):
                name_item = self.debaters_table.item(row, 0)
                if name_item and name_item.text() == self.selected_papal_debater.name:
                    committed_checkbox = self.debaters_table.cellWidget(row, 5)
                    break
            
            defender_bonus = 1 if committed_checkbox and committed_checkbox.isChecked() else 2
            papal_dice += defender_bonus  # Defender bonus
            self.output_box.append("Protestant is attacking (+3 dice)")
            self.output_box.append(f"Papal is defending (+{defender_bonus} dice)")
        else:
            papal_dice += 3  # Attacker bonus
            # Check committed status of the PROTESTANT debater (defender)
            committed_checkbox = None
            for row in range(self.debaters_table.rowCount()):
                name_item = self.debaters_table.item(row, 0)
                if name_item and name_item.text() == self.selected_protestant_debater.name:
                    committed_checkbox = self.debaters_table.cellWidget(row, 5)
                    break
            
            defender_bonus = 1 if committed_checkbox and committed_checkbox.isChecked() else 2
            protestant_dice += defender_bonus  # Defender bonus
            self.output_box.append("Papal is attacking (+3 dice)")
            self.output_box.append(f"Protestant is defending (+{defender_bonus} dice)")

        # --------------------------------------------------------
        # 2) Apply event checkboxes 
        # (Mary I, Augsburg, Thomas More, etc.)
        # --------------------------------------------------------
        if self.augsburg_cb.isChecked():
            papal_dice -= 1
            self.output_box.append("Augsburg Confession => Papal -1 die.")

        # Check language zone for “Mary I is English Ruler => double Papal value if in English zone”
        if self.mary_cb.isChecked():
            # If the debate is actually in English zone 
            # (You might check the *space* of the debate rather than the debater.)
            if self.selected_protestant_debater.language_zone == ENGLISH:
                # Double the PAPAL DEBATER VALUE portion
                papal_dice += self.selected_papal_debater.debate_value
                self.output_box.append("Mary I => Doubling Papal debater's value in English zone.")

        # Thomas More / Papal Inquisition => extra papal dice
        extra_papal = 0
        if self.thomas_more_cb.isChecked():
            extra_papal += 1
        if self.papal_inq_cb.isChecked():
            extra_papal += 1
        if extra_papal > 0:
            papal_dice += extra_papal
            self.output_box.append(f"Thomas More/Papal Inquisition => +{extra_papal} Papal dice.")

        # Eck/Gardiner => +1 papal if specifically that name
        if self.eck_gardiner_bonus_cb.isChecked():
            if self.selected_papal_debater.name in ["Eck", "Gardiner"]:
                papal_dice += 1
                self.output_box.append("Eck/Gardiner bonus => +1 Papal die.")

        # --------------------------------------------------------
        # 3) Apply spin-box bonus dice
        # --------------------------------------------------------
        protestant_dice += self.protestant_bonus_spin.value()
        papal_dice += self.papal_bonus_spin.value()

        # Each side must roll at least 1 die
        protestant_dice = max(1, protestant_dice)
        papal_dice = max(1, papal_dice)

        # --------------------------------------------------------
        # 4) Roll dice & count hits (5 or 6 = hit)
        # --------------------------------------------------------
        protestant_rolls = [random.randint(1, 6) for _ in range(protestant_dice)]
        papal_rolls = [random.randint(1, 6) for _ in range(papal_dice)]
        protestant_hits = sum(1 for x in protestant_rolls if x >= 5)
        papal_hits = sum(1 for x in papal_rolls if x >= 5)

        self.output_box.append(f"Protestant dice ({protestant_dice}): {protestant_rolls} => {protestant_hits} hits")
        self.output_box.append(f"Papal dice ({papal_dice}): {papal_rolls} => {papal_hits} hits")

        # --------------------------------------------------------
        # 5) Determine winner & apply new burning/disgrace rules:
        #    "If margin > losingDebaterValue => burned / disgraced
        #     else => no effect"
        # --------------------------------------------------------
        if protestant_hits > papal_hits:
            margin = protestant_hits - papal_hits
            self.output_box.append(f"Protestant wins by {margin}")
            losing_value = self.selected_papal_debater.debate_value

            if margin > losing_value:
                self.output_box.append("Papal debater is DISGRACED!")
                # Make the papal debater unavailable
                self.set_debater_availability(self.selected_papal_debater.name, False)
            else:
                self.output_box.append("No effect on Papal debater.")

            # Spaces converted could be the margin, or some other formula:
            self.output_box.append(f"{margin} space(s) converted to Protestant.")

        elif papal_hits > protestant_hits:
            margin = papal_hits - protestant_hits
            self.output_box.append(f"Papal wins by {margin}")
            losing_value = self.selected_protestant_debater.debate_value

            if margin > losing_value:
                self.output_box.append("Protestant debater is BURNED at the stake!")
                # Make the protestant debater unavailable
                self.set_debater_availability(self.selected_protestant_debater.name, False)
            else:
                self.output_box.append("No effect on Protestant debater.")

            self.output_box.append(f"{margin} space(s) converted to Catholic.")

        else:
            self.output_box.append("Tie! (Possible second round or no effect)")

        # --------------------------------------------------------
        # 6) Mark them as committed in your actual data if needed
        #    (not implemented here—just mention it)
        # --------------------------------------------------------

        # --------------------------------------------------------
        # 7) **Only clear the spin boxes**. We do NOT clear the checkboxes.
        # --------------------------------------------------------
        self.protestant_bonus_spin.setValue(0)
        self.papal_bonus_spin.setValue(0)

        # After determining the winner, mark both debaters as committed
        # Find and update the committed checkboxes for both debaters
        for row in range(self.debaters_table.rowCount()):
            name_item = self.debaters_table.item(row, 0)
            if name_item:
                if name_item.text() in [self.selected_protestant_debater.name, self.selected_papal_debater.name]:
                    committed_checkbox = self.debaters_table.cellWidget(row, 5)
                    if committed_checkbox:
                        committed_checkbox.setChecked(True)

        self.output_box.append("--- Debate Resolution Complete ---\n")

    def reset_all_committed(self):
        """Reset all committed checkboxes to False"""
        for row in range(self.debaters_table.rowCount()):
            committed_checkbox = self.debaters_table.cellWidget(row, 5)
            if committed_checkbox:
                committed_checkbox.setChecked(False)
        self.output_box.append("Reset all debaters' committed status.")

    def set_debater_availability(self, debater_name, available):
        """Set a debater's availability checkbox based on their name"""
        for row in range(self.debaters_table.rowCount()):
            name_item = self.debaters_table.item(row, 0)
            if name_item and name_item.text() == debater_name:
                available_checkbox = self.debaters_table.cellWidget(row, 4)
                if available_checkbox:
                    available_checkbox.setChecked(available)
                    break

def main():
    app = QApplication(sys.argv)
    window = DebateResolverWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
