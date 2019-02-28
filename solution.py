#!/bin/python
from typing import List, Optional, Set
import sys
import os.path
import os
import time
from math import *


# current_path = []
# current_set = set()
# best_path = []
# best_score = 0

sys.setrecursionlimit(2000)
total = 0

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


def get_score(photos: List[Photo]) -> int:
    if len(photos) == 0:
        return 0

    photos = photos.copy()

    curr: Photo = photos.pop(0)
    score = 0
    while len(photos) > 0:
        p: Photo = photos.pop(0)

        inter = curr.tags.intersection(p.tags)
        score += min(map(len,[inter, p.tags - inter, curr.tags - inter]))
        curr = p

    return score


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


def dfs(current_path, photos):
    global total
    if len(photos) == 0:
        return (get_score(current_path), current_path)

    choices = []
    for photo in photos:
        t = photos.copy()
        t.remove(photo)
        assert(t != None)
        choices.append(dfs(current_path + [photo], t))

    return max(choices, key=lambda x: x[0])


def solve(photos_in):
    score = 0
    path = []
    for photos in split_list(photos_in):
        photo_set = set(photos)
        result = dfs([], photo_set)
        score += result[0]
        [x.id for x in result[1]]
        path += result[1]
    # print("The score: " + str(score))
    return score, path


def split_list(l):
    return [l[x:x+5] for x in range(floor(len(l)/5))]


def output(filename, photos):
    slide_count: int = 0
    prev_id: Optional[int] = None
    slides = []

    f = open(filename, "w")

    for photo in photos:
        if photo.is_vertical() and prev_id is None:
            prev_id = photo.id
            continue

        if prev_id is None:
            slides.append("{}".format(photo.id))
        else:
            slides.append("{} {}".format(photo.id, prev_id))

        prev_id = None
        slide_count += 1

    f.write("{}\n".format(slide_count))
    f.write("\n".join(slides))
    f.flush()
    f.close()


def main():
    if len(sys.argv) != 2:
        print("Please provide an input file as the first argument")
        return

    filename: str = sys.argv[1]

    if not os.path.isfile(filename):
        print("File {} doesn't exist".format(filename))
        return

    solution_filename: str = "solution_" + filename

    prev_time: time.time = time.time()
    photos: List[Photo] = parse_input(filename)
    print("Took {}s to parse {} photos".format(
        time.time() - prev_time, len(photos)))

    prev_time = time.time()
    score, path = solve(photos)
    print("Took {}s to solve {} photos".format(
        time.time() - prev_time, len(photos)))

    print("Score of solution: {}".format(score))
    for photo in photos:
        # print(photo)
        pass

    output(solution_filename, path)


if __name__ == "__main__":
    main()
