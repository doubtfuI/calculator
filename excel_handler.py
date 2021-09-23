import pandas as pd

from typing import List, Tuple


def header_handler(start: int, end: int) -> List[str]:
    """
    :param start: header 起始行 (从 1 开始
    :param end: header 起始行
    :return:
    """
    nrows = end
    df = pd.read_excel("sample1.xlsx", header=None, nrows=nrows, keep_default_na=False)
    headers = []

    ncols = df.columns.size
    for c in range(ncols):
        header = []
        for r in range(nrows):
            header.append(df[c][start - 1 + r])
            # if c > 38:
            #     print(df[c][start - 1 + r])

        headers.append("".join(header))

    return headers


def read_excel():
    row_start = 2

    headers = header_handler(1, 2)

    df = pd.read_excel("sample1.xlsx", header=None, names=headers)

    print(df.columns)

    nrows = df.shape[0]
    ncols = df.columns.size

    for r in range(row_start, nrows):
        name = df["客户姓名"][r]
        print(name)
        start = df["生效日期"][r]
        print(start, type(start))


def main():
    # header_handler(1, 2)
    read_excel()


main()
