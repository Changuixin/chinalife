class InsuredPerson(object):
    def __init__(self, policy_number, id, name):
        self.policy_number = policy_number
        self.policy_number_with_encryption = self.__get_encryption_policy_number()
        self.name = name
        self.id = id
        self.format_birthday_str = self.__get_format_birthday_str()

    # 获取加密的保单号"2020350425**************6_65"
    def __get_encryption_policy_number(self):
        return self.policy_number[0:10] + '**************' + self.policy_number[-4:]

    # 获取格式化的生日字符串"2020-05-18"
    def __get_format_birthday_str(self):
        id = self.id
        return '{}-{}-{}'.format(id[6:10], id[10:12], id[12:14])
