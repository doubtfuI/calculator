import re
from datetime import datetime
from decimal import Decimal, InvalidOperation
from typing import List, Tuple

import pandas as pd
from calculator import CostCalculator


def time_serialize(time_str: str):
    nums = time_str.split("/")
    year = int(nums[0])
    month = int(nums[1])
    day = int(nums[2])
    return datetime(year=year, month=month, day=day)


class AutoNameHandler:
    """
    用于将 excel 中文字信息转换为接口可以识别的信息
    """

    class Type:
        EMPLOYEE = "epy"
        SPOUSE = "sps"
        CHILD = "chd"

    @staticmethod
    def contains(target_str: str, pattern: str) -> bool:
        if target_str is None:
            return False

        if re.search(rf".*?{pattern}.*?", target_str) is not None:
            return True

        return False

    def handle(self, auto_name: str) -> Tuple[str, int]:
        if self.contains(auto_name, "子女"):
            type_ = self.Type.CHILD

            if self.contains(auto_name, "医疗"):
                # 子女医疗名称单独处理
                if self.contains(auto_name, "同员工基础"):
                    level = 2

                elif self.contains(auto_name, "基础"):
                    level = 1

                elif self.contains(auto_name, "同员工加强"):
                    level = 3

                elif self.contains(auto_name, "同员工比强更强"):
                    level = 4

                elif self.contains(auto_name, "同员工VIP"):
                    level = 5

                else:
                    level = None

                return type_, level
        elif self.contains(auto_name, "员工"):
            type_ = self.Type.EMPLOYEE

        elif self.contains(auto_name, "配偶"):
            type_ = self.Type.SPOUSE

        else:
            type_ = None

        if self.contains(auto_name, "医疗"):
            # 医疗名称单独处理
            if self.contains(auto_name, "基础"):
                level = 1

            elif self.contains(auto_name, "加强"):
                level = 3

            elif self.contains(auto_name, "比强更强"):
                level = 4

            elif self.contains(auto_name, "VIP"):
                level = 5

            else:
                level = None

            return type_, level

        if self.contains(auto_name, "基础"):
            level = 1

        elif self.contains(auto_name, "加强"):
            level = 2

        elif self.contains(auto_name, "VIP"):
            level = 3

        else:
            level = None

        return type_, level


class AutoMapHandler:
    """
    用于从 auto 表中读取所有 auto_code 与名称对应关系
    """

    def __init__(self):
        auto_code = "组合计划"
        auto_name = "组合计划名称"
        auto_tl = "定寿"
        auto_add = "意外"
        auto_akdd = "重疾"
        auto_wmp = "医疗"
        auto_pca = "交通意外"
        auto_hi = "住院津贴"

        self.auto_map = {}
        df = pd.read_excel("auto.xlsx", header=0, sheet_name="Sheet2")
        row_num = df.shape[0]

        for r in range(row_num):
            self.auto_map[df[auto_code][r]] = {
                "name": self.none_handler(df[auto_name][r]),
                "tl": self.none_handler(df[auto_tl][r]),
                "add": self.none_handler(df[auto_add][r]),
                "akdd": self.none_handler(df[auto_akdd][r]),
                "wmp": self.none_handler(df[auto_wmp][r]),
                "pca": self.none_handler(df[auto_pca][r]),
                "hi": self.none_handler(df[auto_hi][r]),
            }

    @staticmethod
    def none_handler(target):
        if target == " ":
            return None

        if pd.isnull(target):
            return None

        return target

    def get_auto_name(self, auto_code):
        return self.auto_map.get(
            auto_code,
            {
                "name": None,
                "tl": None,
                "add": None,
                "akdd": None,
                "wmp": None,
                "pca": None,
                "hi": None,
            },
        )


class ExcelHandler:
    def __init__(self):
        self.header_from = 1
        self.header_to = 2
        self.excel_path = "sample1.xlsx"

        self.start = "生效日期"
        self.stop = "终止日期"
        self.salary = "工资"
        self.auto_code = "计划"

        self.pca_amount = "PCA_B保额"
        self.pca_cost = "保费"
        self.add_amount = "ADD_B保额"
        self.add_cost = "保费.1"
        self.wmp_amount = "WMP-HL1保额"
        self.wmp_cost = "保费.2"
        self.tl_amount = "TL保额"
        self.tl_cost = "保费.5"
        self.hi_amount = "HI保额"
        self.hi_cost = "保费.6"
        self.akdd_amount = "AKDD保额"
        self.akdd_cost = "AKDD保额"

        headers = self.header_handler(self.header_from, self.header_to)
        # 截掉标题后 index 从 `self.header_to` 开始记
        self.df = pd.read_excel(self.excel_path, header=None, names=headers).loc[
            self.header_to :
        ]

        self.auto_map = AutoMapHandler()
        self.name_handler = AutoNameHandler()

    @staticmethod
    def to_decimal(num_str):
        try:
            return Decimal(num_str)

        except InvalidOperation:
            return Decimal(0)

    def header_handler(self, start: int, end: int) -> List[str]:
        """
        用于将多行索引(mutiindex) 转换为单行索引
        :param start: header 起始行 (从 1 开始
        :param end: header 起始行
        :return:
        """
        # TODO: handle all header
        nrows = end
        df = pd.read_excel(
            self.excel_path, header=None, nrows=nrows, keep_default_na=False
        )
        headers = []

        ncols = df.columns.size
        for c in range(ncols):
            header = []
            for r in range(nrows):
                header.append(df[c][start - 1 + r])

            headers.append("".join(header))

        return headers

    def add_new_col(self, target_col, name, after: bool = False):
        """
        `after = True`: 在 `target_col` 之后插入名为 `name` 的列
        `after = False`: 在 `target_col` 之前插入名为 `name` 的列
        """
        self.df[name] = ""
        cols = list(self.df)

        try:
            i = cols.index(target_col)
        except ValueError:
            raise ValueError(f"Can't find {target_col}, choices are {cols}")

        index = i if not after else i + 1

        cols.pop()
        cols.insert(index, name)
        self.df = self.df.loc[:, cols]
        return

    def handle_excel(
        self,
    ):
        row_start = self.header_to

        row_num = self.df.shape[0]
        ncols = self.df.columns.size

        # 插入空白列
        self.add_new_col(self.pca_amount, "PCA_type")
        self.add_new_col(self.add_amount, "ADD_type")
        self.add_new_col(self.wmp_amount, "WMP_type")
        self.add_new_col(self.tl_amount, "TL_type")
        self.add_new_col(self.hi_amount, "HI_type")
        self.add_new_col(self.hi_amount, "AKDD_type")

        for pre, tar in (
            ("PCA", self.pca_cost),
            ("ADD", self.add_cost),
            ("WMP", self.wmp_cost),
            ("TL", self.tl_cost),
            ("HI", self.hi_cost),
            ("AKDD", self.akdd_cost),
        ):
            for c in ("emy_formula", "for_emy", "com_formula", "for_com"):
                name = f"{pre}_{c}"
                self.add_new_col(tar, name, after=True)

        for r in range(row_start, row_start + row_num):
            print(f"name: {self.df['客户姓名'][r]}")
            start = self.df[self.start][r]
            stop = self.df[self.stop][r]
            salary = self.df[self.salary][r]
            salary_de = self.to_decimal(salary)
            auto_code = self.df[self.auto_code][r]

            pca_amount = self.df[self.pca_amount][r]
            pca_cost = self.df[self.pca_cost][r]
            add_amount = self.df[self.add_amount][r]
            add_cost = self.df[self.add_cost][r]
            wmp_amount = self.df[self.wmp_amount][r]
            wmp_cost = self.df[self.wmp_cost][r]
            tl_amount = self.df[self.tl_amount][r]
            tl_cost = self.df[self.tl_cost][r]
            hi_amount = self.df[self.hi_amount][r]
            hi_cost = self.df[self.hi_cost][r]
            akdd_amount = self.df[self.akdd_amount][r]
            akdd_cost = self.df[self.akdd_cost][r]

            pca_cost_de = self.to_decimal(pca_cost)
            hi_cost_de = self.to_decimal(hi_cost)

            active_days = (time_serialize(stop) - time_serialize(start)).days
            active_days_de = self.to_decimal(active_days)

            # 通过 auto_code 填入名称
            auto_name_dict = self.auto_map.get_auto_name(auto_code)
            self.df["PCA_type"][r] = auto_name_dict["pca"]
            self.df["ADD_type"][r] = auto_name_dict["add"]
            self.df["WMP_type"][r] = auto_name_dict["wmp"]
            self.df["TL_type"][r] = auto_name_dict["tl"]
            self.df["HI_type"][r] = auto_name_dict["hi"]
            self.df["AKDD_type"][r] = auto_name_dict["akdd"]

            # 计算
            c = CostCalculator(active_days=active_days, days_of_year=365 - 31)

            salary_list = [(salary_de, active_days_de)]

            add_type, add_level = self.name_handler.handle(auto_name_dict["add"])
            wmp_type, wmp_level = self.name_handler.handle(auto_name_dict["wmp"])
            tl_type, tl_level = self.name_handler.handle(auto_name_dict["tl"])
            _, akdd_level = self.name_handler.handle(auto_name_dict["hi"])

            pca_data = c.cal_pca(pca_cost_de)
            add_data = c.cal_add(add_type, add_level, salary_list)
            wmp_data = c.cal_wmp(wmp_type, wmp_level)
            tl_data = c.cal_tl(tl_type, tl_level, salary_list)
            hi_data = c.cal_hi(hi_cost_de)
            akdd_data = c.cal_akdd(akdd_level)

            # 填入计算结果
            for pre, data in (
                ("PCA", pca_data),
                ("ADD", add_data),
                ("WMP", wmp_data),
                ("TL", tl_data),
                ("HI", hi_data),
                ("AKDD", akdd_data),
            ):
                self.df[f"{pre}_for_com"][r] = data["for_company"]["result"]
                self.df[f"{pre}_com_formula"][r] = data["for_company"]["formula"]
                self.df[f"{pre}_for_emy"][r] = data["for_employee"]["result"]
                self.df[f"{pre}_emy_formula"][r] = data["for_employee"]["formula"]

        self.df.to_excel("new.xlsx")
