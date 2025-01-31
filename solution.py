#!/bin/python
from typing import List, Optional, Set
import random
import sys
import os.path
import os
from sklearn.cluster import KMeans
# from sklearn.decomposition import *
import time
import numpy as np
from math import floor

sys.setrecursionlimit(2000)
# total = 0

tags = {}

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

    prev: Photo = photos[0]
    score = 0
    for p in photos[1:]:
        inter = prev.tags.intersection(p.tags)
        score += min(map(len, [inter, p.tags - inter, prev.tags - inter]))
        prev = p

    return score

def expected_get_score(Photo):
    if len(photos) == 0:
        return 0

    prev = photos[0]
    score = 0
    for p in photos[1:]:
        inter = prev*p
        score += min(map(sum, [inter, p.tags - inter, prev.tags - inter]))
        # score += min(map(len, [inter, p.tags - inter, prev.tags - inter]))
        prev = p

    return score

def tag_vector(photos):
    tags = set()

    for photo in photos:
        for tag in photo.tags:
            tags.add(tag)

    tags = list(tags)
    tag_dict = {}
    tag_vector = []

    for i in range(len(tags)):
        tag_dict[tags[i]] = i

    for photo in photos:
        vector = np.zeros(len(tags))
        for tag in photo.tags:
            vector[tag_dict[tag]] = 1
        tag_vector.append(vector)

    tag_vector = np.asarray(tag_vector)

    kmeans = KMeans(n_clusters=5, random_state=0).fit(tag_vector)
    p = kmeans.predict(tag_vector)
    print(p[0])
    

def tag_frequency(photos):
    global tags
    tags = {}
    for photo in photos:
        for tag in photo.tags:
            if tag in tags:
                tags[tag] += 1
            else:
                tags[tag] = 1



# class ExemplarPhoto:
#     def __init__(self, tags):


class Slide:
    _left: Photo
    _right: Optional[Photo]
    dual: bool = False
    tags: Set[str]

    def __init__(self, left: Photo, right: Optional[Photo] = None) -> None:
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
            self.tags = left.tags
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
        self.tags = left.tags.union(right.tags)
        self.dual = True

    def __str__(self):
        if not self.dual:
            return str(self._left.id)

        return "{} {}".format(self._left.id, self._right.id)


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
        assert(t is not None)
        # if current_path[-1].is_vertical() and require_vertical:
        #     continue
        # choices.append(dfs(current_path + [photo], t, photo.is_vertical() != require_vertical))
        choices.append(dfs(current_path + [photo], t))
    return max(choices, key=lambda x: x[0])

def dfs2(current_path, remaining_paths):
    if len(remaining_paths) == 0:
        return (get_score(current_path), current_path)

    choices = []
    for path in remaining_paths:
        t = remaining_paths.copy()
        t.remove(path)
        choices.append(dfs2())


def solve(photos_in):
    score = 0
    path = []
    for photos in split_list(photos_in):
        photo_set = set(photos)
        result = dfs([], photo_set)
        score += result[0]
        # [x.id for x in result[1]]
        path += result[1]
    # print("The score: " + str(score))

    return get_score(path), path
    # return score, path


def split_list(l):
    n = 5
    out = [l[x*n:x*n+n] for x in range(floor(len(l)/n))]
    # out += l[:(len(l)%n)+1]
    # out.append(l[-((len(l)%n)+1):])
    return out


def output(filename, photos):
    slide_count: int = 0
    # prev: Optional[Photo] = None
    slides = []

    f = open(filename, "w")

    for photo in photos:
        slides.append(str(photo))
        # if photo.is_vertical() and prev is None:
        #     prev = photo
        #     continue

        # if prev is None:
        #     slides.append("{}".format(photo.id))
        # else:
        #     slides.append("{} {}".format(prev.id, photo.id))

        # prev = None
        slide_count += 1

    f.write("{}\n".format(slide_count))
    f.write("\n".join(slides))
    f.flush()
    f.close()


def find_distinct_tags(photos: List[Photo]) -> Set[str]:
    tags = set()
    all_tags = [p.tags for p in photos]
    tags.update(*all_tags)
    return tags


def sort_photos(photos: List[Photo]) -> List[Slide]:
    slides: List[Slide] = list(map(
        Slide, filter(lambda p: p.is_horizontal(), photos)))
    
    vertical_photos = list(filter(lambda p: p.is_vertical(), photos))
    for i in range(0, len(vertical_photos), 2):
        left: Photo = vertical_photos[i]
        right: Photo = vertical_photos[i+1]
        slide = Slide(left, right)
        slides.append(slide)

    random.shuffle(slides)

    return slides

def main():
    if len(sys.argv) != 2:
        print("Please provide an input file as the first argument")
        return

    filename: str = sys.argv[1]

    if not os.path.isfile(filename):
        print("File {} doesn't exist".format(filename))
        return

    solution_filename: str = "solution_" + filename

    # Parse photos
    prev_time: time.time = time.time()
    photos: List[Photo] = parse_input(filename)
    print("Took {}s to parse {} photos".format(
        time.time() - prev_time, len(photos)))

    # Find distinct tags
    prev_time = time.time()
    distinct_tags = find_distinct_tags(photos)
    print("Took {}s to find {} distinct tags".format(
        time.time() - prev_time, len(distinct_tags)))
    
    # Sort photos
    slides = sort_photos(photos)

    print("Tag Vector")
    tag_vector(photos)

    # Solve the task
    prev_time = time.time()
    score, path = solve(slides)
    print("Took {}s to solve {} slides".format(
        time.time() - prev_time, len(slides)))

    # Print the score
    print("Score of solution: {}".format(score))

    # Write the solution
    output(solution_filename, path)


if __name__ == "__main__":
    main()
