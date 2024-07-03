#!/bin/bash

# Input and output files
credentials_file="responses.txt"
output_file="ftp_login_results.txt"

# ANSI escape codes for colors
GREEN='\033[92m'
RED='\033[91m'
RESET='\033[0m'

# Check if the credentials file exists
if [ ! -f "$credentials_file" ]; then
    echo "File $credentials_file not found!"
    exit 1
fi

# Function to check FTP login
check_ftp_login() {
    local server="$1"
    local username="$2"
    local password="$3"
    local protocol="$4"
    local port="$5"
    
    if [ "$port" -eq 21 ]; then
        port_option=""
    else
        port_option="-p $port"
    fi

    if [ "$protocol" == "sftp" ]; then
        # Use sshpass for sftp login
        result=$(timeout 3 sshpass -p "$password" sftp -oPort=$port -oBatchMode=no -b - $username@$server <<EOF
EOF
)
    elif [ "$protocol" == "ftp" ]; then
        # Use ftp command for ftp login
        result=$(timeout 3 ftp -inv $port_option $server <<EOF
user $username $password
bye
EOF
)
    else
        echo "Unsupported protocol: $protocol"
        return
    fi
    
    # Check if the login was successful
    if echo "$result" | grep -q "230"; then
        echo -e "${GREEN}Login successful: $protocol $server $username $password${RESET}" >> "$output_file"
    else
        echo -e "${RED}Login failed: $protocol $server${RESET}" >> "$output_file"
    fi
}

# Read credentials file and try to log in to each FTP server
while read -r line; do
    case $line in
        Host:*)
            server="${line#Host: }"
            ;;
        Username:*)
            username="${line#Username: }"
            ;;
        Password:*)
            password="${line#Password: }"
            ;;
        Protocol:*)
            protocol="${line#Protocol: }"
            ;;
        Port:*)
            port="${line#Port: }"
            # Attempt to log in when all details are available
            check_ftp_login "$server" "$username" "$password" "$protocol" "$port" &
            ;;
    esac
done < "$credentials_file"

# Wait for all background jobs to finish
wait

echo "FTP login attempts completed. Check $output_file for results."
