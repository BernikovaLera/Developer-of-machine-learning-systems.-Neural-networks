# %%
import pandas as pd
import numpy as np
from IPython.core.interactiveshell import InteractiveShell
InteractiveShell.ast_node_interactivity = "all"
np.set_printoptions(legacy="1.25")

# %% [markdown]
# ### Загрузка данных
# %%
df = pd.read_csv('data/cities.csv')

# %%
# Координаты административных центров
centers = {
    'Москва': (55.7558, 37.6173),
    'Новосибирск': (55.0084, 82.9357),
    'Владивосток': (43.1155, 131.8855)
}
# %%
# Функция для расчета расстояния между двумя точками на Земле
def haversine(lat1, lon1, lat2, lon2):
    RADIUS = 6371  # Радиус Земли в километрах
    lat1, lon1, lat2, lon2 = map(np.deg2rad, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = np.sin(dlat / 2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2)**2
    c = 2 * np.arcsin(np.sqrt(a))
    total_km = RADIUS * c
    return total_km

# Функция для безопасного преобразования
def safe_convert_population(population):
    try:
        return int(population.replace(' ', ''))
    except ValueError:
        return np.nan
# %%
df['Население'] = df['Население'].apply(safe_convert_population)
# %%
# 1. Города в Центральном федеральном округе в радиусе 100 км от Москвы с населением <= 50т.
central_federal_district = df.query("`Федеральный округ` == 'Центральный' and `Население` <= 50000")
central_federal_district['Расстояние'] = haversine(55.7558, 37.6173, central_federal_district['Широта'].values, central_federal_district['Долгота'].values)
result_central = central_federal_district[central_federal_district['Расстояние'] <= 100]
result_central
# %%
# 2. Города в Сибирском федеральном округе в радиусе от 150 до 250 км от Новосибирска с населением от 100т. до 200т.
siberian_federal_district = df.query("`Федеральный округ` == 'Сибирский' and `Население` >= 100000 and `Население` <= 200000")
siberian_federal_district['Расстояние'] = haversine(55.0084, 82.9357, siberian_federal_district['Широта'].values, siberian_federal_district['Долгота'].values)
result_siberian = siberian_federal_district[(siberian_federal_district['Расстояние'] >= 150) & (siberian_federal_district['Расстояние'] <= 250)]
result_siberian
# %%
# 3. Города в Дальневосточном федеральном округе ближе всего к Владивостоку с населением от 10т. до 20т.
dalnevostochniy_federal_district = df.query("`Федеральный округ` == 'Дальневосточный' and `Население` >= 10000 and `Население` <= 20000")
dalnevostochniy_federal_district['Расстояние'] = haversine(43.1155, 131.8855, dalnevostochniy_federal_district['Широта'].values, dalnevostochniy_federal_district['Долгота'].values)
result_dalnevostochniy = dalnevostochniy_federal_district.nsmallest(5, 'Расстояние')
result_dalnevostochniy
# %%
# 4. Три самых многочисленных округа с радиусом 100 км от административного центра, 
# не считая ЦФО.

# Фильтруем данные, исключая ЦФО
df_non_cfo = df[~df['Федеральный округ'].str.contains('Центральный')]
# %%
# Находим административные центры (где Признак центра района или региона = 1)
admin_centers = df_non_cfo[df_non_cfo['Признак центра района или региона'] == 1]
# %%
# Создаем список для хранения результатов
results = []

# Для каждого административного центра вычисляем расстояние до всех других регионов
for index, center in admin_centers.iterrows():
    center_lat = center['Широта']
    center_lon = center['Долгота']

 # Вычисляем расстояние до всех регионов
    df_non_cfo['Расстояние'] = haversine(center_lat, center_lon, df_non_cfo['Широта'], df_non_cfo['Долгота'])
    # Фильтруем регионы в радиусе 100 км
    nearby_regions = df_non_cfo[df_non_cfo['Расстояние'] <= 100]
    # Считаем население для этих регионов
    total_population = nearby_regions['Население'].sum()
    results.append({'Федеральный округ': center['Федеральный округ'], 'Население': total_population})
# %%
# Преобразуем результаты в DataFrame
results_df = pd.DataFrame(results)
# Находим три самых многочисленных округа
top_counties = results_df.groupby('Федеральный округ')['Население'].sum().nlargest(3)
top_counties