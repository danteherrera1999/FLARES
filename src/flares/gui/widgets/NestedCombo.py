import dearpygui.dearpygui as dpg

class NestedCombo:

    def __init__(self,DATA=None,HEIGHT=20,WIDTH=80):
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
                dpg.add_theme_style(dpg.mvStyleVar_WindowPadding, 0, 0, category=dpg.mvThemeCat_Core)
                dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (30, 30, 30, 255), category=dpg.mvThemeCat_Core)

        self.tag = dpg.add_button(label="",width=self.element_width,height=self.element_height,callback=self.button_callback)
        with dpg.window(popup=True,show=False,no_background=True,no_move=True) as self.popup:
            with dpg.group(horizontal=True):
                self.cat_box = dpg.add_group(width=self.element_width)
                self.item_box = dpg.add_group(width=self.element_width)

        #dpg.bind_item_theme(self.tag,self.dropdown_theme)
        dpg.bind_item_theme(self.popup,self.dropdown_theme)
    def get_value(self):
        return self.current_value
    
    def update_items(self,DATA):
        if DATA is None or not DATA:
            return
        self.data = DATA
        self.active_category = next(iter(self.data))
        dpg.delete_item(self.cat_box,children_only=True)
        dpg.delete_item(self.item_box,children_only=True)
        if self.active_category is not None and self.active_category in self.data.keys():
            
            # Add new Category Elements
            for cat in self.data.keys():
                dpg.add_button(tag=f"{self.tag}_{cat}_element",width=-1,height=self.element_height,label=cat,parent=self.cat_box)
                with dpg.item_handler_registry() as registry:
                    dpg.add_item_hover_handler(callback=self.category_callback, user_data=cat)
                    dpg.bind_item_handler_registry(f"{self.tag}_{cat}_element",registry)

            # Add new Item Elements
            dpg.add_spacer(height=0,parent=self.item_box,tag=f"{self.tag}_item_box_spacer")
            for cat,items in self.data.items():
                show = cat == self.active_category
                for item in items:
                    dpg.add_button(label=item,tag=f"{self.tag}_{item}_element",width=-1,height=self.element_height,show=show,parent=self.item_box)
                    with dpg.item_handler_registry() as registry:
                        dpg.add_item_clicked_handler(callback=self.option_callback,user_data=item)
                        dpg.bind_item_handler_registry(f"{self.tag}_{item}_element",registry)
            
            # Set Default Value
            self.set_value(dpg.get_item_label(dpg.get_item_children(self.item_box)[1][1]))
            
    def set_value(self,new_value):
        for item_element in dpg.get_item_children(self.item_box)[1][1:]:
            if dpg.get_item_label(item_element) == new_value:
                self.current_value=new_value
                dpg.configure_item(self.tag,label=new_value)

    def resize(self,width,height):
        dpg.set_item_width(self.cat_box,width)
        dpg.set_item_width(self.item_box,width)
    
    def category_callback(self, sender, app_data, user_data, refresh=False):
        if user_data != self.active_category or refresh:
            self.active_category = user_data
            active_items = self.data[self.active_category]
            for item in dpg.get_item_children(self.item_box)[1][1:]:
                if dpg.get_item_label(item) in active_items:
                    dpg.show_item(f"{self.tag}_{dpg.get_item_label(item)}_element")
                else:
                    dpg.hide_item(f"{self.tag}_{dpg.get_item_label(item)}_element")
            category_index = list(self.data).index(user_data)
            dpg.set_item_height(f"{self.tag}_item_box_spacer",self.element_height*category_index)

    def button_callback(self, sender, app_data, user_data):
        self.category_callback(None, None, self.active_category,True)
        dpg.configure_item(self.popup,pos=dpg.get_item_rect_min(self.tag),show=True)
    def option_callback(self, sender, app_data, user_data):
        dpg.configure_item(self.popup,show=False)
        self.set_value(user_data)