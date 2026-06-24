import os
import customtkinter as ctk
from PIL import Image, ImageDraw, ImageFont

# Assuming UI.py has these exact exports
from UI import TriageApp, NAV_ACTIVE_COLOR, NAV_INACTIVE_COLOR, INPUT_CARD_COLOR, P3, P5, P7

# Set the appearance mode and default color theme
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PUPPY_IMAGE_PATH = os.path.join(BASE_DIR, "assert", "pups.jpg")

# --- Helper Image Processing Functions ---

def apply_gradient(img, max_alpha=215, start_at=0.45):
    """Bakes a soft white gradient at the bottom so overlaid text is readable."""
    img = img.convert("RGBA")
    w, h = img.size
    gradient = Image.new("L", (1, h))
    for y in range(h):
        t = max(0.0, (y - h * start_at) / (h * (1 - start_at)))
        gradient.putpixel((0, y), int(max_alpha * t))
        
    alpha_mask = gradient.resize((w, h))
    panel = Image.new("RGBA", (w, h), (255, 255, 255, 255))
    panel.putalpha(alpha_mask)
    return Image.alpha_composite(img, panel).convert("RGB")

def crop_center(img, target_w, target_h):
    """Cover-fits the image to fill the given dimensions without distortion."""
    w, h = img.size
    scale = max(target_w / w, target_h / h)
    new_w, new_h = max(1, int(w * scale)), max(1, int(h * scale))
    img = img.resize((new_w, new_h), Image.LANCZOS)
    
    left, top = (new_w - target_w) // 2, (new_h - target_h) // 2
    return img.crop((left, top, left + target_w, top + target_h))

def get_font(size, bold=False):
    """Loads a system font dynamically for PIL drawing."""
    fonts_dir = os.path.join(os.environ.get("WINDIR", "C:\\Windows"), "Fonts")
    names = ["seguisb.ttf", "segoeuib.ttf", "arialbd.ttf"] if bold else ["segoeui.ttf", "arial.ttf"]
    for name in names:
        path = os.path.join(fonts_dir, name)
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


# --- Main Application ---

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Veterinary Triage Assistant")
        self.geometry("820x880")
        self.minsize(760, 600)

        # State Variables
        self.active_page = "home"
        self.last_hero_size = (0, 0)
        self._resize_job = None
        
        try:
            self.original_img = Image.open(PUPPY_IMAGE_PATH)
        except Exception:
            self.original_img = Image.new("RGB", (800, 600), "white") # Fallback if image is missing

        # Layout Setup
        self.setup_navbar()

        # Pages Dictionary
        # All three pages are siblings packed directly into self (the root
        # window) by show_page(), and only the active one is ever packed -
        # there's no shared wrapper frame here, since a permanently-packed
        # wrapper would otherwise keep reserving its layout space even while
        # a different page is showing.
        self.triage = TriageApp(self)
        self.pages = {
            "home": self.create_home_page(),
            "diagnosis": self.triage.pages["diagnosis"],
            "details": self.triage.pages["details"],
        }

        self.show_page("home")
        self.bind("<Configure>", self.on_resize)

    def setup_navbar(self):
        """Builds the top navigation bar."""
        nav_bar = ctk.CTkFrame(self, corner_radius=10, fg_color=INPUT_CARD_COLOR)
        nav_bar.pack(side="top", fill="x", padx=10, pady=(10, 10), ipady=8)

        # Title
        ctk.CTkLabel(nav_bar, text="VETERINARY TRIAGE SYSTEM",
                     font=ctk.CTkFont(size=20, weight="bold"),
                     text_color=(P3, P7)).pack(side="left", padx=16)

        # Theme Switch
        self.theme_switch = ctk.CTkSwitch(nav_bar, text="Dark mode", command=self.toggle_theme,
                                          font=ctk.CTkFont(size=12), progress_color=P5)
        self.theme_switch.pack(side="right", padx=16)

        # Navigation Links
        self.nav_btns = {}
        nav_items = ["Details", "Diagnosis", "Home"]  # Packed right-to-left
        for name in nav_items:
            key = name.lower()
            btn = ctk.CTkButton(nav_bar, text=name, width=80, fg_color="transparent",
                                hover_color=("gray85", "gray25"),
                                command=lambda k=key: self.show_page(k))
            btn.pack(side="right", padx=6)
            self.nav_btns[key] = btn

    def create_home_page(self):
        """Builds the home page layout."""
        page = ctk.CTkFrame(self, fg_color="transparent")

        # 1. Background Image Label
        self.hero_bg = ctk.CTkLabel(page, text="")
        self.hero_bg.place(relx=0, rely=0, relwidth=1, relheight=1)

        # 2. Action Button
        self.cta_button = ctk.CTkButton(
            page,
            text="Start Triage  ➔",
            width=160, 
            height=38,
            command=lambda: self.show_page("diagnosis"), 
            fg_color="white",
            bg_color="transparent",
            hover_color="#D9E7F7", 
            border_width=2, 
            border_color="#000",
            text_color="#000", 
            corner_radius=22,
            font=ctk.CTkFont(size=13, weight="bold")
        )

        return page

    def toggle_theme(self):
        ctk.set_appearance_mode("Dark" if self.theme_switch.get() else "Light")

    def show_page(self, name):
        self.active_page = name
        
        # Display selected page, hide others
        for key, page in self.pages.items():
            if key == name:
                padx, pady = (0, 0) if name == "home" else (10, (0, 10))
                page.pack(fill="both", expand=True, padx=padx, pady=pady)
            else:
                page.pack_forget()

        # Update Navigation styling
        active_font = ctk.CTkFont(size=14, weight="bold", underline=True)
        inactive_font = ctk.CTkFont(size=14)

        for key, btn in self.nav_btns.items():
            is_active = (key == name)
            btn.configure(text_color=NAV_ACTIVE_COLOR if is_active else NAV_INACTIVE_COLOR,
                          font=active_font if is_active else inactive_font)

        if name == "home":
            self.update_hero_image()

    def on_resize(self, event):
        """Debounce resize events so we don't recalculate images constantly."""
        if event.widget is not self:
            return
        if self._resize_job is not None:
            self.after_cancel(self._resize_job)
        self._resize_job = self.after(100, self.update_hero_image)

    def update_hero_image(self):
        """Recalculates the image, bakes the text on it, and adjusts the button."""
        self._resize_job = None
        if self.active_page != "home":
            return

        self.update_idletasks()
        w, h = self.pages["home"].winfo_width(), self.pages["home"].winfo_height()
        
        if w <= 1 or h <= 1 or (w, h) == self.last_hero_size:
            return
            
        self.last_hero_size = (w, h)

        # 1. Format the Background
        cropped = crop_center(self.original_img, w, h)
        gradient_img = apply_gradient(cropped)
        
        # 2. Bake the text directly into the image pixels
        draw = ImageDraw.Draw(gradient_img)
        title_font = get_font(36, bold=True)
        body_font = get_font(14, bold=False)
        
        text_x = int(w * 0.15)
        text_y = int(h * 0.62) # Start position
        
        # Draw Title
        title_text = "Your Pet's Health,\nOur Priority"
        draw.text((text_x, text_y), title_text, font=title_font, fill=(0, 0, 0))
        
        # Find Y position for Subtext
        if hasattr(draw, "multiline_textbbox"):
            bbox = draw.multiline_textbbox((text_x, text_y), title_text, font=title_font)
            text_y = bbox[3] + 15
        else:
            text_y += 90 
            
        # Draw Subtext
        subtext = "Rule-based triage guidance for your dog, cat, bird\nor rabbit - know how urgent their symptoms are in seconds."
        draw.text((text_x, text_y), subtext, font=body_font, fill=(0, 0, 0))
        
        # Find Y position for Button
        if hasattr(draw, "multiline_textbbox"):
            subtext_bbox = draw.multiline_textbbox((text_x, text_y), subtext, font=body_font)
            button_y = subtext_bbox[3] + 25
        else:
            button_y = text_y + 45
        
        # 3. Apply the final drawn image to the UI
        ctk_img = ctk.CTkImage(light_image=gradient_img, dark_image=gradient_img, size=(w, h))
        self.hero_bg.configure(image=ctk_img)

        # 4. Place the CTA button underneath the drawn text
        self.cta_button.place(x=text_x, y=button_y)
        self.cta_button.lift()  # CTkLabel redraws its own canvas on configure()
                                 # above, which can otherwise cover this sibling

if __name__ == "__main__":
    app = App()
    app.mainloop()