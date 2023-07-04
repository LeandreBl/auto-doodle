#!/bin/bash

# Variables needed for further execution
#
# $NEED_ROOT: true/false depending if this script should be run as root or not
NEED_ROOT=true
#
# $VERSION: Version of this script
VERSION=1.0
#
# $RELEASE_DATE: release date of this script
RELEASE_DATE="02 JULY 2023"
#
# $AUTHOR: Author of this script
AUTHOR="leandre.bla@gmail.com"
#
# $AVERAGE_EXECUTION_TIME: On average, the execution time of this script
AVERAGE_EXECUTION_TIME="15min"
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
    GREEN=`tput setaf 2`
    RED=`tput setaf 1`
    YELLOW=`tput setaf 3`
    NO_COLOR=`tput sgr0`
else
    IS_TTY=false
    GREEN=""
    RED=""
    YELLOW=""
    NO_COLOR=""
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
    local COLUMNS=$((`tput cols` - 2))
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

if [[ IS_TTY == "true" ]]; then
    APT_COMMAND="apt"
else
    APT_COMMAND="apt-get"
fi

USER_HOME=/home/$SUDO_USER
HOST_CORES=`grep ^cpu\ cores /proc/cpuinfo | uniq |  awk '{print $4}'`
if [[ `hostname` == "raspberry" ]]; then
    IS_RASPI=true
else
    IS_RASPI=false
fi

#======================================================================================================#
separating_banner "Pre setup"
#------------------------------------------------------------------------------------------------------#
try "Updating apt" $APT_COMMAND update
try "Upgrading apt" $APT_COMMAND upgrade -y
if [[ $IS_RASPI == true ]]; then
    try "Updating raspi" rpi-update
else
    log "Skipping raspi-update, this machine is not a Raspberry Pi"
fi

REQUIRED_APT_PACKAGES="                         \
                    libjpeg8-dev                \
                    clang                       \
                    python3                     \
                    libusb-1.0.0-dev            \
                    libssl-dev                  \
                    cmake                       \
                    libprotobuf-dev             \
                    protobuf-c-compiler         \
                    protobuf-compiler           \
                    libqt5multimedia5           \
                    libqt5multimedia5-plugins   \
                    libqt5multimediawidgets5    \
                    qtmultimedia5-dev           \
                    libqt5bluetooth5            \
                    libqt5bluetooth5-bin        \
                    qtconnectivity5-dev         \
                    pulseaudio                  \
                    librtaudio-dev              \
                    ninja-build                 \
                    pkg-config                  \
                    libgtk-3-dev                \
                    liblzma-dev                 \
                    libglu1-mesa-dev            \
                    "
#                    libstdc++-12-dev            \

#======================================================================================================#
separating_banner "Startup dependencies"
#------------------------------------------------------------------------------------------------------#
try "Updating apt" $APT_COMMAND update
try "Installing dependencies" $APT_COMMAND install -y $REQUIRED_APT_PACKAGES

#======================================================================================================#
separating_banner "Flutter"
#------------------------------------------------------------------------------------------------------#
if [[ `command_exists flutter` == false ]]; then
    FLUTTER_ARCHIVE=flutter_linux_3.10.5-stable.tar.xz
    FLUTTER_FOLDER=`realpath $USER_HOME/flutter`
    if [[ ! -d $FLUTTER_FOLDER ]]; then
        if [[ ! -f $FLUTTER_ARCHIVE ]]; then
            try_as_current_user "Downloading Flutter package" curl -L -o $FLUTTER_ARCHIVE "https://storage.googleapis.com/flutter_infra_release/releases/stable/linux/$FLUTTER_ARCHIVE"
        fi
        FLUTTER_ARCHIVE_REALPATH=`realpath $FLUTTER_ARCHIVE`
        cd `dirname $FLUTTER_FOLDER`
        try_as_current_user "Unpacking Flutter" tar -xvf $FLUTTER_ARCHIVE_REALPATH
        cd $SCRIPT_DIRECTORY
    fi
    EXPORT_LINE="export PATH=\$PATH:$FLUTTER_FOLDER/bin"
    ZSHRC_FILE=$USER_HOME/.zshrc
    grep "$EXPORT_LINE" $ZSHRC_FILE
    if [[ $? -eq 1 ]]; then
        echo $EXPORT_LINE >> $ZSHRC_FILE
        check_error "Adding $FLUTTER_FOLDER/bin directory to \$PATH" $?
    fi
    try_as_current_user "Precaching Flutter binaries" $FLUTTER_FOLDER/bin/flutter precache
    try_as_current_user "Running a setup check" $FLUTTER_FOLDER/bin/flutter doctor
else
    log "Skipping Flutter, already installed"
fi

#======================================================================================================#
separating_banner "Boost 1.66"
#------------------------------------------------------------------------------------------------------#
BOOST_ARCHIVE=boost_1_66_0.tar.bz2
BOOST_FOLDER=${BOOST_ARCHIVE%%.*}
if [[ ! -d $BOOST_FOLDER ]]; then
    if [[ ! -f $BOOST_ARCHIVE ]]; then
        try_as_current_user "Downloading boost 1.66 sources" curl -L -o $BOOST_ARCHIVE https://boostorg.jfrog.io/artifactory/main/release/1.66.0/source/$BOOST_ARCHIVE
    fi
    try_as_current_user "Unpacking boost 1.66" tar -xvf $BOOST_ARCHIVE
fi
cd $BOOST_FOLDER
try_as_current_user "Setting up boost 1.66" ./bootstrap.sh
try "Installing boost 1.66" ./b2 -q --without-python define=BOOST_LOG_DYN_LIN threading=multi --prefix=/usr install
cd $SCRIPT_DIRECTORY

#======================================================================================================#
separating_banner "MJPG Streamer"
#------------------------------------------------------------------------------------------------------#
MJPG_DIRECTORY=`realpath mjpg-streamer`
if [[ ! -d $MJPG_DIRECTORY ]]; then
    try_as_current_user "Cloning repository" git clone https://github.com/LMBernardo/mjpg-streamer.git $MJPG_DIRECTORY
fi
cd $MJPG_DIRECTORY/mjpg-streamer-experimental
try_as_current_user "Creating build directory" mkdir -p _build
cd _build
try_as_current_user "Setting up cmake" cmake -DENABLE_HTTP_MANAGEMENT=ON ..
try_as_current_user "Building mjpg-streamer" make -j $HOST_CORES
try "Installing mjpg-streamer" make install
cd $SCRIPT_DIRECTORY

#======================================================================================================#
separating_banner "Android Auto SDK"
#------------------------------------------------------------------------------------------------------#
AASDK_DIRECTORY=aasdk
if [[ ! -d $AASDK_DIRECTORY ]]; then
    try_as_current_user "Cloning repository" git clone -b master https://github.com/f1xpl/aasdk.git $AASDK_DIRECTORY
    try_as_current_user "Fixing their bullshit C++ code" sed -i "s/LIBUSB_HOTPLUG_EVENT_DEVICE_ARRIVED, LIBUSB_HOTPLUG_NO_FLAGS,/LIBUSB_HOTPLUG_EVENT_DEVICE_ARRIVED, (libusb_hotplug_flag) LIBUSB_HOTPLUG_NO_FLAGS,/g" $AASDK_DIRECTORY/src/USB/USBHub.cpp
fi
cd $AASDK_DIRECTORY
try_as_current_user "Creating build directory" mkdir -p build
cd build
try_as_current_user "Setting up cmake" cmake ..
try_as_current_user "Building library" cmake --build . --config Release -- -j $HOST_CORES
cd $SCRIPT_DIRECTORY

#======================================================================================================#
separating_banner "Ilclient firmware"
#------------------------------------------------------------------------------------------------------#
if [[ $IS_RASPI == true ]]; then
    cd /opt/vc/src/hello_pi/libs/ilclient
    try "Building IlClient" make -j $HOST_CORES
    cd -
else
    log "Skipping ilclient, this machine is not a Raspberry Pi"
fi

#======================================================================================================#
separating_banner "OpenAuto"
#------------------------------------------------------------------------------------------------------#
if [[ $IS_RASPI == true ]]; then
    OA_DIRECTORY=openauto
    if [[ ! -d $OA_DIRECTORY ]]; then
        try_as_current_user "Cloning repository" git clone -b master https://github.com/f1xpl/openauto.git $OA_DIRECTORY
    fi
    cd $OA_DIRECTORY
    try_as_current_user "Creating build directory" mkdir -p build
    cd build
    try_as_current_user "Setting up cmake" cmake .. -DCMAKE_BUILD_TYPE=Release -DRPI3_BUILD=TRUE -DAASDK_LIB_DIRS="$SCRIPT_DIRECTORY/$AASDK_DIRECTORY/lib" -DAASDK_INCLUDE_DIRS="$SCRIPT_DIRECTORY/$AASDK_DIRECTORY/include" -DAASDK_LIBRARIES="$SCRIPT_DIRECTORY/$AASDK_DIRECTORY/lib/libaasdk.so" -DAASDK_PROTO_INCLUDE_DIRS="$SCRIPT_DIRECTORY/$AASDK_DIRECTORY/build" -DAASDK_PROTO_LIBRARIES="$SCRIPT_DIRECTORY/$AASDK_DIRECTORY/lib/libaasdk_proto.so" -D Protobuf_PROTOC_EXECUTABLE=/usr/bin/protoc -D BOOST_LOG_DYN_LINK=TRUE
    try_as_current_user "Building library" cmake --build . --config Release -- -j $HOST_CORES
    log "Enabling AutoApp at startup"
    echo "/home/pi/openauto/bin/autoapp" >> /home/pi/.config/lxsession/LXDE-pi/autostart
    check_error "Add autoapp to startup" $?
    cd $SCRIPT_DIRECTORY
else
    log "Skipping OpenAuto, this machine is not a Raspberry Pi"
fi

#======================================================================================================#
separating_banner "Auto-Doodle"
#------------------------------------------------------------------------------------------------------#
MAIN_SERVER_DIRECTORY=`realpath main_server`
if [[ $IS_RASPI == true ]]; then
    try_as_current_user "Installing python dependencies" $SUDO_USER pip install -r $MAIN_SERVER_DIRECTORY/requirements.txt
else
    log "Skipping Auto-Doodle Python dependencies, this machine is not a Raspberry Pi"
fi

#======================================================================================================#
separating_banner "Cleanup"
#------------------------------------------------------------------------------------------------------#
try "Removing Flutter archive if existing" rm -f $FLUTTER_ARCHIVE
try "Removing Boost archive if existing" rm -f $BOOST_ARCHIVE
try "Reapplying ownership of directories" chown -R $SUDO_USER:$SUDO_USER .
try "Updating apt" $APT_COMMAND update
try "Upgrading apt" $APT_COMMAND upgrade -y
try "Autoremove unused packages" $APT_COMMAND autoremove -y

# ===End===
log "$SCRIPT_PATH finished"