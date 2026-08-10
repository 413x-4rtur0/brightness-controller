#!/usr/bin/python3
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib, Gdk
import os, subprocess

BACKLIGHT = "/sys/class/backlight/intel_backlight"
BIN = "/usr/bin/brightnessctl"

def read_sys(name):
    with open(f"{BACKLIGHT}/{name}") as f:
        return int(f.read().strip())

def set_brightness(pct):
    target = max(1, round(pct / 100 * read_sys("max_brightness")))
    cmd = [BIN, "-d", "intel_backlight", "set", str(target)]
    try:
        subprocess.run(cmd, check=True, capture_output=True)
    except subprocess.CalledProcessError:
        subprocess.run(["sg", "video", "-c", subprocess.list2cmdline(cmd)],
                       check=True, capture_output=True)

class BrightnessUI(Gtk.Window):
    def __init__(self):
        super().__init__(title="Brightness")
        self.set_border_width(18)
        self.set_default_size(320, -1)
        self.set_position(Gtk.WindowPosition.CENTER)

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        self.add(box)

        self.label = Gtk.Label(label="")
        self.label.get_style_context().add_class("dim-label")
        box.pack_start(self.label, False, False, 0)

        self.slider = Gtk.Scale.new(Gtk.Orientation.HORIZONTAL, None)
        self.slider.set_range(0.25, 100)
        self.slider.set_increments(0.25, 1)
        self.slider.set_digits(2)
        self.slider.set_value_pos(Gtk.PositionType.TOP)
        self.slider.set_hexpand(True)
        self.slider.connect("value-changed", self.on_change)
        box.pack_start(self.slider, False, False, 0)

        self.apply = Gtk.Button(label="Apply")
        self.apply.set_sensitive(False)
        self.apply.connect("clicked", self.on_apply)
        box.pack_start(self.apply, False, False, 0)

        self.slider.set_value(self.current_pct())
        self.refresh_label()

    def current_pct(self):
        try:
            return round(read_sys_actual() * 100 / read_sys_max())
        except Exception:
            return 100

    def refresh_label(self):
        self.label.set_text(f"Current: {self.current_pct()} %")

    def on_change(self, w):
        self.refresh_label()
        self.apply.set_sensitive(True)

    def on_apply(self, w):
        set_brightness(self.slider.get_value())
        self.apply.set_sensitive(False)

def read_sys_actual():
    with open(f"{BACKLIGHT}/actual_brightness") as f:
        return int(f.read().strip())

def read_sys_max():
    with open(f"{BACKLIGHT}/max_brightness") as f:
        return int(f.read().strip())

if __name__ == "__main__":
    win = BrightnessUI()
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    Gtk.main()