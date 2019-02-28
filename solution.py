from typing import List, Optional, Set
import sys
import os.path
import os
import time


class Photo:
    _is_horiz: bool

    tags: Set[str]
    id: int

    def __init__(self, id: int, horizontal: bool, tags: List[str]) -> None:
        self.id = id
        self._is_horiz = horizontal
        self.tags = set(tags)

    def is_horizontal(self) -> bool:
        return self._is_horiz

    def is_vertical(self) -> bool:
        return not self._is_horiz

    def __str__(self):
        return "Photo(id={}, horizontal={}, tags=[{}])".format(
            self.id, self.is_horizontal(),
            ", ".join(list(self.tags))
        )


class Slide:
    _left: Photo
    _right: Optional[Photo]

    def __init__(self, left: Photo, right: Optional[Photo]) -> None:
        self.set_photos(left, right)

    def get_left(self):
        return self._left

    def get_right(self):
        return self._right

    def set_photos(self, left: Photo, right: Optional[Photo]) -> None:
        """set_photos allows you to modify a slide"""

        # Ensure left exists
        if left is None:
            assert AssertionError(
                "Left photo cannot be None, Right is {}".format(right))

        # If only one photo
        if right is None:
            # If no right hand side, left must be vertical
            if left.is_vertical():
                assert AssertionError(
                    "Cannot create Slide with a single vertical photo")

            self._left = left
            return

        # Ensure both left and right is vertical
        if left.is_horizontal():
            assert AssertionError(
                "Left cannot be horizontal. Left: {}, Right: {}".format(
                    left, right))
        elif right.is_horizontal():
            assert AssertionError(
                "Right cannot be horizontal. Left: {}, Right: {}".format(
                    left, right))

        self._left = left
        self._right = right


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

    prev_time: time.time = time.time()

    photos: List[Photo] = parse_input(filename)

    time_taken = time.time() - prev_time

    print("Took {}s to parse {} photos".format(time_taken, len(photos)))

    for photo in photos:
        # print(photo)
        pass


if __name__ == "__main__":
    main()
