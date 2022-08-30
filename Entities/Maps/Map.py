import os

import pygame

from Engine.PopupWindow import PopupWindow
from Entities.Maps.BlockChecks import BlockChecks
from Entities.Maps.CheckListItem import CheckListItem
from Entities.Maps.SimpleCheck import SimpleCheck


class Map:
    def __init__(self, map_datas, index_positions, tracker, active=False):
        self.map_background = None
        self.map_image_filename = None
        self.map_datas = map_datas
        self.tracker = tracker
        self.index_positions = (index_positions["x"], index_positions["y"])
        self.active = active
        self.checks_list_open = False
        self.checks_list = []
        self.current_block_checks = None
        self.check_window = PopupWindow(tracker=self.tracker, index_positions=self.index_positions)
        self.maps_list_window = PopupWindow(tracker=self.tracker, index_positions=self.index_positions)
        self.processing()
        self.processing_checks()
        self.update()

    def processing(self):
        self.map_image_filename = self.map_datas[0]["Datas"]["Background"]
        self.checks_list_background_filename = self.map_datas[0]["Datas"]["SubMenuBackground"]
        self.update()

    def get_name(self):
        return self.map_datas[0]["Datas"]["Name"]

    def processing_checks(self):
        for check in self.map_datas[0]["ChecksList"]:
            if check["Kind"] == "Block":
                block = BlockChecks(check["Id"], check["Name"], check["Positions"], self)

                for check_item in check["Checks"]:
                    temp_check = CheckListItem(check_item["Id"], check_item["Name"], check["Positions"],
                                               check_item["Conditions"], self.tracker)
                    block.add_check(temp_check)

                self.checks_list.append(block)

            if check["Kind"] == "SimpleCheck":
                simple_check = SimpleCheck(check["Id"], check["Name"],
                                           check["Positions"], self, check["Conditions"])
                self.checks_list.append(simple_check)

    def update(self):
        self.map_background = self.tracker.bank.addZoomImage(
            os.path.join(self.tracker.resources_path, self.map_image_filename))

        self.checks_list_background = self.tracker.bank.addZoomImage(
            os.path.join(self.tracker.resources_path, self.checks_list_background_filename))

        if self.current_block_checks:
            box_rect = self.map_datas[0]["Datas"]["DrawBoxRect"]
            box_checks = pygame.Rect(
                (box_rect["x"] * self.tracker.core_service.zoom) + self.checks_list_background.get_rect().x + (
                        self.index_positions[0] * self.tracker.core_service.zoom),
                (box_rect["y"] * self.tracker.core_service.zoom) + self.checks_list_background.get_rect().y + (
                        self.index_positions[1] * self.tracker.core_service.zoom),
                box_rect["w"] * self.tracker.core_service.zoom,
                box_rect["h"] * self.tracker.core_service.zoom)

            self.check_window.set_background_image_path(self.checks_list_background_filename)
            self.check_window.set_arrow_left_image_path(self.map_datas[0]["Datas"]["LeftArrow"]["Image"])
            self.check_window.set_arrow_right_image_path(self.map_datas[0]["Datas"]["RightArrow"]["Image"])
            self.check_window.set_title(self.current_block_checks.name)
            self.check_window.set_title_font(self.tracker.core_service.get_font("mapFontTitle"))
            self.check_window.set_title_label_position_y(self.map_datas[0]["Datas"]["LabelY"])
            self.check_window.set_list_items(self.current_block_checks)
            self.check_window.set_box_rect(box_checks)
            left_arrow = (self.map_datas[0]["Datas"]["LeftArrow"]["Positions"]["x"],
                          self.map_datas[0]["Datas"]["LeftArrow"]["Positions"]["y"])
            right_arrow = (self.map_datas[0]["Datas"]["RightArrow"]["Positions"]["x"],
                           self.map_datas[0]["Datas"]["RightArrow"]["Positions"]["y"])

            self.check_window.set_arrows_positions(left_arrow, right_arrow)
            self.check_window.update()

        else:
            for check in self.checks_list:
                check.update()

    def open_window(self):
        self.check_window.open = True

    def draw(self, screen):
        if self.active:
            screen.blit(self.map_background, (self.index_positions[0] * self.tracker.core_service.zoom,
                                              self.index_positions[1] * self.tracker.core_service.zoom))

            for check in self.checks_list:
                check.draw(screen)

            if self.check_window and self.check_window.is_open():
                self.check_window.draw(screen)

    def get_positions_from_index_positions(self, index_positions_index, position):
        return (self.index_positions[index_positions_index] * self.tracker.core_service.zoom) + (
                position * self.tracker.core_service.zoom)

    def click(self, mouse_position, button):
        if self.check_window.is_open():
            self.check_window.left_click(mouse_position)
            self.current_block_checks.update()
        else:
            self.current_block_checks = None

        for check in self.checks_list:
            if type(check) == BlockChecks:
                if not self.current_block_checks:
                    if self.tracker.core_service.is_on_element(mouse_positions=mouse_position,
                                                               element_positons=check.get_position(),
                                                               element_dimension=(
                                                                       check.get_rect().w, check.get_rect().h)):
                        if button == 1:
                            check.left_click(mouse_position)
                            if not self.check_window.is_open():
                                self.check_window.open = True

            if type(check) == SimpleCheck:
                if self.tracker.core_service.is_on_element(mouse_positions=mouse_position,
                                                           element_positons=check.get_position(),
                                                           element_dimension=(check.get_rect().w, check.get_rect().h)):
                    if button == 1:
                        check.left_click(mouse_position)

        self.update()

    def get_name(self):
        return self.map_datas[0]["Datas"]["Name"]

    def get_data(self):
        checks_datas = []
        for check in self.checks_list:
            checks_datas.append(check.get_data())

        data = {
            "name": self.get_name(),
            "checks_datas": checks_datas
        }
        return data

    def load_data(self, datas):
        checks_datas = datas["checks_datas"]
        for data in checks_datas:
            for check in self.checks_list:
                if (check.id == data["id"]) and (check.name == data["name"]):
                    check.set_data(data)
                    break
