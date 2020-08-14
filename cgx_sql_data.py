import pymysql.cursors


class SqlData(object):
    def __init__(self):
        self.host = 'localhost'
        self.port = 3306
        self.username = 'root'
        self.password = '123456'
        self.db = 'china_life'
        self.charset = 'utf8'

    def __connect(self):
        return pymysql.Connect(
            host=self.host,
            port=self.port,
            user=self.username,
            password=self.password,
            database=self.db,
            charset=self.charset
        )

    def select_all(self):
        try:
            Connection = self.__connect()
            cursor = Connection.cursor()
            sql = "SELECT * FROM student_safity_insurance"
            cursor.execute(sql)

            tuple_list = cursor.fetchall()
            return tuple_list
        finally:
            cursor.close()
            Connection.close()


if __name__ == '__main__':
    sql_data = SqlData()
    tuple_list = sql_data.select_all()
    # for tuple in tuple_list:
    #     print(tuple)
