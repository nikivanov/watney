if /usr/sbin/rfkill list wifi | grep -q "Soft blocked: yes" ; then
    echo "unblocking WiFi"
    rfkill unblock wifi
fi