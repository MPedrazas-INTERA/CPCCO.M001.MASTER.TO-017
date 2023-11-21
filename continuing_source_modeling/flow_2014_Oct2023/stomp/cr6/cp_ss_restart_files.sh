source_base_dir="S:\PSC\CHPRC.C003.HANOFF\Rel.112\transport calibration\model_files\continuing_source_modeling\stomp\cr6"
dest_base_dir="C:\Users\rweatherl\OneDrive - INTERA Inc\Documents\GitHub\100HR3-Rebound\continuing_source_modeling\flow_2014_Oct2023\stomp\cr6"

# Loop through the source folders
for source_folder in "$source_base_dir"/*; do
    folder_name=$(basename "$source_folder")
    dest_folder="$dest_base_dir/$folder_name"

    # Check if the source sub-subdirectory exists and is not empty
    source_sub_sub_dir="$source_folder/ss_flow"
    if [[ -d "$source_sub_sub_dir" && -n "$(ls -A "$source_sub_sub_dir")" ]]; then
        # Create the destination sub-subdirectory if it doesn't exist
        mkdir -p "$dest_folder/ss_flow"

        # Copy the contents of source sub-subdirectory to destination sub-subdirectory
        cp -r "$source_sub_sub_dir"/* "$dest_folder/ss_flow/"
        echo "Copied contents from $source_sub_sub_dir to $dest_folder/ss_flow/"
    fi
done

echo "Copy process completed."