import os

import customtkinter as ctk
from tkinter import BOTH, LEFT, RIGHT, TOP, X
from PIL import Image

from UI import TriageApp, NAV_ACTIVE_COLOR, NAV_INACTIVE_COLOR, P3, P5, P7

# Set the appearance mode and default color theme
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")


# Veterinary Triage Expert System - Home page + shared nav (CustomTkinter GUI)


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PUPPY_IMAGE_PATH = os.path.join(BASE_DIR, "assert", "pups.jpg")


# automatically to preserve the crop's aspect ratio.
HERO_CROP_RATIO = 0.6
HERO_WIDTH = 1500

HOME_CARD_COLOR = ("#FBF3E7", "#1B1F2A")
HOME_TEXT_COLOR = ("#1B1B1B", "#F5F5F5")
HOME_SUBTEXT_COLOR = ("gray30", "gray80")


class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Veterinary Triage Assistant")
        self.geometry("820x880")
        self.minsize(760, 600)

        self._nav_font_active = ctk.CTkFont(size=14, weight="bold", underline=True)
        self._nav_font_inactive = ctk.CTkFont(size=14)

        self._build_top_bar()

        self.triage = TriageApp(self)
        home_page = self._build_home_page()

        self.pages = {
            "home": home_page,
            "diagnosis": self.triage.pages["diagnosis"],
            "details": self.triage.pages["details"],
        }
        self.nav_buttons = {
            "home": self.nav_home_btn,
            "diagnosis": self.nav_diagnosis_btn,
            "details": self.nav_details_btn,
        }

        self.show_page("home")

    def _build_top_bar(self):
        top_frame = ctk.CTkFrame(self, fg_color="transparent")
        top_frame.pack(side=TOP, fill=X, padx=20, pady=(15, 10))

        title_label = ctk.CTkLabel(top_frame,
                                   text="VETERINARY TRIAGE SYSTEM",
                                   font=ctk.CTkFont(size=20, weight="bold"),
                                   text_color=(P3, P7))
        title_label.pack(side=LEFT)

        self.theme_switch = ctk.CTkSwitch(top_frame, text="Dark mode",
                                          command=self.toggle_theme, font=ctk.CTkFont(size=12),
                                          progress_color=P5)
        self.theme_switch.pack(side=RIGHT)

        # Plain text-style nav links (no boxed tab widget) live next to the
        # dark mode switch and swap which page is packed below.
        self.nav_details_btn = ctk.CTkButton(top_frame, text="Details", width=80,
                                             command=lambda: self.show_page("details"),
                                             fg_color="transparent", hover_color=("gray85", "gray25"),
                                             text_color=NAV_INACTIVE_COLOR, font=self._nav_font_inactive)
        self.nav_details_btn.pack(side=RIGHT, padx=(0, 16))

        self.nav_diagnosis_btn = ctk.CTkButton(top_frame, text="Diagnosis", width=80,
                                               command=lambda: self.show_page("diagnosis"),
                                               fg_color="transparent", hover_color=("gray85", "gray25"),
                                               text_color=NAV_INACTIVE_COLOR, font=self._nav_font_inactive)
        self.nav_diagnosis_btn.pack(side=RIGHT, padx=(0, 6))

        self.nav_home_btn = ctk.CTkButton(top_frame, text="Home", width=80,
                                          command=lambda: self.show_page("home"),
                                          fg_color="transparent", hover_color=("gray85", "gray25"),
                                          text_color=NAV_ACTIVE_COLOR, font=self._nav_font_active)
        self.nav_home_btn.pack(side=RIGHT, padx=(0, 6))

    def toggle_theme(self):
        ctk.set_appearance_mode("Dark" if self.theme_switch.get() else "Light")

    def show_page(self, name):
        for page in self.pages.values():
            page.pack_forget()
        self.pages[name].pack(fill=BOTH, expand=True, padx=10, pady=(0, 10))

        for key, btn in self.nav_buttons.items():
            active = key == name
            btn.configure(text_color=NAV_ACTIVE_COLOR if active else NAV_INACTIVE_COLOR,
                         font=self._nav_font_active if active else self._nav_font_inactive)

    def _build_home_page(self):
        page = ctk.CTkScrollableFrame(self, fg_color="transparent")

        self._hero_image = self._load_hero_image()
        image_label = ctk.CTkLabel(page, image=self._hero_image, text="")
        image_label.pack(fill=X)

        text_card = ctk.CTkFrame(page, corner_radius=0, fg_color=HOME_CARD_COLOR)
        text_card.pack(fill=X)

        ctk.CTkLabel(text_card, text="Your Pet's Health,\nOur Priority", justify=LEFT,
                    font=ctk.CTkFont(size=30, weight="bold"),
                    text_color=HOME_TEXT_COLOR).pack(anchor="w", padx=30, pady=(30, 10))

        ctk.CTkLabel(text_card,
                    text=("Quick, rule-based triage guidance for your dog, cat, bird\n"
                          "or rabbit - know how urgent their symptoms are in seconds."),
                    justify=LEFT, font=ctk.CTkFont(size=13),
                    text_color=HOME_SUBTEXT_COLOR).pack(anchor="w", padx=30, pady=(0, 20))

        ctk.CTkButton(text_card, text="Start Triage   ➔",
                     command=lambda: self.show_page("diagnosis"),
                     fg_color="transparent", hover_color=("#E9DDCA", "#2A2A2A"),
                     border_width=2, border_color=HOME_TEXT_COLOR,
                     text_color=HOME_TEXT_COLOR, corner_radius=22,
                     font=ctk.CTkFont(size=14, weight="bold"),
                     width=170, height=42).pack(anchor="w", padx=30, pady=(0, 30))

        return page

    def _load_hero_image(self):
        img = Image.open(PUPPY_IMAGE_PATH)
        w, h = img.size
        crop_h = int(h * HERO_CROP_RATIO)
        top = h - crop_h  # keep the bottom crop_h rows, cropping away the top
        cropped = img.crop((0, top, w, h))
        target_h = round(HERO_WIDTH * crop_h / w)
        return ctk.CTkImage(light_image=cropped, dark_image=cropped, size=(HERO_WIDTH, target_h))


if __name__ == "__main__":
    app = App()
    app.mainloop()
