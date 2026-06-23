import customtkinter as ctk
from tkinter import messagebox, filedialog
from tkinter import X, BOTH, LEFT, RIGHT, TOP
from datetime import datetime
from pyswip import Prolog

# Set the appearance mode and default color theme
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")


# Veterinary Triage Expert System (CustomTkinter GUI)


LEVEL_META = {
    'emergency':   {'color': '#E74C3C', 'icon': '\U0001F7E5'},
    'urgent':      {'color': '#E67E22', 'icon': '\U0001F7E7'},
    'non_urgent':  {'color': '#3498DB', 'icon': '\U0001F7E8'},
    'advice':      {'color': '#2ECC71', 'icon': '\U0001F7E6'},
    'observation': {'color': '#95A5A6', 'icon': '❓'},
}

SPECIES_ICONS = {'dog': '\U0001F436', 'cat': '\U0001F431', 'bird': '\U0001F426',
                  'rabbit': '\U0001F430', 'other': '\U0001F43E'}

# Palette: https://coolors.co/palette/7400b8-6930c3-5e60ce-5390d9-4ea8de-48bfe3-56cfe1-64dfdf-72efdd-80ffdb
# Purple -> teal gradient (P1 darkest/most saturated through P10 lightest mint).
# Buttons/accents use the raw palette colors; cards use a light/dark tint of
# the same hue (blended toward white/navy) so dense text stays readable, with
# a matching heading color (deep shade in light mode, the bright hue in dark
# mode) so titles pop against either background.
P1, P2, P3, P4, P5 = "#7400B8", "#6930C3", "#5E60CE", "#5390D9", "#4EA8DE"
P6, P7, P8, P9, P10 = "#48BFE3", "#56CFE1", "#64DFDF", "#72EFDD", "#80FFDB"

INPUT_CARD_COLOR = ("#D9E7F7", "#23364F")        # tint of P4
INPUT_TEXT_COLOR = ("#325682", "#72A4E0")

BREAKDOWN_CARD_COLOR = ("#DCDCF4", "#26294C")    # tint of P3
BREAKDOWN_TEXT_COLOR = ("#383A7C", "#7B7DD7")

EXPLANATION_CARD_COLOR = ("#D7F1F9", "#204352")  # tint of P6
EXPLANATION_TEXT_COLOR = ("#2B7388", "#69CBE8")

HISTORY_CARD_COLOR = ("#DDF8F8", "#284C51")      # tint of P8
HISTORY_TEXT_COLOR = ("#3C8686", "#80E5E5")

NAV_ACTIVE_COLOR = (P4, P7)
NAV_INACTIVE_COLOR = ("#8B86A8", "#6B6480")

# (field name, Prolog predicate, question label, choices)
QUESTIONS = [
    ("species", "species", "1. What is the animal species?", ['dog', 'cat', 'bird', 'rabbit', 'other']),
    ("severity", "symptom_severity", "2. What is the overall symptom severity?", ['mild', 'moderate', 'severe']),
    ("alertness", "alertness", "3. What is the animal's alertness level?", ['active', 'lethargic', 'unconscious']),
    ("appetite", "appetite", "4. How is the animal's appetite?", ['normal', 'slightly_reduced', 'refused']),
    ("breathing", "breathing_difficulty", "5. Is there any breathing difficulty?", ['no', 'mild', 'yes']),
    ("temperature", "temperature", "6. Any fever or low body temperature?", ['normal', 'fever', 'low']),
    ("vomiting", "vomiting", "7. Is the animal vomiting?", ['none', 'occasional', 'persistent']),
    ("pain", "pain_level", "8. What is the animal's pain level?", ['none', 'mild', 'severe']),
    ("hydration", "hydration", "9. Any signs of dehydration?", ['normal', 'dehydrated']),
]

WEIGHT_LABELS = [
    ('Ws', 'Severity'), ('Wa', 'Alertness'), ('Wap', 'Appetite'), ('Wb', 'Breathing'),
    ('Wt', 'Temperature'), ('Wv', 'Vomiting'), ('Wpn', 'Pain'), ('Wh', 'Hydration'),
]


def _decode(value):
    if isinstance(value, bytes):
        try:
            return value.decode('utf-8')
        except Exception:
            return value.decode(errors='ignore')
    return value


def _to_int(value, default=0):
    value = _decode(value)
    try:
        return int(value)
    except Exception:
        pass
    try:
        return int(float(value))
    except Exception:
        return default


def _to_float(value, default=0.0):
    value = _decode(value)
    try:
        return float(value)
    except Exception:
        return default


class TriageApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Veterinary Triage Assistant")
        self.geometry("820x880")
        self.minsize(760, 600)

        self.last_report = None
        self.engine_ready = True
        self.prolog = None

        self._init_prolog()
        self.create_widgets()

        if not self.engine_ready:
            self.diagnose_button.configure(state="disabled")
            self.status_label.configure(
                text="⚠ Prolog engine unavailable - install SWI-Prolog and check rules.pl, then restart.")

    def _init_prolog(self):
        try:
            self.prolog = Prolog()
        except Exception as e:
            self.engine_ready = False
            messagebox.showerror(
                'Prolog Error',
                f'Could not start the Prolog engine: {e}\nEnsure SWI-Prolog is installed and accessible.')
            return

        try:
            self.prolog.consult('rules.pl')
        except Exception as e:
            self.engine_ready = False
            messagebox.showerror(
                'Prolog Error',
                f'Could not load rules.pl: {e}\nEnsure rules.pl is in the same folder as this script.')

    def create_widgets(self):

        # 1. System Title + theme toggle
        top_frame = ctk.CTkFrame(self, fg_color="transparent")
        top_frame.pack(side=TOP, fill=X, padx=20, pady=(15, 10))

        self.species_icon_label = ctk.CTkLabel(top_frame, text=SPECIES_ICONS['dog'],
                                                font=ctk.CTkFont(size=30))
        self.species_icon_label.pack(side=LEFT, padx=(0, 8))

        title_label = ctk.CTkLabel(top_frame,
                                   text="VETERINARY TRIAGE SYSTEM",
                                   font=ctk.CTkFont(size=20, weight="bold"),
                                   text_color=(P3, P7))
        title_label.pack(side=LEFT)

        self.theme_switch = ctk.CTkSwitch(top_frame, text="Dark mode",
                                          command=self.toggle_theme, font=ctk.CTkFont(size=12),
                                          progress_color=P5)
        self.theme_switch.pack(side=RIGHT)

        # Plain text-style nav links (no boxed tab widget) sit right next to
        # the dark mode switch and swap which page is packed below.
        self._nav_font_active = ctk.CTkFont(size=14, weight="bold", underline=True)
        self._nav_font_inactive = ctk.CTkFont(size=14)

        self.nav_details_btn = ctk.CTkButton(top_frame, text="Details", width=80,
                                             command=lambda: self.show_page("details"),
                                             fg_color="transparent", hover_color=("gray85", "gray25"),
                                             text_color=NAV_INACTIVE_COLOR, font=self._nav_font_inactive)
        self.nav_details_btn.pack(side=RIGHT, padx=(0, 16))

        self.nav_diagnosis_btn = ctk.CTkButton(top_frame, text="Diagnosis", width=80,
                                               command=lambda: self.show_page("diagnosis"),
                                               fg_color="transparent", hover_color=("gray85", "gray25"),
                                               text_color=NAV_ACTIVE_COLOR, font=self._nav_font_active)
        self.nav_diagnosis_btn.pack(side=RIGHT, padx=(0, 6))

        self.status_label = ctk.CTkLabel(self, text="", text_color="#E74C3C",
                                         font=ctk.CTkFont(size=12, weight="bold"))
        self.status_label.pack(side=TOP, pady=(0, 5))

        # Two pages: "Diagnosis" holds the inputs and a quick result, "Details"
        # holds the breakdown/explanation/history - swapped via the nav links
        # above instead of a boxed tab widget, so there's no extra background.
        diagnosis_scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        details_scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.pages = {"diagnosis": diagnosis_scroll, "details": details_scroll}
        diagnosis_scroll.pack(fill=BOTH, expand=True, padx=10, pady=(0, 10))

        # Create a main frame to hold all inputs
        input_frame = ctk.CTkFrame(diagnosis_scroll, corner_radius=10, fg_color=INPUT_CARD_COLOR)
        input_frame.pack(fill=X, pady=10, ipady=10)

        for ci in range(1, 8):
            input_frame.columnconfigure(ci, weight=1)
        input_frame.columnconfigure(0, weight=1)

        # --- Helper function for cleaner code ---
        def create_input_row(parent_frame, row_index, label_text, choices, on_change=None):
            label = ctk.CTkLabel(parent_frame, text=label_text, font=ctk.CTkFont(size=14, weight="bold"),
                                 text_color=INPUT_TEXT_COLOR)
            label.grid(row=row_index, column=0, sticky="w", padx=20, pady=12)

            var = ctk.StringVar(value=choices[0])

            def handle_change():
                if on_change:
                    on_change(var.get())

            # Place radio buttons horizontally in the input_frame so columns align across rows.
            for ci, choice in enumerate(choices):
                display = choice.replace('_', ' ')
                rb = ctk.CTkRadioButton(parent_frame, text=display, variable=var, value=choice,
                                        font=ctk.CTkFont(size=12), command=handle_change)
                rb.grid(row=row_index, column=1 + ci, padx=8, pady=6, sticky="w")

            return var

        # 2. Input Rows (built generically from QUESTIONS)
        self.vars = {}
        self._var_defaults = []
        for row_index, (name, _predicate, label_text, choices) in enumerate(QUESTIONS):
            on_change = self._update_species_icon if name == "species" else None
            var = create_input_row(input_frame, row_index, label_text, choices, on_change=on_change)
            self.vars[name] = var
            self._var_defaults.append((var, choices[0]))

        # 3. Action buttons
        button_row = ctk.CTkFrame(diagnosis_scroll, fg_color="transparent")
        button_row.pack(pady=(25, 10))

        self.diagnose_button = ctk.CTkButton(button_row, text="Get Triage Recommendation",
                                             command=self.run_diagnosis,
                                             font=ctk.CTkFont(size=14, weight="bold"),
                                             corner_radius=15,
                                             fg_color=P1,
                                             hover_color=P2,
                                             text_color="white")
        self.diagnose_button.pack(side=LEFT, padx=6, ipady=5)

        self.reset_button = ctk.CTkButton(button_row, text="Reset",
                                          command=self.reset_fields,
                                          font=ctk.CTkFont(size=14),
                                          corner_radius=15,
                                          fg_color=P5,
                                          hover_color=P4,
                                          text_color="white")
        self.reset_button.pack(side=LEFT, padx=6, ipady=5)

        self.save_button = ctk.CTkButton(button_row, text="Save Report",
                                         command=self.save_report,
                                         font=ctk.CTkFont(size=14),
                                         corner_radius=15,
                                         fg_color=P7,
                                         hover_color=P6,
                                         text_color="#10131A")
        self.save_button.pack(side=LEFT, padx=6, ipady=5)

        # 4. Result Display
        result_frame = ctk.CTkFrame(diagnosis_scroll, fg_color="transparent")
        result_frame.pack(pady=10)

        self.icon_label = ctk.CTkLabel(result_frame, text="", font=ctk.CTkFont(size=30))
        self.icon_label.pack(side=LEFT, padx=(0, 10))

        self.result_label = ctk.CTkLabel(result_frame, text="Click the button to analyze condition.",
                                         font=ctk.CTkFont(size=14, slant="italic"),
                                         wraplength=450, justify=LEFT)
        self.result_label.pack(side=LEFT)

        # Score display (progress bar + label)
        self.score_frame = ctk.CTkFrame(diagnosis_scroll, fg_color="transparent")
        self.score_frame.pack(pady=(5, 0))
        self.score_label = ctk.CTkLabel(self.score_frame, text="Score: -", font=ctk.CTkFont(size=12))
        self.score_label.pack(side=LEFT, padx=(0, 10))
        self.score_bar = ctk.CTkProgressBar(self.score_frame, width=300, progress_color=(P4, P7))
        self.score_bar.set(0.0)
        self.score_bar.pack(side=LEFT)

        # Breakdown + Explanation side-by-side (2 columns)
        cards_row = ctk.CTkFrame(details_scroll, fg_color="transparent")
        cards_row.pack(pady=(8, 0), padx=10, fill=X)
        cards_row.columnconfigure(0, weight=1, uniform="cards")
        cards_row.columnconfigure(1, weight=1, uniform="cards")

        self.breakdown_frame = ctk.CTkFrame(cards_row, corner_radius=8, fg_color=BREAKDOWN_CARD_COLOR)
        self.breakdown_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        self.breakdown_title = ctk.CTkLabel(self.breakdown_frame, text="Severity weight breakdown",
                                            font=ctk.CTkFont(size=12, weight="bold"),
                                            text_color=BREAKDOWN_TEXT_COLOR)
        self.breakdown_title.pack(anchor="w", padx=16, pady=(12, 0))
        self.breakdown_text = ctk.CTkLabel(self.breakdown_frame, text="", font=ctk.CTkFont(size=11),
                                           justify=LEFT, wraplength=320)
        self.breakdown_text.pack(anchor="w", padx=16, pady=(6, 12))

        self.explanation_frame = ctk.CTkFrame(cards_row, corner_radius=8, fg_color=EXPLANATION_CARD_COLOR)
        self.explanation_frame.grid(row=0, column=1, sticky="nsew", padx=(5, 0))
        self.explanation_title = ctk.CTkLabel(self.explanation_frame, text="Why this result?",
                                              font=ctk.CTkFont(size=12, weight="bold"),
                                              text_color=EXPLANATION_TEXT_COLOR)
        self.explanation_title.pack(anchor="w", padx=16, pady=(12, 0))
        self.explanation_text = ctk.CTkLabel(self.explanation_frame, text="", font=ctk.CTkFont(size=11),
                                             justify=LEFT, wraplength=320)
        self.explanation_text.pack(anchor="w", padx=16, pady=(6, 12))

        # History card
        self.history_frame = ctk.CTkFrame(details_scroll, corner_radius=8, fg_color=HISTORY_CARD_COLOR)
        self.history_frame.pack(pady=(8, 16), padx=10, fill=X)
        history_header = ctk.CTkFrame(self.history_frame, fg_color="transparent")
        history_header.pack(fill=X, padx=16, pady=(12, 0))
        ctk.CTkLabel(history_header, text="Diagnosis history",
                    font=ctk.CTkFont(size=12, weight="bold"),
                    text_color=HISTORY_TEXT_COLOR).pack(side=LEFT)
        ctk.CTkButton(history_header, text="Clear", width=60, command=self.clear_history,
                     font=ctk.CTkFont(size=11), fg_color=P9, hover_color=P8,
                     text_color="#10131A").pack(side=RIGHT)
        self.history_box = ctk.CTkTextbox(self.history_frame, height=120, font=ctk.CTkFont(size=11))
        self.history_box.pack(padx=16, pady=(6, 12), fill=X)
        self.history_box.configure(state="disabled")

    def show_page(self, name):
        for page in self.pages.values():
            page.pack_forget()
        self.pages[name].pack(fill=BOTH, expand=True, padx=10, pady=(0, 10))

        active_btn = self.nav_diagnosis_btn if name == "diagnosis" else self.nav_details_btn
        inactive_btn = self.nav_details_btn if name == "diagnosis" else self.nav_diagnosis_btn
        active_btn.configure(text_color=NAV_ACTIVE_COLOR, font=self._nav_font_active)
        inactive_btn.configure(text_color=NAV_INACTIVE_COLOR, font=self._nav_font_inactive)

    def _update_species_icon(self, species):
        self.species_icon_label.configure(text=SPECIES_ICONS.get(species, SPECIES_ICONS['other']))

    def toggle_theme(self):
        ctk.set_appearance_mode("Dark" if self.theme_switch.get() else "Light")

    def run_diagnosis(self):
        if not self.engine_ready:
            messagebox.showerror('Prolog Error',
                                 'Prolog engine not available. Ensure rules.pl is loaded.')
            return

        values = {name: var.get() for name, var in self.vars.items()}

        try:
            for _name, predicate, _label, _choices in QUESTIONS:
                list(self.prolog.query(f'retractall({predicate}(_))'))
            for name, predicate, _label, _choices in QUESTIONS:
                self.prolog.assertz(f"{predicate}({values[name]})")
        except Exception as e:
            messagebox.showerror('Prolog Error', f'Could not update facts in Prolog: {e}')
            return

        try:
            solutions = list(self.prolog.query(
                'triage_score(Level, Msg, Score, Percent, Ws, Wa, Wap, Wb, Wt, Wv, Wpn, Wh, Mult)'))
        except Exception as e:
            messagebox.showerror('Prolog Error', f'Error querying Prolog: {e}')
            return

        if not solutions:
            messagebox.showwarning('Triage', 'No triage result returned from Prolog.')
            return

        try:
            sol = solutions[0]
            level = _decode(sol.get('Level'))
            message = _decode(sol.get('Msg'))
            score = _to_int(sol.get('Score'))
            percent = _to_int(sol.get('Percent'))
            weights = {label: _to_int(sol.get(key)) for key, label in WEIGHT_LABELS}
            multiplier = _to_float(sol.get('Mult'), 1.0)

            try:
                expl_sols = list(self.prolog.query('explanation(Factors)'))
                factors = [_decode(f) for f in expl_sols[0]['Factors']] if expl_sols else []
            except Exception:
                factors = []

            self._display_result(level, message, score, percent, weights, multiplier, factors, values)
        except Exception as e:
            messagebox.showerror('Unexpected Error', f'Could not display the triage result: {e}')

    def _display_result(self, level, message, score, percent, weights, multiplier, factors, values):
        meta = LEVEL_META.get(level, {'color': '#BDC3C7', 'icon': '\U0001F4A1'})
        color = meta['color']

        self.icon_label.configure(text=meta['icon'], text_color=color)
        self.result_label.configure(text=message, text_color=color, font=ctk.CTkFont(size=16, weight='bold'))

        self.score_label.configure(text=f"Severity score: {percent}% (raw {score})")
        self.score_bar.set(max(0, min(100, percent)) / 100.0)

        breakdown_lines = "\n".join(f"  - {label} weight: {val}" for label, val in weights.items())
        breakdown_lines += f"\n  - Species multiplier: {multiplier}"
        self.breakdown_text.configure(text=breakdown_lines)

        if factors:
            explanation_lines = "\n".join(f"  • {f}" for f in factors)
        else:
            explanation_lines = "  • No significant risk factors identified"
        self.explanation_text.configure(text=explanation_lines)

        timestamp = datetime.now().strftime('%H:%M:%S')
        history_line = f"[{timestamp}] {level.upper()}: {message} (score {percent}%)\n"
        self.history_box.configure(state="normal")
        self.history_box.insert("end", history_line)
        self.history_box.configure(state="disabled")
        self.history_box.see("end")

        self.last_report = self._build_report_text(level, message, score, percent, weights, multiplier,
                                                    factors, values)

        if level == 'emergency':
            messagebox.showerror('Triage Result', message)
        elif level == 'urgent':
            messagebox.showwarning('Triage Result', message)
        else:
            messagebox.showinfo('Triage Result', message)

    def _build_report_text(self, level, message, score, percent, weights, multiplier, factors, values):
        lines = [
            "VETERINARY TRIAGE REPORT",
            "=" * 40,
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "Inputs:",
        ]
        for name, _predicate, label, _choices in QUESTIONS:
            lines.append(f"  - {label} {values[name]}")
        lines += [
            "",
            f"Result: {level.upper()}",
            f"Message: {message}",
            f"Severity score: {percent}% (raw {score})",
            "",
            "Weight breakdown:",
        ]
        for label, val in weights.items():
            lines.append(f"  - {label}: {val}")
        lines.append(f"  - Species multiplier: {multiplier}")
        lines += ["", "Contributing factors:"]
        if factors:
            lines += [f"  - {f}" for f in factors]
        else:
            lines.append("  - None identified")
        return "\n".join(lines)

    def reset_fields(self):
        for var, default in self._var_defaults:
            var.set(default)
        self._update_species_icon(self.vars['species'].get())
        self.icon_label.configure(text="")
        self.result_label.configure(text="Click the button to analyze condition.",
                                    text_color=("gray10", "gray90"),
                                    font=ctk.CTkFont(size=14, slant="italic"))
        self.score_label.configure(text="Score: -")
        self.score_bar.set(0.0)
        self.breakdown_text.configure(text="")
        self.explanation_text.configure(text="")
        self.last_report = None

    def clear_history(self):
        self.history_box.configure(state="normal")
        self.history_box.delete("1.0", "end")
        self.history_box.configure(state="disabled")

    def save_report(self):
        if not self.last_report:
            messagebox.showwarning('Save Report', 'Run a diagnosis first before saving a report.')
            return
        path = filedialog.asksaveasfilename(defaultextension='.txt',
                                            filetypes=[('Text files', '*.txt')],
                                            initialfile='triage_report.txt')
        if not path:
            return
        try:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(self.last_report)
            messagebox.showinfo('Save Report', f'Report saved to {path}')
        except Exception as e:
            messagebox.showerror('Save Report', f'Could not save report: {e}')


# Main loop setup

if __name__ == "__main__":
    app = TriageApp()
    app.mainloop()
