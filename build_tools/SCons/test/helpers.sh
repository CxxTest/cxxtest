function rmln() {
    local symlink="$1"
    if [[ -h "$symlink" ]]
    then
        rm "$symlink" && echo "[symlinks] removed symlink '$symlink'"
    else
        echo "[symlinks] Buggy definition file - symlink '$symlink' does not exist!"
    fi
}

function mkln() {
    local symlink="$1"
    local target="$2"
    if ! [[ -e "$symlink" ]]
    then
        ln -s "$target" "$symlink" && echo "[symlinks] created $symlink symlink"
    else
        if ! [[ -h "$symlink" ]] 
        then
            echo "[symlinks] Buggy definition file - file '$symlink' exists!"
        fi
    fi
}

function remove_symlinks() {
    local symlinks_file="$1"
    if [[ -f "$symlinks_file" ]]
    then
        xargs -a "$symlinks_file" --max-lines=1 "$0" rmln
    fi
}

function create_symlinks() {
    local symlinks_file="$1"
    if [[ -f "$symlinks_file" ]]
    then
        xargs -a "$symlinks_file" --max-lines=1 "$0" mkln
    fi
}

"${@}"
