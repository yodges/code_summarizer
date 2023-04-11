from create_notebook import create_notebook
from extract_code import extract_code
from utils import copy_directory_tree, extract_py_files, filter_files, read_multiline_input


def main():
    output_file = '/Users/mhodges/PycharmProjects/crypto_twitter_analytics/' \
                  'GCPApps/toto/scratch/summarized_code.py'
    output_notebook = '/Users/mhodges/PycharmProjects/crypto_twitter_analytics/' \
                      'GCPApps/toto/scratch/notebook_docs.ipynb'

    source_directory = input("Enter the source directory: ")
    tree_string = copy_directory_tree(source_directory)

    # Use the read_multiline_input function to read the directory tree string.
    tree_string_input = read_multiline_input(
        "Paste the directory tree string to filter directory code (Press enter twice to finish):")
    if not tree_string_input:
        tree_string_input = tree_string

    include = extract_py_files(tree_string_input)
    print("Extracting:", include)

    filtered_files = filter_files(source_directory, include=include)

    extractor = extract_code(filtered_files, output_file)  # Store the returned extractor instance

    # Call the create_notebook function with the extracted docstrings and code blocks from the extractor instance
    create_notebook(extractor.docstring_blocks, extractor.code_blocks, output_notebook)


if __name__ == "__main__":
    main()
