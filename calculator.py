from decimal import Decimal, getcontext
from typing import List


class CostCalculator:
    """
    计算器
    active_days: 实际缴纳天数
    days_of_year: 费率对应天数
    """

    class Type:
        EMPLOYEE = "epy"
        SPOUSE = "sps"
        CHILD = "chd"

    def __init__(
        self,
        active_days: int,
        days_of_year: int = 365,
    ):

    @staticmethod
    def handle_result(res: Decimal):
        if res == Decimal(0):
            return "0"

        getcontext().rounding = "ROUND_HALF_UP"
        return res.quantize(Decimal("0.00"))

    def cal_pca(self, cost: Decimal, re_cal: bool = False):
        """
        全部员工缴纳
        :param cost: 保费
        :param re_cal: 重新计算保费 (不使用表格中的保费)
        :return:
        """
        # TODO: finish re_call
        if re_cal:
            return {
                "for_company": {
                    "result": 0,
                    "formula": "0",
                },
                "for_employee": {
                    "result": self.handle_result(
                        (self.pca_amount * self.pca_epy_rate)
                        / self.days_of_year
                        * self.active_days
                    ),
                    "formula": f"({self.pca_amount} * {self.pca_epy_rate}) / {self.days_of_year} * {self.active_days}",
                },
            }

        return {
            "for_company": {
                "result": 0,
                "formula": "0",
            },
            "for_employee": {
                "result": cost,
                "formula": f"{cost}",
            },
        }

    def cal_add(self, type_: str, level: int, salary_list: List[tuple]):
        """
        公司缴纳员工的基础倍率
        员工超出倍率员工缴纳
        配偶及子女部分全部由员工缴纳
        salary_list: [(`salary`, `day`), ...]
        :return:
        """
        mag = self.add_mag.get(level)
        if mag is None:
            # raise KeyError(f"add_mag type: {type_}, level: {level} got None")
            return {
                "for_company": {
                    "result": 0,
                    "formula": "0",
                },
                "for_employee": {
                    "result": 0,
                    "formula": "0",
                },
            }

        salary_tmp = 0
        for salary, day in salary_list:
            salary_tmp += salary * day

        if type_ == self.Type.EMPLOYEE:
            return {
                "for_company": {
                    "result": self.handle_result(
                        self.add_basic_mag
                        * self.add_rate
                        / self.days_of_year
                        * salary_tmp
                    ),
                    "formula": f"({self.add_basic_mag} * {self.add_rate}) / {self.days_of_year} * ({' + '.join([f'{s} * {d}' for s, d in salary_list])})",
                },
                "for_employee": {
                    "result": self.handle_result(
                        (mag - self.add_basic_mag)
                        * self.add_rate
                        / self.days_of_year
                        * salary_tmp
                    ),
                    "formula": f"(({mag} - {self.add_basic_mag}) * {self.add_rate}) / {self.days_of_year} * ({' + '.join([f'{s} * {d}' for s, d in salary_list])})",
                },
            }

        else:
            return {
                "for_company": {
                    "result": 0,
                    "formula": "0",
                },
                "for_employee": {
                    "result": self.handle_result(
                        mag * self.add_rate / self.days_of_year * salary_tmp
                    ),
                    "formula": f"({mag} * {self.add_rate}) / {self.days_of_year} * ({' + '.join([f'{s} * {d}' for s, d in salary_list])})",
                },
            }

    def cal_wmp(self, type_: str, level: int):
        """
        员工及子女基础医疗公司缴纳
        员工及子女超出基础部分员工缴纳
        配偶全部员工缴纳
        :return:
        """

        if type_ == self.Type.EMPLOYEE:
            cost = self.wmp_emy_cost.get(level)
            if cost is not None:
                return {
                    "for_company": {
                        "result": self.handle_result(
                            self.wmp_emy_basic_cost
                            / self.days_of_year
                            * self.active_days
                        ),
                        "formula": f"{self.wmp_emy_basic_cost} / {self.days_of_year} * {self.active_days}",
                    },
                    "for_employee": {
                        "result": self.handle_result(
                            (cost - self.wmp_emy_basic_cost)
                            / self.days_of_year
                            * self.active_days
                        ),
                        "formula": f"({cost} - {self.wmp_emy_basic_cost}) / {self.days_of_year} * {self.active_days}",
                    },
                }

        elif type_ == self.Type.SPOUSE:
            cost = self.wmp_sps_cost.get(level)
            if cost is not None:
                return {
                    "for_company": {
                        "result": 0,
                        "formula": "0",
                    },
                    "for_employee": {
                        "result": self.handle_result(
                            cost / self.days_of_year * self.active_days
                        ),
                        "formula": f"{cost} / {self.days_of_year} * {self.active_days}",
                    },
                }

        elif type_ == self.Type.CHILD:
            cost = self.wmp_chd_cost.get(level)
            if cost is not None:
                return {
                    "for_company": {
                        "result": self.handle_result(
                            self.wmp_chd_basic_cost
                            / self.days_of_year
                            * self.active_days
                        ),
                        "formula": f"{self.wmp_chd_basic_cost} / {self.days_of_year} * {self.active_days}",
                    },
                    "for_employee": {
                        "result": self.handle_result(
                            (cost - self.wmp_chd_basic_cost)
                            / self.days_of_year
                            * self.active_days
                        ),
                        "formula": f"({cost} - {self.wmp_chd_basic_cost}) / {self.days_of_year} * {self.active_days}",
                    },
                }

        # raise KeyError(f"type{type_}, level{level} got None")

        return {
            "for_company": {
                "result": 0,
                "formula": "0",
            },
            "for_employee": {
                "result": 0,
                "formula": "0",
            },
        }

    def cal_tl(self, type_: str, level: int, salary_list: list):
        """
        公司缴纳员工的基础倍率
        员工超出倍率员工缴纳
        配偶及子女部分全部由员工缴纳
        :return:
        """
        mag = self.tl_mag.get(level)
        if mag is None:
            # raise KeyError(f"tl_mag type{type_}, level{level} got None")
            return {
                "for_company": {
                    "result": 0,
                    "formula": "0",
                },
                "for_employee": {
                    "result": 0,
                    "formula": "0",
                },
            }

        salary_tmp = 0
        for salary, day in salary_list:
            salary_tmp += salary * day

        if type_ == self.Type.EMPLOYEE:
            return {
                "for_company": {
                    "result": self.handle_result(
                        (self.tl_basic_mag * self.tl_rate)
                        / self.days_of_year
                        * salary_tmp
                    ),
                    "formula": f"({self.tl_basic_mag} * {self.tl_rate}) / {self.days_of_year} * ({' + '.join([f'{s} * {d}' for s, d in salary_list])})",
                },
                "for_employee": {
                    "result": self.handle_result(
                        (mag - self.tl_basic_mag)
                        * self.tl_rate
                        / self.days_of_year
                        * salary_tmp
                    ),
                    "formula": f"(({mag} - {self.tl_basic_mag}) * {self.tl_rate}) / {self.days_of_year} * ({' + '.join([f'{s} * {d}' for s, d in salary_list])})",
                },
            }

        else:
            return {
                "for_company": {
                    "result": 0,
                    "formula": "0",
                },
                "for_employee": {
                    "result": self.handle_result(
                        mag * self.tl_rate / self.days_of_year * salary_tmp
                    ),
                    "formula": f"({mag} * {self.tl_rate}) / {self.days_of_year} * ({' + '.join([f'{s} * {d}' for s, d in salary_list])})",
                },
            }

    def cal_hi(self, cost: Decimal, re_cal: bool = False):
        """
        全部公司缴纳
        :param cost: 保费
        :param re_cal: 重新计算保费 (不使用表格中的保费)
        :return:
        """
        if re_cal:
            return {
                "for_company": {
                    "result": self.handle_result(
                        self.hi_basic_amount
                        * self.hi_rate
                        / self.days_of_year
                        * self.active_days
                    ),
                    "formula": f"({self.hi_basic_amount} * {self.hi_rate}) / {self.days_of_year} * {self.active_days}",
                },
                "for_employee": {
                    "result": 0,
                    "formula": "0",
                },
            }

        return {
            "for_company": {
                "result": cost,
                "formula": f"{cost}",
            },
            "for_employee": {
                "result": 0,
                "formula": "0",
            },
        }

    def cal_akdd(self, level: int):
        """
        基础保额公司缴纳
        超出基础部分保额员工缴纳
        :param level:
        :return:
        """
        amount = self.akdd_amount.get(level)
        if amount is None:
            # raise KeyError(f"akdd_amount level{level} got None")
            return {
                "for_company": {
                    "result": 0,
                    "formula": "0",
                },
                "for_employee": {
                    "result": 0,
                    "formula": "0",
                },
            }

        return {
            "for_company": {
                "result": self.handle_result(
                    self.akdd_basic_amount
                    * self.akdd_rate
                    / self.days_of_year
                    * self.active_days
                ),
                "formula": f"({self.akdd_basic_amount} * {self.akdd_rate}) / {self.days_of_year} * {self.active_days}",
            },
            "for_employee": {
                "result": self.handle_result(amount - self.akdd_basic_amount)
                * self.akdd_rate
                / self.days_of_year
                * self.active_days,
                "formula": f"({amount} - {self.akdd_basic_amount}) * {self.akdd_rate} / {self.days_of_year} * {self.active_days}",
            },
        }
