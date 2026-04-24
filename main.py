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
        self.set_default_size(450, 400)

        # 1. Load Custom CSS
        self.setup_css()

        # 2. Main Layout
        self.view_stack = Adw.ToolbarView()
        self.set_content(self.view_stack)
        
        # Header Bar
        header = Adw.HeaderBar()
        self.view_stack.add_top_bar(header)

        # Content Container (Scrollable)
        scroll = Gtk.ScrolledWindow()
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=20)
        box.set_margin_top(20)
        box.set_margin_bottom(20)
        box.set_margin_start(20)
        box.set_margin_end(20)
        scroll.set_child(box)
        self.view_stack.set_content(scroll)

        # --- LIVE STATS SECTION ---
        stats_group = Adw.PreferencesGroup(title="Live GPU Status")
        box.append(stats_group)

        self.temp_label = Gtk.Label(label="--.-°C")
        self.temp_label.add_css_class("status-display")
        
        self.mode_label = Gtk.Label(label="Mode: Unknown")
        self.mode_label.add_css_class("dim-label")

        stats_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        stats_box.append(self.temp_label)
        stats_box.append(self.mode_label)
        stats_box.set_margin_top(15)
        stats_box.set_margin_bottom(15)
        
        stats_group.add(stats_box)

        # --- CONFIGURATION SECTION ---
        config_group = Adw.PreferencesGroup(title="Throttling Limits")
        box.append(config_group)

        # Temp Limit Row
        self.temp_spin = Gtk.SpinButton.new_with_range(60.0, 105.0, 1.0)
        self.temp_spin.set_value(85.0) # Default
        
        row1 = Adw.ActionRow(title="Critical Temperature (°C)", subtitle="When the GPU switches to LOW mode")
        row1.add_suffix(self.temp_spin)
        config_group.add(row1)

        # Save Button
        save_btn = Gtk.Button(label="Save & Apply")
        save_btn.add_css_class("suggested-action") # Makes it a nice blue button
        save_btn.set_margin_top(10)
        save_btn.connect("clicked", self.on_save_clicked)
        box.append(save_btn)

        # 3. Start the Timer (Runs every 500ms)
        GLib.timeout_add(500, self.update_stats)

    def setup_css(self):
        css_provider = Gtk.CssProvider()
        css = b"""
        .status-display {
            font-size: 32pt;
            font-weight: 900;
        }
        .dim-label {
            opacity: 0.7;
            font-size: 14pt;
        }
        """
        css_provider.load_from_data(css)
        Gtk.StyleContext.add_provider_for_display(
            Gdk.Display.get_default(), 
            css_provider, 
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

    def update_stats(self):
        """Reads the volatile /run file created by the C engine."""
        try:
            with open("/run/gpugov.stats", "r") as f:
                # Parse Key=Value into a dictionary
                stats = dict(line.strip().split('=') for line in f if '=' in line)
            
            # Update UI elements
            temp = float(stats.get('temp', 0))
            self.temp_label.set_text(f"{temp}°C")
            self.mode_label.set_text(f"Mode: {stats.get('mode', 'Unknown')}")
            
        except Exception as e:
            # If the service isn't running, show a placeholder
            self.temp_label.set_text("Waiting...")
            self.mode_label.set_text("Service Offline")
            
        return True # Returning True keeps the timer looping!

    def on_save_clicked(self, button):
        """Writes to /etc/ using pkexec for privilege escalation."""
        new_temp = self.temp_spin.get_value()
        
        # 1. Write the new config to a temporary file as the standard user
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as tf:
            tf.write(f"temp_critical={new_temp}\n")
            temp_path = tf.name

        try:
            # 2. Use pkexec to move the file to /etc/ and set permissions
            # 3. Send SIGHUP to the C daemon so it reloads the config live
            cmd = f"pkexec sh -c 'mv {temp_path} /etc/gpugov.conf && chmod 644 /etc/gpugov.conf && pkill -HUP gpugov_daemon'"
            
            # Run the command. This will pop up the GNOME password dialog!
            subprocess.run(cmd, shell=True, check=True)
            print("Config saved and daemon signaled successfully.")
            
        except subprocess.CalledProcessError:
            print("User canceled the password prompt or command failed.")
        finally:
            # Cleanup temp file if the move failed
            if os.path.exists(temp_path):
                os.remove(temp_path)


class GpuGovApp(Adw.Application):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.connect('activate', self.on_activate)
    def on_activate(self, app):
        self.win = GpuGovWindow(application=app)
        self.win.present()


if __name__ == '__main__':
    app = GpuGovApp(application_id="com.github.afrnow.gpugov")
    app.run(sys.argv)
