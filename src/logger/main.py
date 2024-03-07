from .Logger import Logger


def main():
    logger = Logger()
    logger.start()
    print("Listening to all keystrokes...")
    while True:
        command = input("Command: ")
        if command == ".end":
            # Remove the terminate command from the second last
            # item in the list, because the last enter creates
            # an empty ""
            logger.log[-2] = logger.log[-2][:-5]
            logger.stop()
            print(logger.log)
            print("Session ended.")
            break


if __name__ == "__main__":
    main()
