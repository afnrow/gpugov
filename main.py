import sys
import os
import tempfile
import subprocess
import gi

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw, GLib, Gdk

class GpuGovWindow(Adw.ApplicationWindow):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_title("GPU Governor")
        self.set_default_size(450, 500)
        
        # Overlay for toasts (popups)
        self.overlay = Adw.ToastOverlay()
        self.set_content(self.overlay)
        
        self.setup_css()
        self.view_stack = Adw.ToolbarView()
        self.overlay.set_child(self.view_stack)
        
        header = Adw.HeaderBar()
        self.view_stack.add_top_bar(header)
        
        scroll = Gtk.ScrolledWindow()
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=20)
        for m in ['top', 'bottom', 'start', 'end']:
            getattr(box, f'set_margin_{m}')(20)
        scroll.set_child(box)
        self.view_stack.set_content(scroll)

        # --- LIVE STATS ---
        stats_group = Adw.PreferencesGroup(title="Live GPU Status")
        box.append(stats_group)
        self.temp_label = Gtk.Label(label="--.-°C")
        self.temp_label.add_css_class("status-display")
        self.mode_label = Gtk.Label(label="Mode: Unknown")
        self.mode_label.add_css_class("dim-label")
        
        stats_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        stats_box.append(self.temp_label)
        stats_box.append(self.mode_label)
        stats_group.add(stats_box)

        # --- CONFIG ---
        config_group = Adw.PreferencesGroup(title="Throttling Limits")
        box.append(config_group)
        self.temp_spin = Gtk.SpinButton.new_with_range(60.0, 105.0, 1.0)
        self.temp_spin.set_value(85.0)
        row_temp = Adw.ActionRow(title="Critical Temperature (°C)")
        row_temp.add_suffix(self.temp_spin)
        config_group.add(row_temp)

        save_btn = Gtk.Button(label="Apply Settings")
        save_btn.add_css_class("suggested-action")
        save_btn.connect("clicked", self.on_save_clicked)
        box.append(save_btn)

        GLib.timeout_add(1000, self.update_stats)

    def setup_css(self):
        css_provider = Gtk.CssProvider()
        css_provider.load_from_data(b"""
            .status-display { font-size: 36pt; font-weight: 900; color: #3584e4; } 
            .dim-label { opacity: 0.7; font-size: 14pt; }
        """)
        Gtk.StyleContext.add_provider_for_display(Gdk.Display.get_default(), css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

    def update_stats(self):
        stats_path = "/run/gpugov.stats"
        if not os.path.exists(stats_path):
            self.mode_label.set_text("Daemon not running")
            return True
        try:
            with open(stats_path, "r") as f:
                # IMPORTANT: .strip() on the value removes the padding spaces from C
                stats = {}
                for line in f:
                    if '=' in line:
                        k, v = line.strip().split('=', 1)
                        stats[k] = v.strip() # Remove the extra spaces!
            
            temp = stats.get('temp', '--')
            raw_mode = stats.get('mode', 'Unknown').lower()
            
            mode_map = {"0": "LOW", "1": "AUTO", "2": "HIGH"}
            mode_name = mode_map.get(raw_mode, raw_mode.upper())
            
            self.temp_label.set_text(f"{temp}°C")
            self.mode_label.set_text(f"Mode: {mode_name}")
        except Exception as e:
            print(f"Read error: {e}")
        return True

    def on_save_clicked(self, button):
        t_crit = self.temp_spin.get_value()
        config_content = f"temp_critical={t_crit}\\n" # Escaped for shell

        # We use a proper pkexec command to run sh directly
        # This is more reliable for triggering the GUI agent
        cmd = [
            "pkexec", "sh", "-c", 
            f'echo "{config_content}" > /etc/gpugov.conf && chmod 644 /etc/gpugov.conf && pkill -HUP -x gpugov'
        ]

        try:
            subprocess.run(cmd, check=True)
            self.show_toast("Settings Applied Successfully")
        except subprocess.CalledProcessError:
            self.show_toast("Authentication Failed / Cancelled")

    def show_toast(self, message):
        toast = Adw.Toast.new(message)
        self.overlay.add_toast(toast)

class GpuGovApp(Adw.Application):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.connect('activate', self.on_activate)

    def on_activate(self, app):
        style_manager = Adw.StyleManager.get_default()
        style_manager.set_color_scheme(Adw.ColorScheme.PREFER_DARK)
        self.win = GpuGovWindow(application=app)
        self.win.present()

if __name__ == '__main__':
    app = GpuGovApp(application_id="com.github.afnrow.gpugov")
    app.run(sys.argv)
