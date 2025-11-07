import random


class HanoiTower:
    def __init__(self, disks, pegs):
        self.disks = min(disks, 1000)
        self.pegs = min(pegs, 1000)
        self.towers = [[] for _ in range(self.pegs)]

        all_disks = list(range(1, self.disks + 1))
        random.shuffle(all_disks)

        for disk in all_disks:
            random_peg = random.randint(0, self.pegs - 1)
            self.towers[random_peg].append(disk)

        for tower in self.towers:
            tower.sort(reverse=True)

        self.moves = 0
        self.hint_mode = False

    def display(self):
        print("\n" * 50)
        print(f"Ходы: {self.moves}")
        if self.hint_mode:
            print("*** РЕЖИМ ПОДСКАЗКИ ***")
        print("Штыри: ", end="")
        for i in range(self.pegs):
            print(f"{i + 1} ", end="")
        print()

        for i in range(max(len(tower) for tower in self.towers), 0, -1):
            for tower in self.towers:
                if len(tower) >= i:
                    if self.hint_mode and i == len(tower):
                        print(f" *{tower[i - 1]:1}*", end=" ")
                    else:
                        print(f"[{tower[i - 1]:2}]", end=" ")
                else:
                    print(" |  ", end=" ")
            print()
        print("-" * (self.pegs * 6))

    def move_disk(self, from_peg, to_peg):
        if not self.towers[from_peg]:
            return False

        if self.towers[to_peg] and self.towers[from_peg][-1] > self.towers[to_peg][-1]:
            return False

        disk = self.towers[from_peg].pop()
        self.towers[to_peg].append(disk)
        self.moves += 1
        return True

    def is_win(self):
        for tower in self.towers:
            if len(tower) == self.disks:
                return True
        return False

    def get_possible_moves(self):
        moves = []
        for from_peg in range(self.pegs):
            for to_peg in range(self.pegs):
                if from_peg != to_peg and self.towers[from_peg]:
                    if not self.towers[to_peg] or self.towers[from_peg][-1] < self.towers[to_peg][-1]:
                        moves.append((from_peg, to_peg))
        return moves

    def solve_recursive(self, target_peg=None, depth=0):
        if self.is_win():
            return True

        if depth > self.disks * 2:
            return False

        if target_peg is None:
            target_peg = self.pegs - 1

        possible_moves = self.get_possible_moves()

        for from_peg, to_peg in possible_moves:
            disk = self.towers[from_peg][-1]

            self.towers[from_peg].pop()
            self.towers[to_peg].append(disk)
            self.moves += 1

            self.display()
            print(f"Автоход: {from_peg + 1} -> {to_peg + 1} (диск {disk})")
            print(f"Глубина поиска: {depth}")
            input("Нажмите Enter для следующего хода...")

            if self.solve_recursive(target_peg, depth + 1):
                return True

            self.towers[to_peg].pop()
            self.towers[from_peg].append(disk)
            self.moves += 1

        return False


def get_input(prompt, min_val=3, max_val=1000):
    while True:
        try:
            value = int(input(prompt))
            if min_val <= value <= max_val:
                return value
            else:
                print(f"Введите число от {min_val} до {max_val}")
        except ValueError:
            print("Введите число!")


def play_game():
    disks = get_input("Количество дисков (3-1000): ", 3, 1000)
    pegs = get_input("Количество штырей (3-1000): ", 3, 1000)

    game = HanoiTower(disks, pegs)

    while True:
        game.display()

        if game.is_win():
            print("Победа!")
            break

        print("\nКоманды:")
        print("1-9 - номера штырей")
        print("h - подсказка")
        print("s - сдаться (авторешение)")
        print("q - выход")

        command = input("Введите команду: ").lower()

        if command == 'q':
            break
        elif command == 'h':
            game.hint_mode = not game.hint_mode
            print("Режим подсказки", "включен" if game.hint_mode else "выключен")
            input("Нажмите Enter чтобы продолжить...")
        elif command == 's':
            print("Начинаем авторешение...")
            input("Нажмите Enter чтобы продолжить...")
            game.solve_recursive()
            if game.is_win():
                print("Головоломка решена!")
                break
        else:
            try:
                from_peg = int(command) - 1
                to_peg = int(input(f"Куда (1-{game.pegs}): ")) - 1

                if from_peg < 0 or from_peg >= game.pegs or to_peg < 0 or to_peg >= game.pegs:
                    print("Неверный номер штыря!")
                    input("Нажмите Enter чтобы продолжить...")
                    continue

                if not game.move_disk(from_peg, to_peg):
                    print("Неверный ход! На меньший диск нельзя класть больший")
                    input("Нажмите Enter чтобы продолжить...")

            except ValueError:
                print("Неверная команда!")
                input("Нажмите Enter чтобы продолжить...")


play_game()
