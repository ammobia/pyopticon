from tkinter import Label, Frame, Button

class StatusWidget:
    def __init__(self, parent_dashboard):
        self.parent_dashboard = parent_dashboard
        self.main_color = '#FF7F7F'
        self.frame = Frame(parent_dashboard.get_tkinter_object(), highlightbackground = self.main_color, highlightcolor = self.main_color, highlightthickness = 5)
        self.label = Label(self.frame, text="System State: Not Running")
        self.label.pack()
        self.maintenance_button = Button(self.frame, text="Enter Maintenance Mode", command=self.toggle_maintenance_mode)
        self.maintenance_button.pack()

    def get_frame(self):
        return self.frame

    def update(self, event):
        if event == "SYSTEM_STATE_CHANGED":
            new_state = self.parent_dashboard.get_system_state()
            self.label.config(text=f"System State: {new_state}")
            if new_state == "Not Running" or new_state == "Maintenance":
                self.maintenance_button.config(state="normal")
            else:
                self.maintenance_button.config(state="disabled")

    def toggle_maintenance_mode(self):
        current_state = self.parent_dashboard.get_system_state()
        if current_state == "Not Running":
            self.parent_dashboard.set_system_state("Maintenance")
            self.maintenance_button.config(text="Exit Maintenance Mode")
        elif current_state == "Maintenance":
            self.parent_dashboard.set_system_state("Not Running")
            self.maintenance_button.config(text="Enter Maintenance Mode")
