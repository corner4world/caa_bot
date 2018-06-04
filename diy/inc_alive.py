#!/usr/bin/env python
# -*- coding: UTF-8 -*-  

'''
{
"版权":"LDAE工作室",
"author":{
"1":"集体",
}
"初创时间:"2017年3月",
}
'''

# 花费处理类
from enum import Enum
import re


class DurationJudger(object):
    """
    薪酬转化
    """


    #@unique
    class DurationTypeScale(Enum):
        """薪酬进制比例"""
        Week=0.25
        Month = 1
        Year = 12

    # 中文对应数字比
    DIC_NUMB = {
        '〇': 0,
        '一': 1,
        '二': 2,
        '三': 3,
        '四': 4,
        '五': 5,
        '六': 6,
        '七': 7,
        '八': 8,
        '九': 9,
        '零': 0,
        '壹': 1,
        '贰': 2,
        '叁': 3,
        '肆': 4,
        '伍': 5,
        '陆': 6,
        '柒': 7,
        '捌': 8,
        '玖': 9,
        '貮': 1,
        '两': 2,
        '十': 10,
        '拾': 10
    }
    ALL_MATCH = dict({str(x): x for x in range(1, 10)}, **DIC_NUMB)

    # 数字匹配规则
    NUMB_MATCH_PATTERN = "[" + "".join(DIC_NUMB.keys()) + "]"

    # 薪酬类型判别
    UNIT_MATCH_PATTERN = "([周月年])"

    # 浮点数｜正整数匹配，非标准匹配中文混合匹配
    FLOAT_MATCH_PATTERN = '[\d\.]+'
    NONSTANDAED_MATCH_PATTERN = "{}{}".format("".join(DIC_NUMB.keys()), "\d")
    NONSTANDAED_NUM_MATCH_PATTERN = "[一二三四五六七八九壹贰叁肆伍陆柒捌玖貮两1-9]"
    CN_NUM_MATCH_PATTERN = "[一二三四五六七八九壹贰叁肆伍陆柒捌玖貮两]"

    # 省略匹配
    OMIT_QIAN_MATCH_PATTERN = "\s*({})[百佰千]({})[^一二三四五六七八九壹贰叁肆伍陆柒捌玖貮两1-9]+".\
        format(NONSTANDAED_NUM_MATCH_PATTERN, NONSTANDAED_NUM_MATCH_PATTERN)
    OMIT_WANG_MATCH_PATTERN = "\s*({})[万]({})[^一二三四五六七八九壹贰叁肆伍陆柒捌玖貮两1-9]*".\
        format(NONSTANDAED_NUM_MATCH_PATTERN, NONSTANDAED_NUM_MATCH_PATTERN)

    OMIT_MATCH_PATTERN = "({})([百])({})"\
        .format(NONSTANDAED_NUM_MATCH_PATTERN, NONSTANDAED_NUM_MATCH_PATTERN)

    #OMIT_MATCH_PATTERN_BEFORE =r"、腺第针粒碘以稀基℃直唯样代周之黄步联样其例定贴m."
    #OMIT_MATCH_PATTERN_AFTER = r"大种般些天处级余%贴岁经:下甲公科贴治是日世肢类、医院疗点期半起支腺楼叉第克部针粒(以稀基℃小直唯样代周分次黄步联样其例月年定个贴m.±)"
    FLOAT_MATCH_PATTERN_2 = "([\d.]+)([万千仟萬kKＫｋ])"

    def __init__(self):

        self.RADIX_TYPE_MATCH = {
            "周": self.DurationTypeScale.Week,
            "月": self.DurationTypeScale.Month,
            "年": self.DurationTypeScale.Year
        }


        self.DICT_JI_NUM = {
            "几十年": "20年， 90年",
            "十几年": "11年， 19年",
            "几年": "2年， 9年",
            "几周": "2周， 9周",
            "几月": "2月， 9月"
        }
        # 薪酬类型判别式, 进制判别式
        self.RADIX_TYPE_MATCH_PATTERN = "|".join(self.RADIX_TYPE_MATCH.keys())

    def duration_judge(self, salary_string):
        """
        判定上下限的薪酬函数
        :param salary_string: 薪酬字符串
        :return:
        """
        salary_string=salary_string.replace(' ', '')
        salary_string = salary_string.replace('个', '')
        radix_type = None
        nums_list = self.__get_nums_from_string(salary_string)
        return nums_list


    def __cn2dig(self, string_):
        """
        中文数字转阿拉伯
        :param string_:
        :return:
        """
        value = re.compile(r'^[0-9]+$')
        result = value.match(string_)
        if result:
            return int(string_)

        if len(string_) == 3:
            # 省略匹配，　例如一千五，　一万五
            omit_match = re.search(self.OMIT_MATCH_PATTERN, string_)

            # 省略形式的千进制匹配
            if omit_match:
                return (self.ALL_MATCH[omit_match.group(1)] + self.ALL_MATCH[omit_match.group(3)]*0.1) \
                       * self.ALL_MATCH[omit_match.group(2)]

        # 千进制数
        thousand_num_list = re.split("万|萬", string_)
        if string_.endswith("万") or string_.endswith("萬"):
            return self.__turn_thousand_nonstandard_string(string_.strip("万")) * 10000

        # 获取一万以下的数
        t1 = list(reversed(thousand_num_list))[0]
        num = self.__turn_thousand_nonstandard_string(t1)

        # 获取一万以上的数
        if len(thousand_num_list) > 1:
            t2 = thousand_num_list[0]
            num += self.__turn_thousand_nonstandard_string(t2) * 10000
        return num

    def __str2dig(self, string_):
        """
        字符串的浮点数或正整数转化成数字
        :param string_:　
        :return:
        """
        return float(string_)

    def __get_nums_from_string(self, inputstring):
        for i in self.DICT_JI_NUM.keys():
            if i in inputstring:
                inputstring=inputstring.replace(i, self.DICT_JI_NUM[i])

        number = re.compile(r'(([一二三四五六七八九壹两十1234567890]+)[周月年])')
        pattern = re.compile(number)
        nums_list = pattern.findall(inputstring)

        l=[]
        restr = r"[{}]+".format(self.NONSTANDAED_MATCH_PATTERN) + r"\s*" + "[{}]*".format(
            self.NONSTANDAED_MATCH_PATTERN) + r"\s*" + "[{}]*".format(self.NONSTANDAED_MATCH_PATTERN)

        for i in nums_list :
            radix_type=None
            unit_match = re.search(self.UNIT_MATCH_PATTERN, i[0])
            if unit_match:
                radix_type = self.RADIX_TYPE_MATCH[unit_match.group(1)]
            else:
                radix_type = self.DurationTypeScale.Month

            cn_match = re.search("[一二三四五六七八九壹贰叁肆伍陆柒捌玖貮两零]", i[1])
            try:
                if cn_match:
                    value=0
                    if radix_type.value!=1:
                        t=i[1].replace(unit_match.group(),'')
                        value = self.__cn2dig(t) * radix_type.value
                    else:
                        value = self.__cn2dig(i[1])
                    if value > 10:
                        l.append(value)
                else:
                    value=self.__str2dig(i[1].replace(' ',''))
                    l.append(int(value * radix_type.value))
            except Exception as e:
                print(str(e))
        return l


    def __turn_thousand_nonstandard_string(self, string_):
        """
        将千进制非标准数字字符串转化成数字
        :param string_: 中文字符串
        :return:
        """
        if len(string_) == 1:
            return self.ALL_MATCH[string_]

        # 十 十三 十五 匹配匹配
        shi_match_ = re.match("[拾十]({})".format(self.NONSTANDAED_NUM_MATCH_PATTERN), string_)
        if shi_match_:
            return 10 + self.ALL_MATCH[shi_match_.group(1)]

        num = 0
        week_match = re.search("({})({})".format(self.NONSTANDAED_NUM_MATCH_PATTERN, "[周]"), string_)
        month_match = re.search("({})({})".format(self.NONSTANDAED_NUM_MATCH_PATTERN, "[月]"), string_)
        year_match = re.search("({})({})({})".format(self.NONSTANDAED_NUM_MATCH_PATTERN, "[年]",
                                                    self.NONSTANDAED_NUM_MATCH_PATTERN), string_)
        single_match = re.search("{}({})".format("[拾十零]", self.NONSTANDAED_NUM_MATCH_PATTERN), string_)

        # 转化进制
        if week_match:
            num += self.ALL_MATCH[week_match.group(1)] * 0.25
        if month_match:
            num += self.ALL_MATCH[month_match.group(1)] * 1
        if year_match:
            num += self.ALL_MATCH[shi_match.group(1)] * 12
        if single_match:
            num += self.ALL_MATCH[single_match.group(1)]

        return num
