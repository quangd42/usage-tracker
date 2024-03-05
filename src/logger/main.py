from .Logger import Logger


def main():
    logger = Logger()
    logger.start()
    print("Listening to all keystrokes...")
    while True:
        command = input("Command: ")
        if command == ".end":
            logger.stop()
            print(logger.log)
            print("Session ended.")
            break


if __name__ == "__main__":
    main()
