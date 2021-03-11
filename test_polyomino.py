import unittest
import polyomino as pm


class TestPolyomino(unittest.TestCase):
    """
    Класс для тестов поиска замощения стола набором полиомино, то есть для тестов Pavement
    """
    # изначально тут ещё были тесты класса Table, но после переписывания программы они стали неактуальными,
    # и я их удалил
    def setUp(self) -> None:
        pass

    def test_1(self):
        data = [(3, 5), [((2, 2), 1)], [((3, 2), 1), ((2, 2), 2)]]
        print('1. Замощение стола в случае, если это возможно и при этом останутся пустоты:')
        pavement = pm.Pavement(data)
        pavement.answer()

    def test_2(self):
        data = [(5, 5), [((3, 3), 1)], [((3, 3), 2), ((2, 2), 2)]]
        print('2. Замощение стола в случае, если это возможно и при этом не останется пустот:')
        pavement = pm.Pavement(data)
        pavement.answer()

    def test_3(self):
        data = [(5, 5), [((3, 3), 1)], [((3, 3), 1), ((2, 3), 2), ((2, 2), 1)]]
        print('3. Замощение стола в случае, если это возможно и при этом не останется пустот:')
        pavement = pm.Pavement(data)
        pavement.answer()

    def test_4(self):
        data = [(5, 5), [((3, 3), 1)], [((3, 3), 1), ((3, 2), 1), ((2, 3), 1), ((2, 2), 1)]]
        print('4. Замощение стола в случае, если это (не)возможно, но площадь стола и всех полиомино совпадают:')
        pavement = pm.Pavement(data)
        pavement.answer()

    def test_5(self):
        data = [(3, 3), [((1, 1), 1)], [((3, 2), 1), ((2, 3), 1)]]
        print('5. Замощение стола в случае, если это невозможно, но площадь стола и всех полиомино совпадают:')
        pavement = pm.Pavement(data)
        try:
            pavement.answer()
        except SystemExit:
            pass


if __name__ == '__main__':
    unittest.main()
