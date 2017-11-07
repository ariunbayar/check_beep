#!/bin/bash
script_dir=$(dirname "$(readlink -e "$0")")

function generate_launcher_file {

file="$HOME/Desktop/check-beep.desktop"
touch "$file"
chmod +x "$file"
cat > "$file" <<EOL
#!/usr/bin/env xdg-open

[Desktop Entry]
Version=1.0
Type=Application
Terminal=true
Exec=$script_dir/launch.sh
Name=check-beep
Comment=Ping and load URL to test availability, Also launches nfcatd
Icon=gnome-terminal
EOL

}

if [[ $1 = "install" ]]; then
    generate_launcher_file
else
    sleep 0.5
    screen -dmS test bash -c '/usr/bin/python /home/user/projects/check_beep/py-app-indicator.py'
    sleep 0.5
fi
