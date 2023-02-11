class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def colored_message(msg : str, color : bcolors):
    print(color + msg + bcolors.ENDC)

def fail_message(msg : str):
    colored_message(msg, bcolors.FAIL)

def warning_message(msg : str):
    colored_message(msg, bcolors.WARNING)

def success_message(msg : str):
    colored_message(msg, bcolors.OKBLUE)