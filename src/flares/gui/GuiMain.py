import dearpygui.dearpygui as dpg

class GuiMain():
    def __init__(self,DATA_BUFFER):
        self.initialize_dpg()
        self.data_buffer = DATA_BUFFER
    def initialize_dpg(self):
        dpg.create_context() # Setup DPG environment
        dpg.create_viewport(title="FLARES",width=500,height=300) # Create viewport (Actual application window, all other windows exist inside of this one)
        dpg.setup_dearpygui() # "Communicates with graphics hardware to prep renderer and resources" not sure what that means specifically tbh

    def configure_dpg_theme(self):
        with dpg.theme() as disabled_theme:
            with dpg.theme_component(dpg.mvCombo):
                dpg.add_theme_color(dpg.mvThemeCol_Button, [50, 50, 50])
                dpg.add_theme_color(dpg.mvThemeCol_Text, [150, 150, 150])

    def run(self):
        dpg.show_viewport() # Displays the viewport
        while dpg.is_dearpygui_running():
            self.gui_update()
            dpg.render_dearpygui_frame() # Renders a new frame

    def gui_update(self):
        data = self.data_buffer.get_ordered_data()
        try:
            print(f"{data[0][0]},shape: {data[1].shape}")
        except:
            pass
    def stop(self): 
        dpg.destroy_context()