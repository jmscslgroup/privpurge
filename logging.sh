#!/bin/bash

log_set_bold=$'\e[1m'
log_set_dim=$'\e[2m'
log_set_underline=$'\e[4m'
log_set_blink=$'\e[5m'
log_set_inverse=$'\e[7m'
log_set_hidden=$'\e[8m'

log_reset_all=$'\e[0m'
log_reset_bold=$'\e[21m'
log_reset_dim=$'\e[22m'
log_reset_underline=$'\e[24m'
log_reset_blink=$'\e[25m'
log_reset_inverse=$'\e[27m'
log_reset_hidden=$'\e[28m'

log_fore_default=$'\e[39m'
log_fore_black=$'\e[30m'
log_fore_red=$'\e[31m'
log_fore_green=$'\e[32m'
log_fore_yellow=$'\e[33m'
log_fore_blue=$'\e[34m'
log_fore_magenta=$'\e[35m'
log_fore_cyan=$'\e[36m'
log_fore_lgray=$'\e[37m'
log_fore_dgray=$'\e[90m'
log_fore_lred=$'\e[91m'
log_fore_lgreen=$'\e[92m'
log_fore_lyellow=$'\e[93m'
log_fore_lblue=$'\e[94m'
log_fore_lmagenta=$'\e[95m'
log_fore_lcyan=$'\e[96m'
log_fore_white=$'\e[97m'

log_back_default=$'\e[49m'
log_back_black=$'\e[40m'
log_back_red=$'\e[41m'
log_back_green=$'\e[42m'
log_back_yellow=$'\e[43m'
log_back_blue=$'\e[44m'
log_back_magenta=$'\e[45m'
log_back_cyan=$'\e[46m'
log_back_lgray=$'\e[47m'
log_back_dgray=$'\e[100m'
log_back_lred=$'\e[101m'
log_back_lgreen=$'\e[102m'
log_back_lyellow=$'\e[103m'
log_back_lblue=$'\e[104m'
log_back_lmagenta=$'\e[105m'
log_back_lcyan=$'\e[106m'
log_back_white=$'\e[107m'

# make_print_func name arrow_col text_col
log::make_print_func() {
local print_func
read -r -d '' print_func << EOM
${1}() {
    if [ -z "\$1" ]; then return 1; fi
    echo "  ${2}-->${log_reset_all} ${3}\${1}${log_reset_all}"
    if [ "\$#" -gt 1 ]; then
        shift
        for thing in "\${@}"; do
            echo "      ${2}*${log_reset_all} ${3}\${thing}${log_reset_all}";
        done
    fi
}
EOM
eval "${print_func}" && log_funcnames+=(${1})
}

log::enable() {
    log::make_print_func "log::info"  "${log_fore_lgreen}"   "${log_set_bold}"
    log::make_print_func "log::warn"  "${log_fore_lyellow}"  "${log_set_bold}"
    log::make_print_func "log::error" "${log_fore_lred}"     "${log_set_bold}"
    log_enabled=true
}

log::disable() {
    if [ "$log_enabled" = true ]; then
        for i in "${log_funcnames[@]}"; do unset -f "$i"; done
        log_enabled=false
        log_funcnames=()
    fi
}

log::enable