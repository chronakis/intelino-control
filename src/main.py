from train_driver import TrainDriver
from key_controller import KeyController
from gui_key_controller import GuiKeyController
from reporter import Reporter, ConsoleReporter


def main():
    driver = TrainDriver()
    # key_controller = KeyController()
    # key_controller.set_train_driver(driver)
    # key_controller.control()

    gui_controller = GuiKeyController()
    driver.add_reporter(gui_controller)
    gui_controller.set_train_driver(driver)
    gui_controller.control()


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()
