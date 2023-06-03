import requests
from bs4 import BeautifulSoup
import re
import csv
import pandas as pd

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
            publications = list(map(int, row[1].strip().split(', ')))

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
# до 2010 | 2010-2017 | 2018-2023                     #
#######################################################

# with open('Data/AuthorID_NEW_AuthorID_TSU_PublicationsID.csv', 'r', newline='') as input_file:
#     csv_reader = csv.reader(input_file, delimiter=';')
#     next(csv_reader)  # Пропускаем заголовок
#
#     for row in csv_reader:
#         publications = []
#         publications.extend(row[2].split(','))
#         for publication in publications:
#             try:
#                 if int(find_year_by_publication_id(publication)) < 2010:
#                     with open('before_2010.csv', 'a') as before_2010_file:
#                         writer = csv.writer(before_2010_file)
#                         write_row = row[0] + ';' + publication
#                         # print(write_row)
#                         writer.writerow(write_row)
#                         before_2010_file.close()
#
#                 if int(find_year_by_publication_id(publication)) >= 2010 and int(
#                         find_year_by_publication_id(publication)) <= 2017:
#                     with open('2005-2015.csv', 'a') as _2010_2017_file:
#                         writer = csv.writer(_2010_2017_file)
#                         write_row = row[0] + ';' + publication
#                         # print(write_row)
#                         writer.writerow(write_row)
#                         _2010_2017_file.close()
#
#                 if int(find_year_by_publication_id(publication)) > 2017:
#                     with open('after_2015.csv', 'a') as after_2017_file:
#                         writer = csv.writer(after_2017_file)
#                         write_row = row[0] + ';' + publication
#                         # print(write_row)
#                         writer.writerow(write_row)
#                         after_2017_file.close()
#             except Exception:
#                 with open('Data/there_have_been_problems.txt', 'a') as exception_file:
#                     txt_string = f'Publication ID: {publication}\n {row}'
#                     exception_file.write(txt_string)
#                     exception_file.close()
#                 # print(f'Publication ID: {publication}\n {row}')
#             # print(publication)
