import json
import random
# al 信息启发因子，值与搜索范围正相关，本问题推荐取值[1,5]
# be 期望启发因子，值与收敛速度正相关，本问题推荐取值[1,5]
# rho 信息素挥发因子，值与收敛速度正相关，强制取值范围(0,1),前端需要做范围校验
# israndom 为1时，d_x,d_y置空，表示随机产生城市坐标,范围是[1,800]
# 为0时，d_x d_y中填入每个城市的x,y坐标，，前端需要校验x和y数量是否相等
# 你可以自行指定每个城市的x,y坐标，也可以使用我们提供的随机坐标

al = 1
be = 2
rho = 0.5
israndom = 0
city_n = 50
d_x = [random.randint(50, 800) for i in range(city_n)]
d_y = [random.randint(50, 800) for i in range(city_n)]


def update(al=al, be=be, rho=rho, israndom=israndom, city_n=city_n, d_x=d_x, d_y=d_y):
    data = {'al': al, 'be': be, 'rho': rho, 'israndom': israndom,
            'd_x': d_x, 'd_y': d_y}
    with open('./config.json', 'w') as json_file:
        print(data)
        json.dump(data, json_file)


if __name__ == '__main__':
    update()  # 在这里填入你的自定义参数
