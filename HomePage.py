import os

import customtkinter as ctk
from tkinter import BOTH, LEFT, RIGHT, TOP, X
from PIL import Image, ImageDraw, ImageFont

from UI import TriageApp, NAV_ACTIVE_COLOR, NAV_INACTIVE_COLOR, INPUT_CARD_COLOR, P3, P5, P7

# Set the appearance mode and default color theme
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")


# Veterinary Triage Expert System - Home page + shared nav (CustomTkinter GUI)


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PUPPY_IMAGE_PATH = os.path.join(BASE_DIR, "assert", "pups.jpg")


NAV_BAR_COLOR = INPUT_CARD_COLOR  # ("#D9E7F7", dark navy counterpart)

# The headline/subtext/CTA sit directly on top of the photo, so their colors
# are fixed (not light/dark-mode aware) - they need to read against the
# photo's gradient scrim, not against the app's light/dark theme.
OVERLAY_TEXT_COLOR = "#000"
OVERLAY_SUBTEXT_COLOR = "#000"


def _lighten_bottom(img, max_alpha=215, start_at=0.45):
    """Bake a soft white gradient into the bottom of img so dark text drawn
    on top stays readable, without a hard-edged box. A CTkLabel placed as a
    sibling over an image can't blend with it - "transparent" just paints a
    flat rectangle matching the label's own resolved background color - so
    the text and its backdrop both need to be composited into the actual
    pixels instead.
    """
    img = img.convert("RGBA")
    w, h = img.size
    gradient = Image.new("L", (1, h))
    for y in range(h):
        t = max(0.0, (y - h * start_at) / (h * (1 - start_at)))
        gradient.putpixel((0, y), int(max_alpha * t))
    alpha_mask = gradient.resize((w, h))
    panel = Image.new("RGBA", (w, h), (255, 255, 255, 255))
    panel.putalpha(alpha_mask)
    return Image.alpha_composite(img, panel)


def _load_font(size, bold=True):
    fonts_dir = os.path.join(os.environ.get("WINDIR", "C:\\Windows"), "Fonts")
    names = ["seguisb.ttf", "segoeuib.ttf", "arialbd.ttf"] if bold else ["segoeui.ttf", "arial.ttf"]
    for name in names:
        path = os.path.join(fonts_dir, name)
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def _draw_lines(draw, xy, lines, font, fill, line_gap=4):
    x, y = xy
    for line in lines:
        draw.text((x, y), line, font=font, fill=fill)
        bbox = draw.textbbox((x, y), line, font=font)
        y += (bbox[3] - bbox[1]) + line_gap
    return y


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
        top_frame = ctk.CTkFrame(self, corner_radius=10, fg_color=NAV_BAR_COLOR)
        top_frame.pack(side=TOP, fill=X, padx=10, pady=(10, 10), ipady=8)
        top_frame.update_idletasks()
        self._top_bar_height = top_frame.winfo_height()

        title_label = ctk.CTkLabel(top_frame,
                                   text="VETERINARY TRIAGE SYSTEM",
                                   font=ctk.CTkFont(size=20, weight="bold"),
                                   text_color=(P3, P7))
        title_label.pack(side=LEFT, padx=(16, 0))

        self.theme_switch = ctk.CTkSwitch(top_frame, text="Dark mode",
                                          command=self.toggle_theme, font=ctk.CTkFont(size=12),
                                          progress_color=P5)
        self.theme_switch.pack(side=RIGHT, padx=(0, 16))

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
        self._active_page = name
        for page in self.pages.values():
            page.pack_forget()
        if name == "home":
            self.pages[name].pack(fill=BOTH, expand=True)  # edge-to-edge, no margin
        else:
            self.pages[name].pack(fill=BOTH, expand=True, padx=10, pady=(0, 10))

        for key, btn in self.nav_buttons.items():
            active = key == name
            btn.configure(text_color=NAV_ACTIVE_COLOR if active else NAV_INACTIVE_COLOR,
                         font=self._nav_font_active if active else self._nav_font_inactive)

        if name == "home":
            self._refresh_hero()

    def _build_home_page(self):
        # Plain (non-scrolling) frame: the hero image is sized to exactly
        # fill this page, edge-to-edge, so there's nothing to scroll to.
        page = ctk.CTkFrame(self, fg_color="transparent")

        # Fixed-size container so relx/rely placement lines up exactly with
        # the photo underneath. Built empty here and sized/filled by
        # _refresh_hero, since the window's real size isn't known until it's
        # actually been drawn - and needs to be redone on every resize.
        self._hero_container = ctk.CTkFrame(page, fg_color="transparent")
        self._hero_container.pack(fill=BOTH, expand=True)
        self._hero_container.pack_propagate(False)

        self._hero_image_label = ctk.CTkLabel(self._hero_container, text="")
        self._hero_image_label.place(x=0, y=0)

        # # clickable button stays a real widget.
        self._cta_button = ctk.CTkButton(self._hero_container, text="Start Triage   ➔",
                                         command=lambda: self.show_page("diagnosis"),
                                         fg_color="transparent", hover_color="#D9E7F7",
                                         border_width=2, border_color=OVERLAY_TEXT_COLOR,
                                         text_color=OVERLAY_TEXT_COLOR, corner_radius=22,
                                         font=ctk.CTkFont(size=13, weight="bold"),
                                         width=160, height=38)
        
        self._last_hero_size = (0, 0)
        self._resize_job = None
        self.bind("<Configure>", self._on_resize)
        self._refresh_hero()

        return page

    def _on_resize(self, event):
        if event.widget is not self:
            return
        if self._resize_job is not None:
            self.after_cancel(self._resize_job)
        self._resize_job = self.after(200, self._refresh_hero)

    def _refresh_hero(self):
        self._resize_job = None
        if getattr(self, "_active_page", "home") != "home":
            return

        self.update_idletasks()
        avail_w = max(300, self.winfo_width())
        avail_h = max(200, self.winfo_height() - self._top_bar_height)
        if (avail_w, avail_h) == self._last_hero_size:
            return
        self._last_hero_size = (avail_w, avail_h)

        self._hero_image, hero_w, hero_h = self._load_hero_image(avail_w, avail_h)
        self._hero_container.configure(width=hero_w, height=hero_h)
        self._hero_image_label.configure(image=self._hero_image)
        self._cta_button.place(relx=0.07, rely=self._cta_rely, anchor="w")

    def _load_hero_image(self, avail_w, avail_h):
        img = Image.open(PUPPY_IMAGE_PATH)
        w, h = img.size

        # Cover-fit: scale the photo up to the larger of the two ratios, then
        # center-crop the overflow so it fills avail_w x avail_h exactly with
        # no letterbox gaps - a true full-screen background.
        scale = max(avail_w / w, avail_h / h)
        scaled_w = max(1, round(w * scale))
        scaled_h = max(1, round(h * scale))
        resized_full = img.resize((scaled_w, scaled_h), Image.LANCZOS)

        left = (scaled_w - avail_w) // 2
        top = (scaled_h - avail_h) // 2
        resized = resized_full.crop((left, top, left + avail_w, top + avail_h))
        target_w, target_h = avail_w, avail_h
        panelled = _lighten_bottom(resized)

        draw = ImageDraw.Draw(panelled)
        text_x = int(target_w * 0.06)
        y = int(target_h * 0.58)

        headline_font = _load_font(max(18, int(target_h * 0.050)))
        y = _draw_lines(draw, (text_x, y), ["Your Pet's Health,", "Our Priority"],
                        headline_font, fill=OVERLAY_TEXT_COLOR, line_gap=2)

        y += int(target_h * 0.02)
        body_font = _load_font(max(12, int(target_h * 0.020)), bold=False)
        y = _draw_lines(draw, (text_x, y),
                        ["Rule-based triage guidance for your dog, cat, bird",
                         "or rabbit - know how urgent their symptoms are in seconds."],
                        body_font, fill=OVERLAY_SUBTEXT_COLOR, line_gap=2)

        self._cta_rely = min(0.94, (y + target_h * 0.04) / target_h)

        flat = panelled.convert("RGB")
        image = ctk.CTkImage(light_image=flat, dark_image=flat, size=(target_w, target_h))
        return image, target_w, target_h


if __name__ == "__main__":
    app = App()
    app.mainloop()
