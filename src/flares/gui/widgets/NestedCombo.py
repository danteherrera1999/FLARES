import dearpygui.dearpygui as dpg

class NestedCombo:

    def __init__(self,DATA):
        self.data = DATA
        self.active_category = next(iter(self.data))
        self.tag = self.regenerate_elements()
        self.expanded = False
        self.current_value = None

    def regenerate_elements(self):
        if self.active_category!= None and self.active_category in self.data.keys():

            with dpg.group(horizontal=True,tag="Nested_Combo"):
                with dpg.group(tag="Cat Box",show=False):
                    for cat in self.data.keys():
                        dpg.add_button(tag=f"{cat}_element",width=100,label=cat)
                        with dpg.item_handler_registry() as registry:
                            dpg.add_item_hover_handler(callback=self.category_callback, user_data=cat)
                            dpg.bind_item_handler_registry(f"{cat}_element",registry)

                with dpg.group(tag="Item Box"):
                    active_items = self.data[self.active_category]
                    for cat,items in self.data.items():
                        for item in items:
                            dpg.add_button(label=item,tag=f"{item}_element",width=100,show=item in active_items)
                        
                            with dpg.item_handler_registry() as registry:
                                dpg.add_item_clicked_handler(callback=self.option_callback,user_data=item)
                                dpg.bind_item_handler_registry(f"{item}_element",registry)

                self.set_value(dpg.get_item_label(dpg.get_item_children("Item Box")[1][0]))
            return "Nested_Combo"

    def set_value(self,new_value):
        for item_element in dpg.get_item_children("Item Box")[1]:
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
            for item in dpg.get_item_children("Item Box")[1]:
                if dpg.get_item_label(item) in active_items:
                    dpg.show_item(f"{dpg.get_item_label(item)}_element")
                else:
                    dpg.hide_item(f"{dpg.get_item_label(item)}_element")

    def option_callback(self, sender, app_data, user_data):
        if self.expanded:
            self.set_value(user_data)
            dpg.hide_item("Cat Box")
            self.expanded = False
        else:
            dpg.show_item("Cat Box")
            self.category_callback(None, None, self.active_category,True)
            self.expanded = True
            
data = {"category 1":["option 1","option 2","option 3"],
                     "category 2":["option 4", "option 5"],
                     "category 3":["option 6"]}



dpg.create_context() # Setup DPG environment
dpg.create_viewport(title="FLARES",width=1000,height=1000) # Create viewport (Actual application window, all other windows exist inside of this one)
dpg.setup_dearpygui() # "Com


with dpg.window(label="Virtual Session", tag="nested_combo_virtual_session",width=300):
    NestedCombo(data)

dpg.show_viewport()

while dpg.is_dearpygui_running():
    dpg.render_dearpygui_frame() # Renders a new frame