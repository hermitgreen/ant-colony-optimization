import copy
import sys
import json
from functools import reduce
import threading
import tkinter
import time
import random
# al 信息启发因子，值与搜索范围正相关，本问题推荐取值[1,5]
# be 期望启发因子，值与收敛速度正相关，本问题推荐取值[1,5]
# rho 信息素挥发因子，值与收敛速度正相关，强制取值范围(0,1)
al, be, rho, Q = 1, 1, 0.5, 100
# 城市数和蚁群数
city_n, ant_n = 64, 64
# 城市的x,y坐标
d_x = [random.randint(50, 800) for i in range(city_n)]
d_y = [random.randint(50, 800) for i in range(city_n)]
# 预处理出距离和信息素浓度
d_g = [[0.0 for col in range(city_n)] for raw in range(city_n)]
p_g = [[1.0 for col in range(city_n)] for raw in range(city_n)]


# 处理每只蚂蚁
class slove(object):
    # 初始化
    def __init__(self, i):
        self.i = i
        self.__init()

    # 初始数据
    def __init(self):
        self.path = []  # 路径
        self.total = 0.0  # 总距离
        self.move_count = 0  # 移动次数
        self.now = -1  # 当前城市
        self.open = [True for i in range(city_n)]  # open表，初始时全部没有访问过
        city_index = random.randint(0, city_n - 1)  # 初始点
        self.now = city_index  # 更新当前位置
        self.path.append(city_index)  # 更新当前路径
        self.open[city_index] = False  # 当前位置访问过了
        self.move_count = self.move_count+1  # 访问量+1

    # 下一个
    def __choice_next(self):
        next = -1
        prob = [0.0 for i in range(city_n)]  # 去下个城市的概率
        total_prob = 0.0
        # 获取去下一个城市的概率
        for i in range(city_n):
            if self.open[i]:
                prob[i] = pow(p_g[self.now][i], al) * \
                    pow((1.0 / d_g[self.now][i]), be)
                total_prob += prob[i]
        # 选择城市
        if total_prob > 0.0:
            # 产生一个随机概率
            temp_prob = random.uniform(0.0, total_prob)
            for i in range(city_n):
                if self.open[i]:
                    temp_prob -= prob[i]
                    if temp_prob < 0.0:
                        next = i
                        break
        if (next == -1):
            next = random.randint(0, city_n - 1)
            while ((self.open[next]) == False):
                next = random.randint(0, city_n - 1)
        return next

    # 计算总距离
    def __cal_total(self):
        dis = 0.0
        for i in range(1, city_n):
            start, end = self.path[i], self.path[i - 1]
            dis += d_g[start][end]
        end = self.path[0]
        dis += d_g[start][end]
        self.total = dis

    # 移动
    def __move(self, next):
        self.path.append(next)
        self.open[next] = False
        self.total += d_g[self.now][next]
        self.now = next
        self.move_count += 1

    # 搜索路径
    def search_path(self):
        self.__init()
        # 搜素路径，遍历完所有城市为止
        while self.move_count < city_n:
            # 移动到下一个城市
            next = self.__choice_next()
            self.__move(next)
        # 计算路径总长度
        self.__cal_total()


# 图形化
class graph(object):
    def __init__(self, root, width=900, height=800, n=city_n):
        # 创建画布
        self.root = root
        self.width = width
        self.height = height
        self.n = n
        self.canvas = tkinter.Canvas(
            root,
            width=self.width,
            height=self.height,
            bg="#FFFFFF",
            xscrollincrement=1,
            yscrollincrement=1
        )
        self.canvas.pack(expand=tkinter.YES, fill=tkinter.BOTH)
        self.title(
            "s:开始搜索 e:停止搜索 q:退出程序 u:加快速度 d:减慢速度 f:重新开始 当前速度9(1-9) 当前迭代次数0 当前最短距离INF")
        self.__r = 3
        self.__lock = threading.RLock()
        self.__bindEvents()
        self.__init()
        # 计算城市之间的距离
        for i in range(city_n):
            for j in range(city_n):
                dis = pow(
                    (d_x[i] - d_x[j]), 2) + pow((d_y[i] - d_y[j]), 2)
                dis = pow(dis, 0.5)
                d_g[i][j] = float(int(dis + 0.5))

    # 绑定按键
    def __bindEvents(self):
        self.root.bind("q", self.quite)  # 退出程序
        self.root.bind("f", self.__init)  # 初始化
        self.root.bind("s", self.search_path)  # 开始搜索
        self.root.bind("e", self.stop)  # 停止搜索
        self.root.bind("u", self.up_speed)  # 加快速度
        self.root.bind("d", self.down_speed)  # 减慢速度

    def up_speed(self, evt):
        # 开启线程
        self.__lock.acquire()
        self.__running = True
        self.__lock.release()
        t = self.delay
        t = t+1
        if t > 9:
            self.delay = 9
        else:
            self.delay = t

    def down_speed(self, evt):
        # 开启线程
        self.__lock.acquire()
        self.__running = True
        self.__lock.release()
        t = self.delay
        t = t-1
        if t < 1:
            self.delay = 1
        else:
            self.delay = t

    # 更改标题
    def title(self, s):
        self.root.title(s)

    # 初始化
    def __init(self, evt=None):
        # 停止线程
        self.__lock.acquire()
        self.__running = False
        self.__lock.release()
        self.clear()  # 清除信息
        self.nodes = []  # 节点坐标
        self.objs = []  # 节点对象
        for i in range(len(d_x)):
            x = d_x[i]
            y = d_y[i]
            self.nodes.append((x, y))
            # 生成节点椭圆，半径为self.__r
            node = self.canvas.create_oval(
                x - self.__r, y - self.__r, x + self.__r, y + self.__r, fill="#000000", outline="#000000", tags="node")
            self.objs.append(node)
            # 显示坐标
            self.canvas.create_text(
                x, y - 10, text='(' + str(x) + ',' + str(y) + ')', fill='black')
        for i in range(city_n):
            for j in range(city_n):
                p_g[i][j] = 1.0
        self.ants = [slove(i) for i in range(ant_n)]  # 初始蚁群
        self.best = slove(-1)  # 初始最优解
        self.best.total = 1 << 31  # 初始最大距离
        self.iter = 1  # 初始迭代次数
        self.delay = 9  # 初始延迟

    # 将节点按order顺序连线
    def line(self, order):
        # 删除原线
        self.canvas.delete("line")

        def line2(i1, i2):
            p1, p2 = self.nodes[i1], self.nodes[i2]
            self.canvas.create_line(p1, p2, fill="#000000", tags="line")
            return i2
        reduce(line2, order, order[-1])

    # 清除
    def clear(self):
        for item in self.canvas.find_all():
            self.canvas.delete(item)

    # 退出程序
    def quite(self, evt):
        self.__lock.acquire()
        self.__running = False
        self.__lock.release()
        self.root.destroy()
        print(u"\nFinish")
        sys.exit()

    # 停止搜索
    def stop(self, evt):
        self.__lock.acquire()
        self.__running = False
        self.__lock.release()

    # 开始搜索
    def search_path(self, evt=None):
        # 开启线程
        self.__lock.acquire()
        self.__running = True
        self.__lock.release()
        while self.__running:
            for i in range(9-self.delay):
                time.sleep(0.1)
            for ant in self.ants:  # 遍历每一只蚂蚁
                ant.search_path()  # 搜索一条路径
                if ant.total < self.best.total:  # 与当前最优蚂蚁比较
                    self.best = copy.deepcopy(ant)  # 更新最优解
            # 更新信息素
            self.__update_p_g()
            print(u"迭代次数：", self.iter, u"总距离：",
                  int(self.best.total))
            # 连线
            self.line(self.best.path)
            # 设置标题
            self.title(
                "s:开始搜索 e:停止搜索 q:退出程序 u:加快速度 d:减慢速度 f:重新开始 当前速度%d(1-9) 当前迭代次数%d 当前最短距离%d" % (self.delay, self.iter, int(self.best.total)))
            # 更新画布
            self.canvas.update()
            self.iter += 1

    # 更新信息素
    def __update_p_g(self):
        # 获取之前的
        t_p = [[0.0 for col in range(
            city_n)] for raw in range(city_n)]
        for ant in self.ants:
            for i in range(1, city_n):
                start, end = ant.path[i - 1], ant.path[i]
                # 留下信息
                t_p[start][end] += Q / ant.total
                t_p[end][start] = t_p[start][end]
        # 更新信息素
        for i in range(city_n):
            for j in range(city_n):
                p_g[i][j] = p_g[i][j] * rho + t_p[i][j]

    def mainloop(self):
        self.root.mainloop()


if __name__ == '__main__':
    with open('./config.json', 'r') as json_file:
        data = json.load(json_file)
        al = data['al']
        be = data['be']
        rho = data['rho']
        israndom = data['israndom']
        if israndom != 1:
            d_x = data['d_x']
            d_y = data['d_y']
            ant_n = city_n = len(d_x)
            d_g = [[0.0 for col in range(city_n)] for raw in range(city_n)]
            p_g = [[1.0 for col in range(city_n)] for raw in range(city_n)]

    graph(tkinter.Tk()).mainloop()
