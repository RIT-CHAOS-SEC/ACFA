## Project params ## DO NOT MODIFY
APP_LOGS_PATH = "../logs/"#"./"
APP_NAME = "demo_prv"
CFG_FILE_PATH = "./objs/cfg.bin"
HMAC_PMEM_FILE_PATH = "./objs/pmem_hmac.bin"
SHADOW_STACK_FILE_PATH = "./objs/shadow_stack.bin"

# Log params
CF_LOG_SIZE = 256 #in bytes
LOG_ENTRIES = CF_LOG_SIZE/4 # Expected total log entries: bytes / 4 bytes per entry

## Script constants
QUIT = "-q"

## TCB definitions
TCB_B00T_CALL_ENTRY = "e040a000"
TCB_BOOT_RET_ENTRY = "dffee040"
TCB_MIN = "a000"
TCB_MAX = "dffe"

#### Fancy printing
#### Source: https://patorjk.com/software/taag/
#### Fonts used: Ivrit, ANSI Regular
## demo header
header=" █████   ██████ ███████  █████      ██████  ███████ ███    ███  ██████  "+'\n'+"██   ██ ██      ██      ██   ██     ██   ██ ██      ████  ████ ██    ██ "+'\n'+"███████ ██      █████   ███████     ██   ██ █████   ██ ████ ██ ██    ██ "+'\n'+"██   ██ ██      ██      ██   ██     ██   ██ ██      ██  ██  ██ ██    ██ "+'\n'+"██   ██  ██████ ██      ██   ██     ██████  ███████ ██      ██  ██████ "

## protocol round / current report num
printIter = ["","","",""]
printIter[0] =" ____  _____ ____   ___  ____ _____     ___  "+"\n"+"|  _ \\| ____|  _ \\ / _ \\|  _ \\_   _|   / _ \\ "+"\n"+"| |_) |  _| | |_) | | | | |_) || |    | | | |"+"\n"+"|  _ <| |___|  __/| |_| |  _ < | |    | |_| |"+"\n"+"|_| \\_\\_____|_|    \\___/|_| \\_\\|_|     \\___/"+"\n"
printIter[1] = " ____  _____ ____   ___  ____ _____    _ "+"\n"+"|  _ \\| ____|  _ \\ / _ \\|  _ \\_   _|  / |"+"\n"+"| |_) |  _| | |_) | | | | |_) || |    | |"+"\n"+"|  _ <| |___|  __/| |_| |  _ < | |    | |"+"\n"+"|_| \\_\\_____|_|    \\___/|_| \\_\\|_|    |_|"+"\n"
printIter[2] =  "____  _____ ____   ___  ____ _____    ____ "+"\n"+"|  _ \\| ____|  _ \\ / _ \\|  _ \\_   _|  |___ \\ "+"\n"+"| |_) |  _| | |_) | | | | |_) || |      __) |"+"\n"+"|  _ <| |___|  __/| |_| |  _ < | |     / __/ "+"\n"+"|_| \\_\\_____|_|    \\___/|_| \\_\\|_|    |_____|"
printIter[3] = " ____  _____ ____   ___  ____ _____    _____ "+"\n"+"|  _ \\| ____|  _ \\ / _ \\|  _ \\_   _|  |___ / "+"\n"+"| |_) |  _| | |_) | | | | |_) || |      |_ \\ "+"\n"+"|  _ <| |___|  __/| |_| |  _ < | |     ___) |"+"\n"+"|_| \\_\\_____|_|    \\___/|_| \\_\\|_|    |____/"

## Log verification messages
acceptLog = "  ____ _____ _     ___   ____         _    ____ ____ _____ ____ _____ _____ ____"+"\n"+" / ___|  ___| |   / _ \\ / ___|       / \\  / ___/ ___| ____|  _ \\_   _| ____|  _ \\ "+"\n"+"| |   | |_  | |  | | | | |  _       / _ \\| |  | |   |  _| | |_) || | |  _| | | | |"+"\n"+"| |__ |  _| | |__| |_| | |_| |     / ___ \\ |__| |___| |___|  __/ | | | |___| |_| |"+"\n"+" \\____|_|   |_____\\___/ \\____|    /_/   \\_\\____\\____|_____|_|    |_| |_____|____/"+"\n"
rejectLog = "  ____ _____ _     ___   ____       ____  _____    _ _____ ____ _____ _____ ____  "+"\n"+" / ___|  ___| |   / _ \\ / ___|     |  _ \\| ____|  | | ____/ ___|_   _| ____|  _ \\ "+"\n"+"| |   | |_  | |  | | | | |  _      | |_) |  _| _  | |  _|| |     | | |  _| | | | |"+"\n"+"| |___|  _| | |__| |_| | |_| |     |  _ <| |__| |_| | |__| |___  | | | |___| |_| |"+"\n"+" \\____|_|   |_____\\___/ \\____|     |_| \\_\\_____\\___/|_____\\____| |_| |_____|____/ "
logMessage = [rejectLog, acceptLog]

## Hmac verification messages
rejectMac = " ___ _   ___     ___    _     ___ ____           __  __    _    ____ "+"\n"+"|_ _| \\ | \\ \\   / / \\  | |   |_ _|  _ \\         |  \\/  |  / \\  / ___|"+"\n"+" | ||  \\| |\\ \\ / / _ \\ | |    | || | | |        | |\\/| | / _ \\| |    "+"\n"+" | || |\\  | \\ V / ___ \\| |___ | || |_| |        | |  | |/ ___ \\ |___ "+"\n"+"|___|_| \\_|  \\_/_/   \\_\\_____|___|____/         |_|  |_/_/   \\_\\____|"
acceptMac = "__     ___    _     ___ ____           __  __    _    ____ "+"\n"+"\\ \\   / / \\  | |   |_ _|  _ \\         |  \\/  |  / \\  / ___|"+"\n"+" \\ \\ / / _ \\ | |    | || | | |        | |\\/| | / _ \\| |    "+"\n"+"  \\ V / ___ \\| |___ | || |_| |        | |  | |/ ___ \\ |___ "+"\n"+"   \\_/_/   \\_\\_____|___|____/         |_|  |_/_/   \\_\\____|"
macMessage = [rejectMac, acceptMac]    

## verification messages
passVerify = " ____   _    ____ ____       __     _______ ____  ___ _____ ___ ____    _  _____ ___ ___  _   _"+"\n"+"|  _ \\ / \\  / ___/ ___|      \\ \\   / / ____|  _ \\|_ _|  ___|_ _/ ___|  / \\|_   _|_ _/ _ \\| \\ | |"+"\n"+"| |_) / _ \\ \\___ \\___ \\       \\ \\ / /|  _| | |_) || || |_   | | |     / _ \\ | |  | | | | |  \\| |"+"\n"+"|  __/ ___ \\ ___) |__) |       \\ V / | |___|  _ < | ||  _|  | | |___ / ___ \\| |  | | |_| | |\\  |"+"\n"+"|_| /_/   \\_\\____/____/         \\_/  |_____|_| \\_\\___|_|   |___\\____/_/   \\_\\_| |___\\___/|_| \\_|"
failVerify = " _____ _    ___ _     _____ ____       __     _______ ____  ___ _____ ___ ____    _  _____ ___ ___  _   _ "+"\n"+"|  ___/ \\  |_ _| |   | ____|  _ \\      \\ \\   / / ____|  _ \\|_ _|  ___|_ _/ ___|  / \\|_   _|_ _/ _ \\| \\ | |"+"\n"+"| |_ / _ \\  | || |   |  _| | | | |      \\ \\ / /|  _| | |_) || || |_   | | |     / _ \\ | |  | | | | |  \\| |"+"\n"+"|  _/ ___ \\ | || |___| |___| |_| |       \\ V / | |___|  _ < | ||  _|  | | |___ / ___ \\| |  | | |_| | |\\  |"+"\n"+"|_|/_/   \\_\\___|_____|_____|____/         \\_/  |_____|_| \\_\\___|_|   |___\\____/_/   \\_\\_| |___\\___/|_| \\_|"
verifyMessage = [failVerify, passVerify]

##
redoWait = " ____  _____ ____  ____   ___  _   _ ____  _____            ____  _____    _ _____ ____ _____ _____ ____  "+"\n"+"|  _ \\| ____/ ___||  _ \\ / _ \\| \\ | / ___|| ____|          |  _ \\| ____|  | | ____/ ___|_   _| ____|  _ \\ "+"\n"+"| |_) |  _| \\___ \\| |_) | | | |  \\| \\___ \\|  _|            | |_) |  _| _  | |  _|| |     | | |  _| | | | |"+"\n"+"|  _ <| |___ ___) |  __/| |_| | |\\  |___) | |___           |  _ <| |__| |_| | |__| |___  | | | |___| |_| |"+"\n"+"|_| \\_\\_____|____/|_|    \\___/|_| \\_|____/|_____|          |_| \\_\\_____\\___/|_____\\____| |_| |_____|____/ "
enterHeal = "  ____ _____  _    ____ _____       _   _ _____    _    _     "+"\n"+" / ___|_   _|/ \\  |  _ \\_   _|     | | | | ____|  / \\  | |    "+"\n"+" \\___ \\ | | / _ \\ | |_) || |       | |_| |  _|   / _ \\ | |    "+"\n"+"  ___) || |/ ___ \\|  _ < | |       |  _  | |___ / ___ \\| |___ "+"\n"+" |____/ |_/_/   \\_\\_| \\_\\|_|       |_| |_|_____/_/   \\_\\_____|"
enterExec = " ____ _____  _    ____ _____       _______  _______ ____ "+"\n"+"/ ___|_   _|/ \\  |  _ \\_   _|     | ____\\ \\/ / ____/ ___|"+"\n"+"\\___ \\ | | / _ \\ | |_) || |       |  _|  \\  /|  _|| |    "+"\n"+" ___) || |/ ___ \\|  _ < | |       | |___ /  \\| |__| |___ "+"\n"+"|____/ |_/_/   \\_\\_| \\_\\|_|       |_____/_/\\_\\_____\\____|"
prvnextMessage = [redoWait, enterHeal, enterExec]
## 0 -- out == 0 ---> Reject message, re-enter TCB-Wait
## 1 -- out == 1, app = 0 --> Accept messgge, TCB-Heal
## 2 -- exec == 1, app = 1 --> Accept mesage, Exec