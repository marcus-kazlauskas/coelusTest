import polyomino as pm


if __name__ == '__main__':
    # m = tuple(map(int, input('Введите ширину и высоту стола в виде пары целых чисел: ').split()))
    # так как способ ввода данных не указан, то я их буду брать из кода
    data = [(3, 5), [((2, 2), 1)], [((3, 2), 1), ((2, 2), 2)]]
    pavement = pm.Pavement(data)
    pavement.answer()

