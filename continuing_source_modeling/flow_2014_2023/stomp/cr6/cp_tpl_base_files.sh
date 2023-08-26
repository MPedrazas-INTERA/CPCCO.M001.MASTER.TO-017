source_dir="C:\Users\rweatherl\OneDrive - INTERA Inc\Documents\GitHub\100HR3_v2\100HR3\continuing_source_modeling\scenarios\flow_2014_2022\stomp\cr6"
dest_dir="C:\Users\rweatherl\OneDrive - INTERA Inc\Documents\GitHub\100HR3-Rebound\continuing_source_modeling\flow_2014_2023\stomp\cr6"

# List of specific file names you want to copy
files=("append_release.R" "input_cycle2.tpl" "runstomp.sh")

# Loop through the source subdirectories
for sub_dir in "$source_dir"/*; do
    sub_dir_name=$(basename "$sub_dir")
	echo "$sub_dir_name"
    dest_sub_dir="$dest_dir/$sub_dir_name"
    
    # Check if the destination subdirectory exists and is not empty
    if [[ -d "$dest_sub_dir" && -n "$(ls -A "$dest_sub_dir")" ]]; then
        echo "Copying files from $sub_dir_name to $dest_sub_dir"
        for file_name in "${files[@]}"; do
            source_file="$sub_dir/$file_name"
            if [[ -f "$source_file" ]]; then
                cp "$source_file" "$dest_sub_dir/"
                echo "Copied $file_name"
            fi
        done
    fi
done

echo "Copy process completed."