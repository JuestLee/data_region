# -*- coding: utf-8 -*-
# 导入:
import json
from sqlalchemy import Column, String, create_engine, Integer
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from pypinyin import pinyin, lazy_pinyin, Style

# 创建对象的基类:
Base = declarative_base()


class CityCn(Base):
    # 表的名字:
    __tablename__ = 'city_cn'

    # 表的结构:
    id = Column(Integer(), primary_key=True)
    country = Column(String(255))
    state = Column(String())
    city = Column(String())
    state_code = Column(String())
    city_code = Column(String())
    country_code = Column(String())
    country_pinyin = Column(String())
    state_pinyin = Column(String())
    city_pinyin = Column(String())


# 初始化数据库连接:
engine = create_engine('postgresql+psycopg2://hwan:@127.0.0.1:5432/mydb',client_encoding='utf8')
# 创建DBSession类型:
DBSession = sessionmaker(bind=engine)

session = DBSession()


def pinyin_data():
    all_rows = (session.query(CityCn).order_by(CityCn.id).all())
    for row in all_rows:
        # 国家
        name = row.country
        name_pinyin_list = pinyin(name, style=Style.NORMAL)
        name_pinyin = ''
        for item_piyin in name_pinyin_list:
            name_pinyin = name_pinyin + item_piyin[0] + ' '
        row.country_pinyin = name_pinyin

        # 省
        name = row.state
        if name:
            name_pinyin_list = pinyin(name, style=Style.NORMAL)
            name_pinyin = ''
            for item_piyin in name_pinyin_list:
                name_pinyin = name_pinyin + item_piyin[0] + ' '
            row.state_pinyin = name_pinyin

        # 市
        name = row.city
        if name:
            name_pinyin_list = pinyin(name, style=Style.NORMAL)
            name_pinyin = ''
            for item_piyin in name_pinyin_list:
                name_pinyin = name_pinyin + item_piyin[0] + ' '
            row.city_pinyin = name_pinyin
    session.commit()


def dump_data():
    has = set()
    res = []
    countries = (session.query(CityCn)
                 .order_by(CityCn.country_pinyin).all())
    for country in countries:
        if country.country in has:
            continue
        if not country.state:
            # 没有省
            provinces = (session.query(CityCn)
                         .filter(CityCn.country_code == country.country_code)
                         .order_by(CityCn.city_pinyin).all())
            province_list = []
            for province in provinces:
                province_dict = {"city": [], "name": province.city}
                province_list.append(province_dict)
        else:
            # 有省
            provinces = (session.query(CityCn)
                         .filter(CityCn.country_code == country.country_code)
                         .order_by(CityCn.state_pinyin).all())
            province_list = []
            has_province = set()
            for province in provinces:
                if province.state in has_province:
                    continue
                city_list = []
                cities = (session.query(CityCn)
                         .filter(CityCn.country_code == country.country_code)
                         .filter(CityCn.state == province.state)
                         .order_by(CityCn.city_pinyin).all())
                for city in cities:
                    city_list.append({'name': city.city})
                province_dict = {'name': province.state, 'city': city_list}
                province_list.append(province_dict)
                has_province.add(province.state)
        country_dict = {"province": province_list, 'country': country.country}
        res.append(country_dict)
        has.add(country.country)
    with open('data_region_android.json', 'w', encoding='utf-8') as file:
        json.dump(res, file, indent=4, sort_keys=True)
    json.dumps(res, indent=4)


if __name__ == '__main__':
    # pinyin_data()
    dump_data()
