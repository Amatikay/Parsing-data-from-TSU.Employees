import requests
from bs4 import BeautifulSoup
import re
import csv
import pandas as pd
from scipy.sparse import coo_matrix, save_npz



def save_get_request_to_file(url, filename):
    response = requests.get(url)

    if response.status_code == 200:
        with open(filename, 'w') as file:
            file.write(response.text)
        print("Запрос успешно сохранен в файл", filename)
    else:
        print("Ошибка при выполнении GET-запроса:", response.status_code)
def extract_references(response_text):
    pattern = r"\?publicationId=(\d+)"
    soup = BeautifulSoup(response_text, 'html.parser')
    references = []

    td_elements = soup.find_all('td', class_='py-2')
    for td in td_elements:
        link_element = td.find('a')
        if link_element:
            href = link_element.get('href')
            match = re.search(pattern, href)
            if match:
                publication_id = match.group(1)
                references.append(publication_id)
    return references

def get_and_extract_data(url):
    response = requests.get(url)
    if response.status_code == 200:
        publication_titles = extract_references(response.text)
        return publication_titles

def check_page_exist(url):
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        object_div = soup.find('div', class_='alert alert-primary')
        object_h1 = soup.find('h1', class_='mb-1 row justify-content-between')
        if object_div and object_div.get_text(strip=True) == 'Нет данных':
            return False
        else:
            return True
    else:
        print("Ошибка при выполнении запроса:", response.status_code)

def extract_unique_publication_ids(input_file, output_file):
    unique_publication_ids = set()

    with open(input_file, 'r') as csv_file:
        reader = csv.reader(csv_file, delimiter=';')
        next(reader)  # Пропускаем заголовок

        for row in reader:
            publication_ids = row[1].strip().split(', ')
            for publication_id in publication_ids:
                unique_publication_ids.add(publication_id)

    with open(output_file, 'w', newline='') as csv_file:
        writer = csv.writer(csv_file, delimiter=';')
        writer.writerow(['Publication ID'])

        for publication_id in unique_publication_ids:
            writer.writerow([publication_id])

def sort_csv(input_file, output_file, sort_column):
    with open(input_file, 'r') as csv_file:
        reader = csv.reader(csv_file)
        header = next(reader)
        sorted_rows = sorted(reader, key=lambda row: row[sort_column])

    with open(output_file, 'w', newline='') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(header)
        writer.writerows(sorted_rows)

def build_adjacency_matrix_from_csv(csv_file_path, mtx_file_path):
    adjacency_matrix = []
    publication_ids = set()

    with open(csv_file_path, 'r') as csv_file:
        reader = csv.reader(csv_file, delimiter=';')
        next(reader)  # Пропускаем заголовок

        for row in reader:
            author_id = int(row[0])
            publications = list(map(int, row[1].strip().split(',')))

            adjacency_row = [author_id, publications]
            adjacency_matrix.append(adjacency_row)

            publication_ids.update(publications)

    publication_list = sorted(publication_ids)
    num_authors = len(adjacency_matrix)
    num_publications = len(publication_list)

    with open(mtx_file_path, 'w') as mtx_file:
        mtx_file.write("%%MatrixMarket matrix coordinate integer general\n")
        mtx_file.write(f"{num_authors} {num_publications} {sum(len(row[1]) for row in adjacency_matrix)}\n")

        for i, adjacency_row in enumerate(adjacency_matrix):
            author_id = adjacency_row[0]
            publications = adjacency_row[1]

            for publication_id in publications:
                mtx_file.write(f"{i + 1} {publication_list.index(publication_id) + 1} 1\n")

def extract_year_from_publication_url(url):  #
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    year_element = soup.find('td', string='Год')
    if year_element:
        year = year_element.find_next_sibling('td').text
        return year
    else:
        print("Год не найден")

def group_by_authorID_and_append_publicationID_by_coma(csvfile):
    df = pd.read_csv(csvfile, delimiter=';')

    # Группировка по 'author_id' и объединение 'publication_id' через запятую
    grouped_df = df.groupby('author_id')['publication_id'].apply(lambda x: ','.join(x.astype(str))).reset_index()

    # Сохранение результата в новый CSV файл
    grouped_df.to_csv('new_' + csvfile, index=False, sep=';')

def find_year_by_publication_id(publication_id, ):
    with open('Data/PublicationID_Year.csv', 'r') as file:
        reader = csv.DictReader(file, delimiter=';')
        for row in reader:
            if row['Publication_ID'] == str(publication_id):
                return row['Year']
    return None






#######################################################
#                                                     #
#                                                     #
# Добавление полей стажа и факультета                 #
#                                                     #
#                                                     #
#######################################################
# # Функция для получения значения Experience по AuthorID_TSU
# def getExp(author_id):
#     url = f'https://persona.tsu.ru/Home/UserProfile/{author_id}'
#     response = requests.get(url)
#     soup = BeautifulSoup(response.text, 'html.parser')
#     divs = soup.find_all('div')
#     for i, div in enumerate(divs):
#         if div.text.strip() == 'Общий стаж' and i + 1 < len(divs):
#             return divs[i + 1].text.strip()
#     return 0
# def getSubdiv(author_id):
#     url = f'https://persona.tsu.ru/Home/UserProfile/{author_id}'
#     response = requests.get(url)
#     soup = BeautifulSoup(response.text, 'html.parser')
#     spans = soup.find_all('span', itemprop='name')
#
#     if len(spans) >= 2:
#         return spans[1].text.strip()
#     else:
#         return None
#
# # Чтение исходной таблицы из CSV файла
# df = pd.read_csv('Data/AuthorID_NEW_AuthorID_TSU_PublicationsID.csv', delimiter=';')
#
# # Создание новой таблицы с необходимыми полями
# new_df = pd.DataFrame(columns=['AuthorID_NEW', 'AuthorID_TSU', 'Experience', 'Subdivision', 'PublicationsID'])
#
# # Итерация по исходной таблице и заполнение новой таблицы
# for index, row in df.iterrows():
#     author_id_new = row['AuthorID_NEW']
#     author_id_tsu = row['AuthorID_TSU']
#     publications_id = row['PublicationsID']
#     experience = getExp(author_id_tsu)
#     subdivision = getSubdiv(author_id_tsu)
#
#     new_row = {'AuthorID_NEW': author_id_new, 'AuthorID_TSU': author_id_tsu, 'Experience': experience,
#                'Subdivision': subdivision, 'PublicationsID': publications_id}
#     new_df = new_df._append(new_row, ignore_index=True)
#
# # Сохранение новой таблицы в CSV файл
# new_df.to_csv('AuthorID_NEW_AuthorID_TSU_Experience_Subdivision_PublicationsID.csv.csv', index=False, sep=';')








# Соединил таблицы в одну
# years_df = pd.read_csv('Data/Years_of_publication.csv')
# publications_df = pd.read_csv('Data/Publication_ID.csv')
#
# # Combine the columns into a new dataframe
# new_table_df = pd.DataFrame({
#     'new_column': publications_df['Publication_ID'].astype(str) + ';' + years_df['Year_of_publication'].astype(str)
# })
#
# # Save the new table as a CSV file
# new_table_df.to_csv('new_table.csv', index=False)




# Создание таблицы с автором и его публикациями. Этот блок кода не полный. Данные приходилось немного корректровать. (Удалить несуществующие ссылки, лишние запятые и тд.
# Этих корректировок было около 10 по этому в скрипт не добавлял.
# with open('Data/AuthorID_PublicationID.csv', 'w') as file:
#     writer = csv.writer(file)
#     # Запись заголовков столбцов
#     headers = ['Author ID', 'Publication ID']
#     writer.writerow(headers)
#     file.close()
#
#
# with open('Data/sorted_Employees_with_publications.txt', 'r') as input_file:
#     id_s = input_file.readlines()
#     for id_value in id_s:
#         id_value = id_value.strip()
#         i = 1
#         while True:
#             url = f"https://persona.tsu.ru/Publications/Index/{id_value}?page={i}"
#             if not check_page_exist(url):
#                 break  # Прерываем цикл, если страница не существует
#             with open('Data/AuthorID_PublicationID.csv', 'a') as file:
#                 writer = csv.writer(file)
#                 data_row = [id_value, get_and_extract_data(url)]
#                 writer.writerow(data_row)
#                 file.close()
#             i += 1




# Поиск дат публикаций
# def find_author_id(publication_id, author_publications):
#     for row in author_publications:
#         author_id = row[0]
#         publications = row[1].split(', ')
#         if publication_id in publications:
#             return author_id
#     return None
#
#
# with open('Data/PublicationID(1).csv', 'r') as publication_file:
#     publication_reader = csv.reader(publication_file)
#     next(publication_reader)  # Пропуск заголовка
#     for row in publication_reader:
#         publication_id = row[0]
#
#         # Чтение файла AuthorID_PublicationsID.csv
#         with open('Data/AuthorID_PublicationsID.csv', 'r') as author_file:
#             author_reader = csv.reader(author_file, delimiter=';')
#             next(author_reader)  # Пропуск заголовка
#             author_publications = list(author_reader)
#
#             # Поиск Author ID
#             author_id = find_author_id(publication_id, author_publications)
#
#             if author_id:
#                 with open('Data/Years_of_publication.csv','a') as years_file:
#                     writer = csv.writer(years_file)
#                     row = extract_year_from_publication_url(f'https://persona.tsu.ru/Publications/Info/{author_id}?publicationId={publication_id}')
#                     writer.writerow(row)
#                     years_file.close()
#             else:
#                 print(f'Publication ID: {publication_id}, Author ID not found')
#


#######################################################
#                                                     #
#                                                     #
# Разделение на 3 таблицы по датам публикации         #
#                                                     #
# до 2016 | 2016-2019 | 2020-2023                     #
#######################################################
#
# with open('Data/AuthorID_NEW_AuthorID_TSU_PublicationsID.csv', 'r', newline='') as input_file:
#     csv_reader = csv.reader(input_file, delimiter=';')
#     next(csv_reader)  # Пропускаем заголовок
#
#     for row in csv_reader:
#         publications = []
#         publications.extend(row[2].split(','))
#         for publication in publications:
#             try:
#                 if int(find_year_by_publication_id(publication)) < 2016:
#                     with open('before_2016.csv', 'a') as before_2016_file:
#                         writer = csv.writer(before_2016_file)
#                         write_row = row[0] + ';' + publication
#                         # print(write_row)
#                         writer.writerow(write_row)
#                         before_2016_file.close()
#
#                 if int(find_year_by_publication_id(publication)) >= 2016 and int(
#                         find_year_by_publication_id(publication)) <= 2019:
#                     with open('2016-2019.csv', 'a') as _2017_2019_file:
#                         writer = csv.writer(_2017_2019_file)
#                         write_row = row[0] + ';' + publication
#                         # print(write_row)
#                         writer.writerow(write_row)
#                         _2017_2019_file.close()
#
#                 if int(find_year_by_publication_id(publication)) > 2019:
#                     with open('after_2021.csv', 'a') as after_2021_file:
#                         writer = csv.writer(after_2021_file)
#                         write_row = row[0] + ';' + publication
#                         # print(write_row)
#                         writer.writerow(write_row)
#                         after_2021_file.close()
#             except Exception:
#                 # with open('Data/there_have_been_problems.txt', 'a') as exception_file:
#                 #     txt_string = f'Publication ID: {publication}\n {row}'
#                 #     exception_file.write(txt_string)
#                 #     exception_file.close()
#                 print(f'Publication ID: {publication}\n {row}')
#             # print(publication)




###########################################################

####### Разбиение на 2 файла с ОДИНАКОВОЙ размерностью ####

###########################################################

# file1_path = 'Data/PublicationID_Year.csv'
# data1 = {}
# with open(file1_path, 'r') as file1:
#     reader = csv.DictReader(file1, delimiter=';')
#     for row in reader:
#         publication_id = int(row['Publication_ID'])
#         year = int(row['Year'])
#         data1[publication_id] = year
#
# file2_path = 'Data/AuthorID_NEW_AuthorID_TSU_PublicationsID.csv'
# data2 = {}
# with open(file2_path, 'r') as file2:
#     reader = csv.DictReader(file2, delimiter=';')
#     for row in reader:
#         author_id_new = int(row['AuthorID_NEW'])
#         publication_ids = row['PublicationsID'].split(',')
#         publication_ids = [int(publication_id) for publication_id in publication_ids]
#         data2[author_id_new] = publication_ids
# # Создание матрицы смежности для периода до 2016 года
# adjacency_matrix_before_2016 = [[0] * len(data2) for _ in range(len(data2))]
#
# for author_id_new, publication_ids in data2.items():
#     for publication_id in publication_ids:
#         if publication_id in data1 and data1[publication_id] < 2016:
#             for other_author_id_new, other_publication_ids in data2.items():
#                 if other_author_id_new != author_id_new and publication_id in other_publication_ids:
#                     adjacency_matrix_before_2016[author_id_new-1][other_author_id_new-1] = 1
#                     adjacency_matrix_before_2016[other_author_id_new-1][author_id_new-1] = 1
#
# # Создание матрицы смежности для периода 2016-2019 годы
# adjacency_matrix_2016_2019 = [[0] * len(data2) for _ in range(len(data2))]
#
# for author_id_new, publication_ids in data2.items():
#     for publication_id in publication_ids:
#         if publication_id in data1 and 2016 <= data1[publication_id] <= 2019:
#             for other_author_id_new, other_publication_ids in data2.items():
#                 if other_author_id_new != author_id_new and publication_id in other_publication_ids:
#                     adjacency_matrix_2016_2019[author_id_new-1][other_author_id_new-1] = 1
#                     adjacency_matrix_2016_2019[other_author_id_new-1][author_id_new-1] = 1
#
# # Создание матрицы смежности для периода после 2019 года
# adjacency_matrix_after_2019 = [[0] * len(data2) for _ in range(len(data2))]
#
# for author_id_new, publication_ids in data2.items():
#     for publication_id in publication_ids:
#         if publication_id in data1 and data1[publication_id] > 2019:
#             for other_author_id_new, other_publication_ids in data2.items():
#                 if other_author_id_new != author_id_new and publication_id in other_publication_ids:
#                     adjacency_matrix_after_2019[author_id_new-1][other_author_id_new-1] = 1
#                     adjacency_matrix_after_2019[other_author_id_new-1][author_id_new-1] = 1
#
# # Сохранение матрицы смежности для периода до 2016 года в файл .dat
# matrix_before_2016_path = 'путь_к_файлу_матрицы_до_2016.dat'
# with open(matrix_before_2016_path, 'w') as file:
#     for row in adjacency_matrix_before_2016:
#         file.write(' '.join(map(str, row)) + '\n')
#
# # Сохранение матрицы смежности для периода 2016-2019 годы в файл .dat
# matrix_2016_2019_path = 'путь_к_файлу_матрицы_2016_2019.dat'
# with open(matrix_2016_2019_path, 'w') as file:
#     for row in adjacency_matrix_2016_2019:
#         file.write(' '.join(map(str, row)) + '\n')
#
# # Сохранение матрицы смежности для периода после 2019 года в файл .dat
# matrix_after_2019_path = 'путь_к_файлу_матрицы_после_2019.dat'
# with open(matrix_after_2019_path, 'w') as file:
#     for row in adjacency_matrix_after_2019:
#         file.write(' '.join(map(str, row)) + '\n')
