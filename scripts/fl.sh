###################################################################
# The program is intended to find the last entry in the directory #
#                                                                 #
# Author: Brent Barbachem                                         #
# Date: July 19, 2021                                             #
###################################################################

# Define some colors based on their ANSI values
ERROR_COLOR='\033[0;31m'  # Red
WARN_COLOR='\033[1;33m'   # Yellow
NORM_COLOR='\033[0;37m'   # Light Grey
NO_COLOR='\033[0m'        # No Color  


PrintError()
{
    if [[ "$-" == *x* ]]; then
	printf "${ERROR_COLOR}${1}${NORM_COLOR}\n"
    fi
}

PrintWarning()
{
    if [[ "$-" == *x* ]]; then
	printf "${WARN_COLOR}${1}${NORM_COLOR}\n"
    fi
}

FindLastModifiedFile()
{
    # Find the last modified file
    # :param $1: List of files
    # :return: Name of the last mofidied from the selection
    #          If no files provided, an empty string is returned
    local last_updated_file=""
    local last_update="0"
    a=("$@")
    #for filename in "${a[@]}"; do
    for filename in $a; do
        file_date=$(date -r $filename "+%m-%d-%Y %H:%M:%S")
        if [ "$file_date" \> "$last_update" ]; then
            last_updated_file=$filename
            last_update=$file_date
        fi
    done
    echo $last_updated_file
}


_Help()
{
    # Function to display the help information about the program
    echo "Usage: fl [OPTION]..."
    echo # Blank Line - Do NOT Remove
    echo "Find the most recent entry for a file in the directory."
    echo # Blank Line - Do NOT Remove
    echo "  -d, --directory      Directory to search [Default to current (.)."
    echo "  -f, --file_text      Text to search for in the filenames.        "
    echo "  -x                   Print Debugging Statements.                 "
    echo # Blank Line - Do NOT Remove
}


while getopts ":h" help_option; do
    case $help_option in
	h) _Help; exit;;
    esac
done

# unset the options find that was already performed
# This environment variable is only set once [manually]
# each time that getopts is called.
unset OPTIND

# Parameters for the life of the program
_directory="."
_file_search_text=""

while getopts ":d:f:x" option; do
    case $option in
	d) _directory=$OPTARG;;
	f) _file_search_text=$OPTARG;;
	x) set -x;;
    esac
done


# bash version, for future use in the event of bash version changes
# only care about the major changes to bash
curr_bash_version=${BASH_VERSION:0:1}
PrintWarning "Using Bash ${BASH_VERSION}"


# find all data in the choice directory. Then we can search the results
# to find the data that we are looking for 
ls_output=$(find $_directory -maxdepth 1 -type f -exec ls -h {} +)


if [ "$_file_search_text" = "" ]; then
    # when no variable was set find the last modified file in the directory
    last_updated_file=$(FindLastModifiedFile "$ls_output")

    if [ "$last_updated_file" = "" ]; then
        PrintError "No files found"
    else
        echo $last_updated_file
    fi
else
    SAVED_NO_CASE_MATCH=$(shopt -p nocasematch; true)  # save the current state
    shopt -s nocasematch  # just in case, remove case sensitive match

    # variable was set, do a text comparison to see what is available and select 
    # the last one from that list
    ret_array=()
    for x in ${ls_output[@]}; do
	if [[ "$x" == *"$_file_search_text" ]]; then
	    ret_array+=($x)
	fi
    done

    eval $SAVED_NO_CASE_MATCH  # reset the original value

    # This will grab the last `modified` file. SO Please DO NOT
    # modify the files and expect a result of finding the last 
    # created file.
        PrintWarning "Searching for last modified file in ${_directory}"
    last_updated_file=$(FindLastModifiedFile "${ret_array[*]}")

    if [ "$last_updated_file" = "" ]; then
	PrintError "No files found"
    else
	echo $last_updated_file
    fi
fi
