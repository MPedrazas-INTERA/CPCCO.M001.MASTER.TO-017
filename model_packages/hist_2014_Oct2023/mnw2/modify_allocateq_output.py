# Function to replace the first n occurrences of a substring in a text file
def replace_first_n_occurrences(partial_string, new_string, n):
    with open('100hr3.mnw2', 'r') as file:
        content = file.read()

    replaced_content = content.replace(partial_string, new_string, n)

    with open('100hr3.mnw2', 'w') as file:
        file.write(replaced_content)

    print(f"Replaced the first {n} occurrences of '{partial_string}' with '{new_string}'.")

    return None

if __name__ == "__main__":

    partial_string = '     0.000'
    new_string = '         0'
    nwells = 163 ## number of wells (this is how many times the string needs to be replaced. Used to avoid editing content past this point
    replace_first_n_occurrences(partial_string, new_string, nwells)