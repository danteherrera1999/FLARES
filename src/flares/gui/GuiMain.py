import dearpygui.dearpygui as dpg
from gui.tabs.DataTab import DataTab

class GuiMain():
    def __init__(self,SYSTEM_CONFIG):
        self.system_config = SYSTEM_CONFIG
        self.data_buffer = self.system_config["data buffer"]
        self.tabs = {}
        self.initialize_dpg()

    def initialize_dpg(self):
        dpg.create_context() # Setup DPG environment
        dpg.create_viewport(title="FLARES",width=500,height=300) # Create viewport (Actual application window, all other windows exist inside of this one)
        dpg.setup_dearpygui() # "Communicates with graphics hardware to prep renderer and resources" not sure what that means specifically tbh

        with dpg.viewport_menu_bar():
            with dpg.menu(label="Tools"):
                dpg.add_menu_item(label="New Detached Plot")#callback=open_detached_plot)

        with dpg.window(label="Main", tag="window_main", width=400, height=400):
            dpg.add_spacer(height=20)
            with dpg.tab_bar(label="Tab Bar"):
                self.tabs["DATA"] = DataTab(self.system_config)
                #TABS["CONFIGURE"] = ConfigureTab()

        dpg.set_primary_window("window_main", True)
        dpg.set_viewport_resize_callback(self.viewport_resize_handler)

    def configure_dpg_theme(self):
        with dpg.theme() as disabled_theme:
            with dpg.theme_component(dpg.mvCombo):
                dpg.add_theme_color(dpg.mvThemeCol_Button, [50, 50, 50])
                dpg.add_theme_color(dpg.mvThemeCol_Text, [150, 150, 150])

    def viewport_resize_handler(self,sender, app_data):
            _, _, new_width, new_height = app_data
            
            for tab in self.tabs.values():
                tab.handle_resize(new_width, new_height)

    
    def run(self):
        dpg.show_viewport() # Displays the viewport
        while dpg.is_dearpygui_running():
            self.gui_update()
            dpg.render_dearpygui_frame() # Renders a new frame

    def gui_update(self):
        for tab_name,tab_ref in self.tabs.items():
            tab_ref.update()


    def stop(self): 
        dpg.destroy_context()