from train_driver import TrainDriver
from key_controller import KeyController


def main():
    driver = TrainDriver()
    key_controller = KeyController()
    driver.add_controller(key_controller)
    driver.drive()
    # Here it blocks and waits
    print("EXITING")


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()
