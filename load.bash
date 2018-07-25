#!/usr/bin/env bash

function log() {
    declare -r level="$1"
    declare -r message="$2"
    echo "$(date --rfc-3339 ns) [$level] $message" >&2
}

function request_hh() {
    declare -r path="$1"; shift
    curl -sGA 'irenica (https://irenica.com/)' -w "\n" "https://api.hh.ru$path" "$@"
}

declare -ri INTERVAL_LENGTH=$((60 * 60))

declare -i startTime=$(date -d '-1 month' +%s)
declare -i endTime=$(date -d now +%s)
while ((startTime <= endTime)); do
    declare -i intervalStart=$startTime
    declare -i intervalEnd=$((intervalStart + INTERVAL_LENGTH))
    declare intervalStartIso="$(date -d @$intervalStart +%FT%T)"
    declare intervalEndIso="$(date -d @$intervalEnd +%FT%T)"
    log INFO "process the interval $intervalStartIso - $intervalEndIso"

    declare -i i=0
    while true; do
        log INFO "process the page #$i"

        declare page="$(
            request_hh '/vacancies' \
                -d "date_from=$intervalStartIso" \
                -d "date_to=$intervalEndIso" \
                -d "page=$i" \
                -d 'per_page=100'
        )"
        declare -i foundCount=$(echo "$page" | jq '.found')
        if ((foundCount > 2000)); then
            log WARNING 'found too many vacancies'
            echo "found too many vacancies at $intervalStartIso" >> warnings
        fi

        echo "$page" | jq -r '.items[].id' | while read id; do
            log INFO "process the vacancy #$id"
            request_hh "/vacancies/$id" >> vacancies
        done

        ((i++))
        declare -i totalCount=$(echo "$page" | jq '.pages')
        if ((i >= totalCount)); then
            break
        fi
    done

    startTime=$intervalEnd
done
