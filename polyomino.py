import numpy as np
from itertools import chain
from typing import Union
from typing import Generator


def _pop_pm(pm_pl: list[list[Union[tuple[int, int], int]]],
            i: int) -> tuple[tuple[int, int], int, bool]:
    pm_dim = pm_pl[i][0]
    pm_type = pm_pl[i][2]
    if pm_pl[i][1] == 1:
        del pm_pl[i]
        deleted = True
    else:
        pm_pl[i][1] -= 1
        deleted = False
    return pm_dim, pm_type, deleted


def _push_pm(pm_pl: list[list[Union[tuple[int, int], int]]],
             i: int, pm_dim: tuple[int, int], pm_type: int, deleted: bool) -> None:
    if deleted:
        pm_pl.insert(i, [pm_dim, 1, pm_type])
    else:
        pm_pl[i][1] += 1


class Table:
    """
    Класс для описания стола с полиомино, представляющий собой матрицу и позицию для добавления следующего полиомино,
    которая выбирается из свободных клеток (элементы матрицы, равные нулю) слева направо сверху вниз
    """

    def __init__(self, m: Union[tuple[int, int], list[tuple[tuple[int, int], int]]]):
        self.mat = np.zeros((m[1], m[0]), dtype=int)  # матрица стола
        self.point = (0, 0)  # точка добавления следующего полиомино
        self.prev_points = []  # точки добавления предыдущих полиомино для возможности их удаления

    def _check_dim(self, pm_dim: tuple[int, int], pm_type: int,
                   p: tuple[int, int], angle: int) -> bool:
        # проверка попадания полиомино на стол по габаритам
        mat = self.mat
        if angle % 2 == 0:
            if angle % 4 == 2 and pm_type == 2:  # l-полиомино, повёрнутый на pi
                return (p[1] + pm_dim[1] <= mat.shape[0] and
                        p[0] + 1 - pm_dim[0] >= 0)
            else:
                return (p[1] + pm_dim[1] <= mat.shape[0] and
                        p[0] + pm_dim[0] <= mat.shape[1])
        else:
            return (p[1] + pm_dim[0] <= mat.shape[0] and
                    p[0] + pm_dim[1] <= mat.shape[1])

    def _check_shape(self, pm_dim: tuple[int, int], pm_type: int,
                     p: tuple[int, int], angle: int) -> bool:
        # итератор набора клеток стола для проверки возможности добавления на него полиомино
        mat = self.mat
        if pm_type == 1:  # прямоугольный полиомино
            # матрица для проверки прямоугольного полиомино просто прямоугольная
            if angle % 2 == 0:  # поворот на 0 или pi
                m = mat[p[1]:p[1] + pm_dim[1], p[0]:p[0] + pm_dim[0]]
            else:  # поворот на pi / 2 или 3 * pi / 2
                m = mat[p[1]:p[1] + pm_dim[0], p[0]:p[0] + pm_dim[1]]
            cells = m.flat
        else:  # l-полиомино
            # матрица для проверки l-полиомино (4, 3) при angle == 0:
            #      d[0]
            #       |        d - точка добаления полиомино, которая совмещается с точкой p на столе
            #      ---------
            # d[1]-|a a a a| элементы a - a_wing
            #      ---------
            #      |b|0 0 0| элементы b - b_wing
            #      | |     |
            #      |b|0 0 0| элементы 0 - не проверяются
            #      ---------
            #                d == (0, 0), кроме случая angle == 2 (поворот на pi), тогда d == (pm[0] - 1, 0)
            if angle % 2 == 0:
                if angle % 4 == 0:  # поворот на 0
                    a_wing = mat[p[1], p[0]:p[0] + pm_dim[0]]
                    b_wing = mat[p[1] + 1:p[1] + pm_dim[1], p[0]]
                else:  # поворот на pi
                    a_wing = mat[p[1] + pm_dim[1] - 1, p[0] - pm_dim[0] + 1:p[0] + 1]
                    b_wing = mat[p[1]:p[1] + pm_dim[1] - 1, p[0]]
            else:
                if angle % 4 == 1:  # поворот на pi / 2
                    a_wing = mat[p[1]:p[1] + pm_dim[0], p[0]]
                    b_wing = mat[p[1] + pm_dim[0] - 1, p[0] + 1:p[0] + pm_dim[1]]
                else:  # поворот на 3 * pi / 2
                    a_wing = mat[p[1]:p[1] + pm_dim[0], p[0] + pm_dim[1] - 1]
                    b_wing = mat[p[1], p[0]:p[0] + pm_dim[1] - 1]
            cells = chain(a_wing.flat, b_wing.flat)
        for cell in cells:
            if cell > 0:
                return False
        return True

    def _add_pm(self, pm_dim: tuple[int, int], pm_type: int,
                p: tuple[int, int], angle: int, num: int, sign: int) -> None:
        # добавление очередного полиомино на стол
        mat = self.mat
        if pm_type == 1:  # прямоугольный полиомино
            # матрица для добавления прямоугольного полиомино просто прямоугольная
            if angle % 2 == 0:  # поворот на 0 или pi
                pm_mat = np.full((pm_dim[1], pm_dim[0]), num * sign, dtype=int)
                mat[p[1]:p[1] + pm_dim[1], p[0]:p[0] + pm_dim[0]] += pm_mat
            else:  # поворот на pi / 2 или 3 * pi / 2
                pm_mat = np.full((pm_dim[0], pm_dim[1]), num * sign, dtype=int)
                mat[p[1]:p[1] + pm_dim[0], p[0]:p[0] + pm_dim[1]] += pm_mat
        else:  # l-полиомино
            # матрица для добавления l-полиомино (4, 3) при angle == 0:
            #      d[0]
            #       |        d - точка добавления полиомино, которая совмещается с точкой p на столе
            #      ---------
            # d[1]-|a a a a| элементы a - a_wing
            #      ---------
            #      |b|0 0 0| элементы b - b_wing
            #      | |     |
            #      |b|0 0 0| элементы 0 - void
            #      ---------
            #                d == (0, 0), кроме случая angle == 2 (поворот на pi), тогда d == (pm[0] - 1, 0)
            if angle % 2 == 0:
                a_wing = np.full((1, pm_dim[0]), num * sign, dtype=int)
                b_wing = np.full((pm_dim[1] - 1, 1), num * sign, dtype=int)
                void = np.zeros((pm_dim[1] - 1, pm_dim[0] - 1), dtype=int)
                if angle % 4 == 0:  # поворот на 0
                    pm_mat = np.concatenate((b_wing, void), axis=1)
                    pm_mat = np.concatenate((a_wing, pm_mat), axis=0)
                    mat[p[1]:p[1] + pm_dim[1], p[0]:p[0] + pm_dim[0]] += pm_mat
                else:  # поворот на pi
                    pm_mat = np.concatenate((void, b_wing), axis=1)
                    pm_mat = np.concatenate((pm_mat, a_wing), axis=0)
                    mat[p[1]:p[1] + pm_dim[1], p[0] + 1 - pm_dim[0]:p[0] + 1] += pm_mat
            else:
                a_wing = np.full((pm_dim[0], 1), num * sign, dtype=int)
                b_wing = np.full((1, pm_dim[1] - 1), num * sign, dtype=int)
                void = np.zeros((pm_dim[0] - 1, pm_dim[1] - 1), dtype=int)
                if angle % 4 == 1:  # поворот на pi / 2
                    pm_mat = np.concatenate((void, b_wing), axis=0)
                    pm_mat = np.concatenate((a_wing, pm_mat), axis=1)
                    mat[p[1]:p[1] + pm_dim[0], p[0]:p[0] + pm_dim[1]] += pm_mat
                else:  # поворот на 3 * pi / 2
                    pm_mat = np.concatenate((b_wing, void), axis=0)
                    pm_mat = np.concatenate((pm_mat, a_wing), axis=1)
                    mat[p[1]:p[1] + pm_dim[0], p[0]:p[0] + pm_dim[1]] += pm_mat

    def _free_points(self) -> Generator[tuple[int, int], None, None]:
        # генератор следующей точки добавления полиомино
        p = self.point
        mat = self.mat
        for i in range(p[1], mat.shape[0]):
            if i == p[1]:
                row = range(p[0], mat.shape[1])
            else:
                row = range(mat.shape[1])
            for j in row:
                if mat[i, j] == 0:
                    yield j, i

    def place_pm(self, pm_pl: list[list[Union[tuple[int, int], int]]], num: int) -> bool:
        # рекурсивное расположение набора полиомино на столе
        if len(pm_pl) == 0:
            return True  # первая подходящая конфигурация полиомино найдена, выход из рекурсии
        for point in self._free_points():  # проход слева направо сверху вниз по всем свободным клеткам
            for i in range(len(pm_pl)):
                pm_dim, pm_type, deleted = _pop_pm(pm_pl, i)  # выбор текущего полиомино из оставшегося набора
                if pm_type == 1:
                    angles = range(2)  # для прямоугольного полиомино 2 различных угла поворота
                else:
                    angles = range(4)  # для l-полиомино 4 различных угла поворота
                for angle in angles:
                    if (self._check_dim(pm_dim, pm_type, point, angle) and
                            self._check_shape(pm_dim, pm_type, point, angle)):
                        self._add_pm(pm_dim, pm_type, point, angle, num, 1)
                        self.prev_points.append(self.point)
                        self.point = point
                        if self.place_pm(pm_pl, num + 1):
                            return True  # первая подходящая конфигурация полиомино найдена
                        self._add_pm(pm_dim, pm_type, point, angle, num, -1)
                        self.point = self.prev_points.pop()
                _push_pm(pm_pl, i, pm_dim, pm_type, deleted)
        return False  # нельзя добавить очередное полиомино при данном заполнении из предыдущих


class Pavement:
    """
    Класс для проверки замощения стола table множеством полиомино pm_pl
    """

    def __init__(self, data: list[Union[tuple[int, int], list[tuple[tuple[int, int], int]]]]):
        m = data[0]  # размер стола
        s = ([(s1, s2), n, 1] for (s1, s2), n in data[1])  # генератор данных прямоугольных полиомино
        q = ([(q1, q2), n, 2] for (q1, q2), n in data[2])  # генератор данных l-полиомино
        self.table = Table(m)  # стол для мощения
        self.pm_pl = [*s, *q]  # polyomino plurality в виде общего списка

    def probe(self) -> bool:
        # простейшая проверка возможности замощения стола путём подсчёта общей площади полиомино
        sum_sqr = 0
        for pm in self.pm_pl:
            if pm[2] == 1:
                sum_sqr += np.prod(pm[0], dtype=int) * pm[1]
            else:
                sum_sqr += (sum(pm[0]) - 1) * pm[1]
        return sum_sqr <= self.table.mat.size

    def find(self) -> bool:
        # поиск замощения table множеством pm_pl
        return self.table.place_pm(self.pm_pl, 1)

    def answer(self) -> None:
        # решение задачи и печать ответа
        if self.probe() and self.find():
            print('Правда')
            print(self.table.mat)
            # print(*self.table.prev_points, self.table.point)
        else:
            print('Неправда')
            raise SystemExit
