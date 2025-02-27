source ./venv/bin/activate
mkdir -p ./refresh
python3 refresh.py logs_text_stream.txt > output.txt
awk -F'\t' '{gsub(/"/, "", $1); gsub(/"/, "", $2); print $2 > "./refresh/" $1}' output.txt
cd refresh
for file in *.txt; do
  temp_file="${file}.tmp"
  
  # Use printf to interpret escape sequences and save to a temp file
  printf "%b" "$(cat "$file")" > "$temp_file"

  dos2unix "$temp_file"

  # Replace original file with the formatted one
  mv "$temp_file" "$file"
done
cd ..