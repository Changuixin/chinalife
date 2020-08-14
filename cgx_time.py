import time


def cgx_time(function):
    def wrapper():
        start_time = time.time()
        function()
        end_time = time.time()

        cost_time = end_time - start_time
        print('\033[1;31;40m', end='')
        print('*' * 50)
        print('*开始时间:\t' + time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(start_time)))
        print('*结束时间:\t' + time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(end_time)))
        print('*耗费时间:\t{}秒'.format(cost_time))
        print('*' * 50)
        print('\033[0m')

    return wrapper


@cgx_time
def test():
    time.sleep(3)


if __name__ == '__main__':
    test()
