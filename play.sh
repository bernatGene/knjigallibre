for file in $(printf "%s\n" out*.wav | sort); do
  afplay "$file"
done
