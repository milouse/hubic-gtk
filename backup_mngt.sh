#!/usr/bin/env bash

HUBIC_COLS=()
for col in $(hubic backup info | head -n1); do
    case $col in
        Last)
            HUBIC_COLS+=(--column='Last backup')
            ;;
        Local)
            HUBIC_COLS+=(--column='Local path')
            ;;
        backup|path)
            ;;
        *)
            HUBIC_COLS+=(--column=$col)
            ;;
    esac
done

HUBIC_FIELDS=()
while read LINE; do
    col_items=$(echo $LINE | sed -r 's/^(\w+) (Yes|No) ([^ ]+) ([0-9\/]{10}) ([0-9]{2}:[0-9]{2}) ([0-9,]+) ([KMGT]?B)$/\1\n\2\n\3\n\4 \5\n\6\7/')
    for ci in $col_items; do
        HUBIC_FIELDS+=("$ci")
    done
done < <(hubic backup info | sed 1d)

WORKING_BKP=$(zenity --list --title="Backup list" --width=500 --text="Choose your backup from the liste behind" "${HUBIC_COLS[@]}" "${HUBIC_FIELDS[@]}")

[ "$?" != 0 -o ! -n "$WORKING_BKP" ] && exit 1

ACTION=$(zenity --list --radiolist --text="What do you want to do with ${WORKING_BKP}?" --column= --column=Action FALSE Attach FALSE Download False Delete)

echo $ACTION

case $ACTION in
    Attach)
        echo 'Will attach stuff'
        ;;
    Download)
        echo 'Will download stuff'
        ;;
    Delete)
        if zenity --question --text="This will delete all files and archived versions in backup ${WORKING_BKP}, local data will left unmodified.\nDo you want to proceed ?"
        then
            hubic backup delete --force ${WORKING_BKP}
            zenity --info --text="Your backup ${WORKING_BKP} will be shortly deleted from OVH servers"
        fi
        ;;
esac
