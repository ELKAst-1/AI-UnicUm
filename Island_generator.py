import random
from typing import List, Tuple, Set
from collections import deque


class IslandGenerator:
    def __init__(self, max_land: int):
        self.width = 20
        self.height = 20
        self.max_land = max_land
        self.matrix = [['〰' for _ in range(20)] for _ in range(20)]
        self.land_cells = set()
        self.treasure_pos = None
        self.player_start = None

    def generate_island(self) -> List[List[str]]:
        self._create_lands()
        self._add_treasure()
        self._place_player()
        return self.matrix

    def _create_lands(self):
        num_islands = random.randint(2, 10)

        for _ in range(num_islands):
            if len(self.land_cells) >= self.max_land:
                break

            start_x = random.randint(2, 17)
            start_y = random.randint(2, 17)

            if (start_x, start_y) not in self.land_cells:
                island_size = random.randint(10, min(20, self.max_land - len(self.land_cells)))
                self._grow_island(start_x, start_y, island_size)

    def _grow_island(self, start_x: int, start_y: int, target_size: int):
        queue = [(start_x, start_y)]
        self.land_cells.add((start_x, start_y))
        self.matrix[start_y][start_x] = '▨'

        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        current_size = 1

        while queue and current_size < target_size:
            x, y = queue.pop(0)

            random.shuffle(directions)
            for dx, dy in directions:
                if current_size >= target_size:
                    break

                nx, ny = x + dx, y + dy

                if (2 <= nx < 18 and 2 <= ny < 18 and
                        (nx, ny) not in self.land_cells and
                        random.random() < 0.6):
                    self.land_cells.add((nx, ny))
                    self.matrix[ny][nx] = '▨'
                    queue.append((nx, ny))
                    current_size += 1

    def _add_treasure(self):
        safe_cells = []

        for x in range(2, 18):
            for y in range(2, 18):
                if (x, y) in self.land_cells and self.matrix[y][x] == '▨':
                    if self._is_land_around(x, y):
                        safe_cells.append((x, y))

        if safe_cells:
            self.treasure_pos = random.choice(safe_cells)
            treasure_x, treasure_y = self.treasure_pos
            self.matrix[treasure_y][treasure_x] = '⨉'

    def _is_land_around(self, x: int, y: int) -> bool:
        directions = [
            (-1, -1), (0, -1), (1, -1),
            (-1, 0), (1, 0),
            (-1, 1), (0, 1), (1, 1)
        ]

        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if not (0 <= nx < 20 and 0 <= ny < 20):
                return False
            if self.matrix[ny][nx] != '▨':
                return False

        return True

    def _place_player(self):
        available_cells = [(x, y) for x, y in self.land_cells 
                          if self.matrix[y][x] == '▨']
        
        if available_cells:
            self.player_start = random.choice(available_cells)
            start_x, start_y = self.player_start
            self.matrix[start_y][start_x] = '*'

    def find_shortest_path(self) -> Tuple[List[List[str]], int]:
        if not self.player_start or not self.treasure_pos:
            return self.matrix, -1

        path_matrix = [row[:] for row in self.matrix]
        
        queue = deque([(self.player_start[0], self.player_start[1], 0, [])])
        visited = set()
        visited.add(self.player_start)

        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]

        while queue:
            x, y, cost, path = queue.popleft()

            if (x, y) == self.treasure_pos:
                for px, py in path:
                    if (px, py) != self.player_start and (px, py) != self.treasure_pos:
                        path_matrix[py][px] = '+'
                
                total_cost = cost
                return path_matrix, total_cost

            for dx, dy in directions:
                nx, ny = x + dx, y + dy
                
                if 0 <= nx < 20 and 0 <= ny < 20:
                    if (nx, ny) not in visited:
                        cell_cost = -2 if self.matrix[ny][nx] == '〰' else -1
                        
                        if self.matrix[ny][nx] in ['▨', '〰', '⨉']:
                            new_path = path + [(x, y)]
                            queue.append((nx, ny, cost + cell_cost, new_path))
                            visited.add((nx, ny))

        return path_matrix, -1

    def print_map(self):
        print("\nКарта островов (20x20):")
        print("=" * 43)

        for row in self.matrix:
            print(''.join(row))

        print("=" * 43)
        print("〰 - вода, ▨ - суша, ⨉ - клад, * - игрок")

    def print_path_map(self, path_matrix: List[List[str]], cost: int):
        print(f"\nКарта с кратчайшим путем (стоимость: {cost} баллов):")
        print("=" * 43)

        for row in path_matrix:
            print(''.join(row))

        print("=" * 43)
        print("〰 - вода, ▨ - суша, ⨉ - клад, * - начало, + - путь")


def main():
    print("Генератор островов 20x20")
    print("========================")

    try:
        max_land = int(input("Введите максимальное количество суши(лучше не меньше 100): "))

        generator = IslandGenerator(max_land)
        island_map = generator.generate_island()
        generator.print_map()

        path_matrix, cost = generator.find_shortest_path()
        
        if cost != -1:
            generator.print_path_map(path_matrix, cost)
            print(f"\nРезультат:")
            print(f"- Игрок начинал в позиции: {generator.player_start}")
            print(f"- Клад находится в позиции: {generator.treasure_pos}")
            print(f"- Стоимость кратчайшего пути: {cost} баллов")
            print(f"- Путь отмечен символами '+' на карте")
        else:
            print("\nПуть от игрока до клада не найден!")

    except ValueError:
        print("Ошибка: попробуйте еще разок (c другим числом) 🥲")
    except Exception as e:
        print(f"Произошла ошибка: {e}")


if __name__ == "__main__":
    main()
