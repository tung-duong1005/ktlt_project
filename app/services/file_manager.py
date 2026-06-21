import os

from app.core.linked_list import MyLinkedList


class FileManager:
    """Handles raw I/O for text files."""

    def readFile(self, path: str) -> MyLinkedList:
        """Reads a file line-by-line, stripping newlines.

        Args:
            path (str): Path to the text file.

        Returns:
            MyLinkedList: A list of non-empty line strings.
        """
        lines = MyLinkedList()
        if not os.path.exists(path):
            return lines
        try:
            with open(path, "r", encoding="utf-8") as f:
                for line in f:
                    clean_line = ""
                    for char in line:
                        if char not in ('\r', '\n'):
                            clean_line += char
                    # Skip empty lines
                    if clean_line != "":
                        lines.addLast(clean_line)
        except Exception as e:
            print(f"Error reading file {path}: {e}")
        return lines

    def writeFile(self, path: str, content: str):
        """Overwrites the contents of a file, creating directories if needed.

        Args:
            path (str): Path to the file.
            content (str): The string content to write.
        """
        try:
            dir_name = os.path.dirname(path)
            if dir_name and not os.path.exists(dir_name):
                os.makedirs(dir_name, exist_ok=True)
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
        except Exception as e:
            print(f"Error writing file {path}: {e}")
