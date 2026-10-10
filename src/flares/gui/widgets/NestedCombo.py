import dearpygui.dearpygui as dpg

class NestedCombo:

    def __init__(self,DATA,HEIGHT=20,WIDTH=60):
        self.data = None
        self.active_category = None
        self.expanded = False
        self.current_value = None
        self.element_width = WIDTH
        self.element_height = HEIGHT
        self.generate_elements()
        self.update_items(DATA)

    def generate_elements(self):
        with dpg.theme() as self.dropdown_theme:

            with dpg.theme_component(dpg.mvAll):
                dpg.add_theme_style(dpg.mvStyleVar_ItemSpacing, 0, 0, category=dpg.mvThemeCat_Core)
                dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 0, category=dpg.mvThemeCat_Core)

        with dpg.group(horizontal=True,width=2*self.element_width) as self.tag:
            self.cat_box = dpg.add_group(show=False,width=self.element_width)
            self.item_box = dpg.add_group(width=self.element_width)

        dpg.bind_item_theme(self.tag,self.dropdown_theme)

    def update_items(self,DATA):
        self.data = DATA
        self.active_category = next(iter(self.data))
        dpg.delete_item(self.cat_box,children_only=True)
        dpg.delete_item(self.item_box,children_only=True)
        if self.active_category!= None and self.active_category in self.data.keys():
            
            # Add new Category Elements
            for cat in self.data.keys():
                dpg.add_button(tag=f"{cat}_element",width=self.element_width,height=self.element_height,label=cat,parent=self.cat_box)
                with dpg.item_handler_registry() as registry:
                    dpg.add_item_hover_handler(callback=self.category_callback, user_data=cat)
                    dpg.bind_item_handler_registry(f"{cat}_element",registry)

            # Add new Item Elements
            dpg.add_spacer(show=False,height=0,parent=self.item_box,tag=f"{self.tag}_item_box_spacer")
            for cat,items in self.data.items():
                for item in items:
                    dpg.add_button(label=item,tag=f"{item}_element",width=self.element_width,height=self.element_height,show=False,parent=self.item_box)
                    with dpg.item_handler_registry() as registry:
                        dpg.add_item_clicked_handler(callback=self.option_callback,user_data=item)
                        dpg.bind_item_handler_registry(f"{item}_element",registry)
            
            # Set Default Value
            self.set_value(dpg.get_item_label(dpg.get_item_children(self.item_box)[1][1]))
            
    def set_value(self,new_value):
        for item_element in dpg.get_item_children(self.item_box)[1][1:]:
            if dpg.get_item_label(item_element) == new_value:
                dpg.show_item(item_element)
                self.current_value=new_value
                print(f"New Value: {self.current_value}")
            else:
                dpg.hide_item(item_element)

    
    def category_callback(self, sender, app_data, user_data, refresh=False):
        if user_data != self.active_category or refresh:
            self.active_category = user_data
            active_items = self.data[self.active_category]
            for item in dpg.get_item_children(self.item_box)[1][1:]:
                if dpg.get_item_label(item) in active_items:
                    dpg.show_item(f"{dpg.get_item_label(item)}_element")
                else:
                    dpg.hide_item(f"{dpg.get_item_label(item)}_element")
            category_index = list(self.data).index(user_data)
            dpg.set_item_height(f"{self.tag}_item_box_spacer",self.element_height*category_index)

    def option_callback(self, sender, app_data, user_data):

        if self.expanded: # Collapse
            self.set_value(user_data)
            dpg.hide_item(self.cat_box)
            dpg.hide_item(f"{self.tag}_item_box_spacer")
            self.expanded = False
            
        else: # Expand
            dpg.show_item(self.cat_box)
            dpg.show_item(f"{self.tag}_item_box_spacer")
            self.category_callback(None, None, self.active_category,True)
            self.expanded = True
            
data = {"category 1":["option 1","option 2","option 3"],
                     "category 2":["option 4", "option 5","option 6"],
                     "category 3":["option 7", "option 8","option 9","last option"]}



dpg.create_context() # Setup DPG environment
dpg.create_viewport(title="FLARES",width=1000,height=1000) # Create viewport (Actual application window, all other windows exist inside of this one)
dpg.setup_dearpygui() # "Com


with dpg.window(label="Virtual Session", tag="nested_combo_virtual_session",width=300):
    NestedCombo(data)

dpg.show_viewport()

while dpg.is_dearpygui_running():
    dpg.render_dearpygui_frame() # Renders a new frame