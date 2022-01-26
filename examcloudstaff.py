import json
from operator import itemgetter

OBJECT_STATE = {}


class GridItem:
    name = None
    position = [0, 0]

    def __init__(self, name, position):
        self.name = name
        self.position = position
        self.save_state()

    def save_state(self):
        OBJECT_STATE[self.name] = {"type": type(self).__name__, **self.__dict__}


class Item(GridItem):
    name = None
    position = [0, 0]
    attack_modifier = 0
    defence_modifier = 0
    equipped = False

    def __init__(self, name, position, attack_modifier, defence_modifier):
        self.attack_modifier = attack_modifier
        self.defence_modifier = defence_modifier
        super().__init__(name, position)


class Knight(GridItem):
    status = None
    item = None
    DROWNED = "DROWNED"
    DEAD = "DEAD"
    LIVE = "LIVE"

    def __init__(self, name, position, attack=1, defence=1, status=LIVE, item=None):
        self.attack = attack
        self.defence = defence
        self.status = status
        self.item = item
        super().__init__(name, position)

    def _get_next_position(self, move):
        pos = None
        if move == "N":
            pos = [self.position[0] - 1, self.position[1]]
        elif move == "E":
            pos = [self.position[0], self.position[1] + 1]
        elif move == "W":
            pos = [self.position[0], self.position[1] - 1]
        elif move == "S":
            pos = [self.position[0] + 1, self.position[1]]

        return pos

    def check_next_tile(self, position):
        items_in_tile = []
        for key in OBJECT_STATE:
            if key == self.name:
                continue
            grid_item = OBJECT_STATE[key]
            if grid_item.get("position") == position:
                # TODO, items can be in multiple tiles
                items_in_tile.append(grid_item)
        return items_in_tile

    def attack_knight(self, knight):
        print(f"{ self.name } is attacking { knight.name }")

        surprise_attack_score = 0.5
        attack_score = self.attack + surprise_attack_score
        defence_score = knight.defence

        if attack_score > defence_score:
            knight.status = knight.DEAD
            knight.update_item(knight.position)
            knight.item = None
            knight.save_state()
        else:
            self.status = self.DEAD
            self.update_item(self.position)
            self.item = None
            self.save_state()
        print(
            f"ATTACKER { self.name } { self.status } DEFENDER { knight.name } - { knight.status }"
        )

    def update_pos(self, move):
        if self.status in [self.DROWNED, self.DEAD]:
            return

        prev_pos = self.position
        next_pos = self._get_next_position(move)
        next_tile_item = self.check_next_tile(next_pos)

        # alive_knight = (
        #     next_tile_item
        #     and next_tile_item.get("type") == "Knight"
        #     and next_tile_item.get("status") not in [self.DEAD, self.DROWNED]
        # )
        next_tile_knights = [i for i in next_tile_item if i.get("type") == "Knight"]

        alive_knight = next_tile_knights and next_tile_knights[0].get("status") not in [
            self.DEAD,
            self.DROWNED,
        ]

        item_to_pick = None
        tile_items = [item.get("name") for item in next_tile_item]
        # Determine item inheritance
        if "axe" in tile_items:
            item_to_pick = [
                item for item in next_tile_item if item.get("name") == "axe"
            ][0]
        elif "magic_staff" in tile_items:
            item_to_pick = [
                item for item in next_tile_item if item.get("name") == "magic_staff"
            ][0]
        elif "dagger" in tile_items:
            item_to_pick = [
                item for item in next_tile_item if item.get("name") == "dagger"
            ][0]
        elif "helmet" in tile_items:
            item_to_pick = [
                item for item in next_tile_item if item.get("name") == "helmet"
            ][0]

        can_pickup_item = (
            not self.item and item_to_pick and item_to_pick.get("type") == "Item"
        )

        if can_pickup_item:
            item_to_pick.pop("type")
            item = Item(**item_to_pick)
            self.pickup_item(item)
            item.position = self.position
            item.save_state()
        if alive_knight:
            next_tile_knights[0].pop("type")
            knight = Knight(**next_tile_knights[0])
            self.attack_knight(knight)

        self.position = next_pos

        # keep item the same position as Knight
        if self.item:
            self.update_item(self.position)

        if any([pos >= GRID_SIZE or pos < 0 for pos in self.position]):
            print(f"{ self.name } DROWNED")
            self.status = self.DROWNED
            self.position = None

            # Drop item if knight has drowned
            if self.item:
                print(f"{ self.name } DROPPED ITEM { self.item }")
                self.update_item(prev_pos)

        self.save_state()

    def get_item_from_state(self):
        if self.item:
            item_dict = OBJECT_STATE[self.item]
            item_dict.pop("type")
            item = Item(**item_dict)
            return item

    def update_item(self, pos):
        if self.item:
            item = self.get_item_from_state()
            item.position = pos
            item.save_state()

    def update_attack(self, amount):
        self.attack += amount

    def update_defence(self, amount):
        self.defence += amount

    def update_status(self, status):
        self.status = status

    def pickup_item(self, item):
        print(f"{ self.name} picked up item { item.name }")
        self.item = item.name
        self.update_attack(item.attack_modifier)
        self.update_defence(item.defence_modifier)


def visualize_grid(row, column):
    grid = []
    for i in range(row):
        grid.append(i)
        grid[i] = []
        for j in range(column):
            grid[i].append("_")
            for obj in OBJECT_STATE:
                item = OBJECT_STATE[obj]
                if item.get("position") == [i, j]:
                    grid[i][j] += item.get("name")[0]

    # print grid
    for row in grid:
        print(row)

    return grid


def read_file():
    with open("moves.txt", "r+") as file:
        return file.readlines()


def finalize():
    with open("final_state.json", "w") as file:
        final = {}
        for res in OBJECT_STATE:
            obj = OBJECT_STATE[res]
            type = obj.get("type")
            position = obj.get("position")
            status = obj.get("status")
            item = obj.get("item")
            attack = obj.get("attack")
            defence = obj.get("defence")
            if type == "Knight":
                final[res] = [position, status, item, attack, defence]
            elif type == "Item":
                item_equipped = any(
                    [
                        True if v.get("item") == res else False
                        for k, v in OBJECT_STATE.items()
                    ]
                )

                final[res] = [position, item_equipped]
        file.write(json.dumps(final))


GRID_SIZE = 8


def __main__():
    red = Knight("red", [0, 0])
    blue = Knight("blue", [7, 0])
    green = Knight("green", [7, 7])
    yellow = Knight("yellow", [0, 7])
    axe = Item("axe", [2, 2], 2, 0)
    dagger = Item("dagger", [2, 5], 1, 0)
    helmet = Item("helmet", [5, 5], 0, 1)
    magic_staff = Item("magic_staff", [5, 2], 1, 1)

    lines = read_file()
    for line in lines:
        if "GAME-START" in line:
            continue
        elif "GAME-END" in line:
            visualize_grid(GRID_SIZE, GRID_SIZE)
            finalize()
            break
        else:
            color, move = line.strip().split(":")
            knight = None
            knight_name = ""
            if color == "R":
                knight_name = "red"
            elif color == "B":
                knight_name = "blue"
            elif color == "G":
                knight_name = "green"
            elif color == "Y":
                knight_name = "yellow"

            knight_state = OBJECT_STATE[knight_name]
            knight_state.pop("type")
            knight = Knight(**knight_state)

            if knight.status == "LIVE":
                knight.update_pos(move)
            else:
                print(f"Knight { knight.name } is not alive, invalid move")


__main__()

print(OBJECT_STATE)
