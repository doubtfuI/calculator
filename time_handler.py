from datetime import datetime


def time_serialize(time_str: str):
    nums = time_str.split("/")
    year = int(nums[0])
    month = int(nums[1])
    day = int(nums[2])
    return datetime(year=year, month=month, day=day)
