from typing import List
import sys
import os.path
import os


class Photo:
    _is_horiz: bool

    tags: List[str]
    id: int

    def __init__(self, id: int, horizontal: bool, tags: List[str]) -> None:
        self.id = id
        self._is_horiz = horizontal
        self.tags = tags

    def is_horizontal(self) -> bool:
        return self._is_horiz

    def is_vertical(self) -> bool:
        return not self._is_horiz

    def __str__(self):
        return "Photo(id={}, horizontal={}, tags=[{}])".format(
            self.id, self.is_horizontal(),
            ", ".join(self.tags)
        )


def parse_input(filename: str) -> List[Photo]:
    # print(filename)
    f = open(filename)

    expected_entry_count: int = None
    photos: List[Photo] = []
    current_id: int = 0

    for line in f.read().splitlines():
        if expected_entry_count is None:
            expected_entry_count = int(line)
            print("{} entries reported".format(expected_entry_count))
            continue

        # Tags at the start includes H/V and a number
        tags: List[str] = line.split(" ")

        # It's a horizontal image if the first item is H
        horiz: bool = tags[0] == "H"

        # If it's not horizontal, make sure the first item is V
        if not horiz and tags[0] != "V":
            print("Expected V got {} in line {}".format(tags[0], line))
            f.close()
            os.exit(1)
            return

        # Second item is the tag count
        expected_tag_count: int = int(tags[1])

        # Reslice the tags slice
        tags = tags[2:]

        # Ensure size is correct
        if len(tags) != expected_tag_count:
            print("Expected {} tags, got {} tags in line {}",
                  expected_tag_count, len(tags)), line
            f.close()
            os.exit(1)
            return

        # Create and append photo
        p: Photo = Photo(current_id, horiz, tags)
        photos.append(p)

        # Increment current ID
        current_id += 1

    f.close()

    if len(photos) != expected_entry_count:
        print("Expected {} photos, got {} photos",
              expected_entry_count, len(photos))

    return photos


def main():
    if len(sys.argv) != 2:
        print("Please provide an input file as the first argument")
        return

    filename: str = sys.argv[1]

    if not os.path.isfile(filename):
        print("File {} doesn't exist".format(filename))
        return

    photos: List[Photo] = parse_input(filename)

    for photo in photos:
        print(photo)


if __name__ == "__main__":
    main()
