Данные выгружаются из [ТГУ.Сотрудники](https://persona.tsu.ru/)

Короткое описание функций созданных в этом проекте:

`save_get_request_to_file(url, filename)` - Функция выполняет GET-запрос по указанному URL и сохраняет полученный ответ в файл с указанным именем.

`extract_references(response_text)` - Функция извлекает ссылки на публикации из текста ответа сервера. Используется библиотека BeautifulSoup для парсинга HTML-кода страницы.

`get_and_extract_data(url)` - Функция выполняет GET-запрос по указанному URL и извлекает ссылки на публикации из полученного ответа.

`check_page_exist(url)` - Функция проверяет, существует ли страница по указанному URL. Возвращает True, если страница существует, и False в противном случае.

`extract_unique_publication_ids(input_file, output_file)` - Функция извлекает уникальные идентификаторы публикаций из CSV-файла и сохраняет их в другой CSV-файл.

`sort_csv(input_file, output_file, sort_column)` - Функция сортирует CSV-файл по указанной колонке и сохраняет отсортированные данные в другой CSV-файл.

`build_adjacency_matrix_from_csv(csv_file_path, mtx_file_path)` - Функция строит матрицу смежности на основе данных из CSV-файла и сохраняет её в формате MatrixMarket.

`extract_year_from_publication_url(url)` - Функция извлекает год публикации из указанного URL-адреса. Используется библиотека BeautifulSoup для парсинга HTML-кода страницы.

`group_by_authorID_and_append_publicationID_by_coma(csvfile)` - Функция группирует данные по идентификатору автора и объединяет идентификаторы публикаций через запятую. Результат сохраняется в новом CSV-файле.

`find_year_by_publication_id(publication_id)` - Функция находит год публикации по указанному идентификатору публикации в CSV-файле.

Результат этого проекта - файлы в директории `./Data/`