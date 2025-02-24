#!/bin/bash

# Variables needed for further execution
#
# $NEED_ROOT: true/false depending if this script should be run as root or not
NEED_ROOT=false
#
# $VERSION: Version of this script
VERSION=2.0
#
# $RELEASE_DATE: release date of this script
RELEASE_DATE="08 JULY 2023"
#
# $AUTHOR: Author of this script
AUTHOR="leandre.bla@gmail.com"
#
# $AVERAGE_EXECUTION_TIME: On average, the execution time of this script
AVERAGE_EXECUTION_TIME="1min"
#
#
# ===Setup of internal variables and working directory===

SCRIPT_PATH=$(realpath $0)

ORIGINAL_PATH=$(realpath .)

SCRIPT_DIRECTORY=$(dirname $SCRIPT_PATH)

cd $SCRIPT_DIRECTORY

# isatty() and applying colors depending on it
if [ -t 0 ]; then
    IS_TTY=true
    GREEN=`echo -e "\033[32m"`
    RED=`echo -e "\033[31m"`
    YELLOW=`echo -e "\033[33m"`
    NO_COLOR=`echo -e "\033[0m"`
else
    IS_TTY=false
fi

# Verifying if a log file was provided by an upper script calling this one, in this case, we inheritate it
if [[ -z $LOG_FILE ]]; then
    ROOT_SCRIPT=TRUE
    export LOG_FILE=`realpath .$(basename ${SCRIPT_PATH%%.*}.log)`
else
    unset ROOT_SCRIPT
fi

# Verifying the need for privileges and seeking them
if [[ $NEED_ROOT == "true" && `id -u` -ne 0 ]]; then
    echo "$RED"This script must be run with sudo"$NO_COLOR"
    exit 1
fi

# Logging script informations
echo "$SCRIPT_PATH"
echo `date '+%Y-%m-%d %H:%M'`
echo "Author: $AUTHOR"
echo "v$VERSION"
echo "Average execution time: $AVERAGE_EXECUTION_TIME"
echo "Log file available at $LOG_FILE"

log() {
    echo "[`date '+%Y-%m-%d %H:%M'`] $@" >> $LOG_FILE
    echo "[`date '+%Y-%m-%d %H:%M'`] $@"
}

log [`date '+%Y-%m-%d %H:%M'`] "$SCRIPT_PATH"
log [`date '+%Y-%m-%d %H:%M'`] "Author: $AUTHOR, $SCRIPT_PATH version $VERSION"
log [`date '+%Y-%m-%d %H:%M'`] "Average execution time: $AVERAGE_EXECUTION_TIME"
log [`date '+%Y-%m-%d %H:%M'`] "Log file available at $LOG_FILE"

check_error() {
    local MESSAGE=$1
    local EXIT_CODE=$2
    shift
    shift
    local COMMAND=$@
    if [[ $EXIT_CODE -ne 0 ]]; then
        log "ERROR: command \"$COMMAND\" exited with exit code $EXIT_CODE"
        log $MESSAGE: [$RED"KO"$NO_COLOR]
        log "$SCRIPT_PATH failed, see $LOG_FILE for more informations."
        exit 1
    fi
    log $MESSAGE: [$GREEN"OK"$NO_COLOR]
}

try() {
    local MESSAGE=$1
    shift
    log "executing: $@"
    $@ 3>&1 &>>$LOG_FILE 1> >(tee -a >(cat >&3))
    local EXIT_CODE=$?
    check_error "$MESSAGE" "$EXIT_CODE" $@
}

try_as() {
    local MESSAGE=$1
    local USER_AS=$2
    shift
    shift
    try "$MESSAGE" sudo -u $USER_AS $@
}

try_as_current_user() {
    local MESSAGE=$1
    shift
    try_as "$MESSAGE" $SUDO_USER $@
}

ask_yes_no() {
    local PROMPT=$@
    read -p "$PROMPT [Y/n]" ANSWER

    case $ANSWER in
        [Yy]* )
        echo "y"
        ;;
        "")
        echo "y"
        ;;
        * )
        echo "n"
        ;;
    esac
}

repeat() {
    local MESSAGE=$1
    local COUNT=$2
    local I=0
    while [[ $I -le $COUNT ]]; do
        echo -ne "$MESSAGE"
        I=$((I + 1))
    done
}

separating_banner() {
    local MESSAGE=$@
    local COLUMNS=$[`stty size | awk '{print $2}'` - 1]
    local MESSAGE_LENGTH=${#MESSAGE}
    local DIFFERENCE=$[COLUMNS - MESSAGE_LENGTH]
    local PADDING_LEFT=$[DIFFERENCE / 2]
    repeat "=" $COLUMNS
    echo $YELLOW
    repeat " " $PADDING_LEFT
    echo $MESSAGE $NO_COLOR
    repeat "=" $COLUMNS
    echo
}

command_exists() {
    local COMMAND=$1
    if ! [ -x "$(command -v $COMMAND)" ]; then
        echo false
    fi
    echo true
}

# ===Variables===
#
# $SCRIPT_PATH: original path of this script
#
# $ORIGINAL_PATH: original path from where this script was executed
#
# $SCRIPT_DIRECTORY: folder in which this script can be found
#
# $GREEN: ansi color green
#
# $RED: ansi color red
#
# $YELLOW: ansi color yellow
#
# $NO_COLOR: ansi reset color
#
# $IS_TTY: true/false if this script is run in a tty
#
# ===Functions===
#
# log(message...): log all the passed arguments both in the terminal and in the log file
#
# try(explanation_of_the_command, command...): log, execute (as the user who launched this script, root if sudo)
#                                              and verify the output of the command if it fails, the program will exit
#
# try_as(explanation_of_the_command, username, command...): log, execute (as the user passed in argument)
#                                              and verify the output of the command if it fails, the program will exit
#
# try_as_current_user(explanation_of_the_command, command...): log, execute (as the user who really started this script)
#                                              and verify the output of the command if it fails, the program will exit
#
# ask_yes_no(prompt): prompt a message asking the user for yes/or no, it returns a string "y" or "n"
#
# check_error(message, exit_code, command...): check if the exit code is 0 or not, it will then display
#                                              a message and exit the script if the command failed,
#                                              it's useful when the command contains redirections
#                                              and pipes and can't be used in a "try" functions
#
# separating_banner(message...): print a little separating banner with a message in the middle
#
# command_exists(command): prints true or false if the command exists or not
#
# ===Code===
# Insert your code here

APT_COMMAND="pkg"

HOST_CORES=`lscpu | grep 'CPU(s):' | awk '{print $2}'`

#======================================================================================================#
separating_banner "Pre setup"
try "Updating PKG" pkg update
try "Setting PKG Termux User Repository" pkg install -y tur-repo
try "Installing packages" pkg install -y curl git openssh zsh python3 cmake binutils python-numpy build-essential gcc-11 ninja
try "Upgrading PKG" pkg upgrade
#------------------------------------------------------------------------------------------------------#

#======================================================================================================#
separating_banner "Installing oh-my-zsh"
(echo "Y"; echo "exit") | sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"
#------------------------------------------------------------------------------------------------------#

#======================================================================================================#
separating_banner "Auto-Doodle main server"
#------------------------------------------------------------------------------------------------------#
MAIN_SERVER_DIRECTORY=`realpath main_server`

try "Installing python dependencies" python3 -m pip install -r $MAIN_SERVER_DIRECTORY/requirements.txt
try "Moving GPIO package to current directory" ln -sr ~/../usr/lib/python3.11/site-packages/gpio/ $MAIN_SERVER_DIRECTORY/GPIO

#======================================================================================================#
separating_banner "Cleanup"
#------------------------------------------------------------------------------------------------------#
try "Reapplying ownership of directories" chown -R $SUDO_USER:$SUDO_USER .
try "Updating PKG" pkg update
try "Upgrading PKG" pkg upgrade

# ===End===
log "$SCRIPT_PATH finished"
