# -*- coding: utf-8 -*-
# 导入:
import json
from sqlalchemy import Column, String, create_engine, Integer
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from pypinyin import pinyin, lazy_pinyin, Style

# 创建对象的基类:
Base = declarative_base()


# 定义User对象
class DataRegion(Base):
    # 表的名字:
    __tablename__ = 'data_region'

    # 表的结构:
    id = Column(Integer(), primary_key=True)
    pid = Column(Integer())
    path = Column(String(255))
    level = Column(String())
    name = Column(String())
    name_en = Column(String())
    name_pinyin = Column(String())
    code = Column(String())


# 初始化数据库连接:
engine = create_engine('postgresql+psycopg2://hwan:@127.0.0.1:5432/mydb',client_encoding='utf8')
# 创建DBSession类型:
DBSession = sessionmaker(bind=engine)

session = DBSession()


def pinyin_data():
    all_rows = (session.query(DataRegion).order_by(DataRegion.id).all())
    for row in all_rows:
        name = row.name
        name_pinyin_list = pinyin(name, style=Style.NORMAL)
        name_pinyin = ''
        for item_piyin in name_pinyin_list:
            name_pinyin = name_pinyin + item_piyin[0] + ' '
        row.name_pinyin = name_pinyin
    session.commit()


def dump_data():
    res = []
    countries = (session.query(DataRegion)
                 .filter(DataRegion.pid.in_(['1', '2', '3', '4', '5', '6']))
                 .order_by(DataRegion.name_pinyin).all())
    for country in countries:

        provinces = (session.query(DataRegion)
                     .filter(DataRegion.pid == country.id)
                     .order_by(DataRegion.name_pinyin).all())
        province_list = []
        for province in provinces:
            city_list = []
            cities = (session.query(DataRegion)
                     .filter(DataRegion.pid == province.id)
                     .order_by(DataRegion.name_pinyin).all())
            for city in cities:
                city_list.append(city.name)
            province_dict = {province.name: city_list}
            province_list.append(province_dict)
        country_dict = {country.name: province_list}
        res.append(country_dict)
    with open('data_region_android.json', 'w', encoding='utf-8') as file:
        json.dump(res, file, indent=4, sort_keys=True)
    json.dumps(res, indent=4)


if __name__ == '__main__':
    # pinyin_data()
    dump_data()
