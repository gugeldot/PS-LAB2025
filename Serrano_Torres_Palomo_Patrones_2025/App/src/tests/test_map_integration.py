import sys
import os
import types

# Ensure the repository's `src` directory is on sys.path so top-level imports
# like `map.map` and `core.*` resolve regardless of the current working dir.
HERE = os.path.dirname(__file__)
SRC_DIR = os.path.abspath(os.path.join(HERE, '..'))

if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)


from map.map import Map
from core.mineCreator import MineCreator
from core.wellCreator import WellCreator


def run_test():
    print('Starting map <-> structure integration test')

    m = Map(50, 50)
    print('Map created:', m.width, 'x', m.height)

    mine_creator = MineCreator()
    well_creator = WellCreator()

    # create structures without a full GameManager (draw won't be used here)
    mine = mine_creator.createStructure((0, 0), 7, None)
    ok = m.placeStructure(1, 1, mine)
    print('Placed mine at (1,1):', ok)
    print('Cell (1,1) empty?', m.getCell(1, 1).isEmpty())

    # try to place another structure on the same cell (should fail)
    well = well_creator.createStructure((2, 2), 2, None)
    ok2 = m.placeStructure(1, 1, well)
    print('Tried placing well at occupied (1,1), success?', ok2)

    # remove and verify
    removed = m.removeStructure(1, 1)
    print('Removed from (1,1) is same object?', removed is mine)
    print('Cell (1,1) empty after remove?', m.getCell(1, 1).isEmpty())

    # place well
    ok3 = m.placeStructure(2, 2, well)
    print('Placed well at (2,2):', ok3)

    # save and load
    tmpfile = './test_map_layout.json'
    m.save_to_file(tmpfile)
    print('Saved map to', tmpfile)

    creators = {'Mine': mine_creator, 'Well': well_creator}
    m2 = Map.load_from_file(tmpfile, creators=creators, gameManager=None)
    # m2 is the singleton instance; ensure we can access cells
    c_mine = m2.getCell(2, 2)  # NOTE: depending on save format, newly placed well was at (2,2)
    # Search grid for any non-empty cell to demonstrate reload
    found = []
    for y in range(m2.height):
        for x in range(m2.width):
            c = m2.getCell(x, y)
            if not c.isEmpty():
                found.append((x, y, c.structure.__class__.__name__))

    print('Structures found after reload:', found)


if __name__ == '__main__':
    run_test()
