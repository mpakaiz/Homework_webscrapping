import requests
import re
from fake_headers import Headers
import bs4
import json
from concurrent.futures import ThreadPoolExecutor
import time

headers = Headers(browser='firefox', os='win')
headers_data = headers.generate()

# def get_page(page_number):
#
#     return requests.get(f"https://spb.hh.ru/search/vacancy?text=python&area=1&area=2&page={page_number}"
#                         f"&hhtmFrom=vacancy_search_list", headers=headers_data).text


def get_vacancies():
    page_number = 0

    vac_info_list = []
    while page_number <5:
        link_search = f"https://spb.hh.ru/search/vacancy?text=python&area=1&area=2&page={page_number}" \
                      f"&hhtmFrom=vacancy_search_list"
        main_html = requests.get(link_search, headers=headers_data).text
        # with ThreadPoolExecutor(max_workers=2) as pool:
        #     results = pool.map(get_page, range(1, 6))
        #     for item in results:
        #         return item
        main_soup = bs4.BeautifulSoup(main_html, 'lxml')
        div_main_content = main_soup.find('div', id="HH-React-Root")
        vacancies = div_main_content.find('main', class_="vacancy-serp-content")
        vacancy_list = vacancies.find_all('div', class_='serp-item')

        for i in vacancy_list:
            vacancy_list_link = i.find('a', class_="serp-item__title")
            link = vacancy_list_link['href']
            time.sleep(0.5)
            vacancy_inside_html = requests.get(link, headers=headers_data).text
            vacancy_inside_soup = bs4.BeautifulSoup(vacancy_inside_html, 'lxml')
            vacancy_description = vacancy_inside_soup.find('div', class_="vacancy-description")
            vacancy_description_text = vacancy_description.text

            pattern_skill = r'^.*(Django).*(Flask).*|.*(Flask).*(Django).*'
            g = re.match(pattern_skill, vacancy_description_text)
            if g:
                vacancy_title = vacancy_inside_soup.find('div', class_="vacancy-title")
                vacancy_salary = vacancy_title.find('span', class_="bloko-header-section-2 bloko-header-section-2_lite")

                if vacancy_salary:
                    vacancy_salary_text = vacancy_salary.text.replace('\xa0', '')
                else:
                    vacancy_salary_text = 'Зарплата не указана'
                vacancy_company = vacancy_inside_soup.find('div', class_="vacancy-company-details")
                vacancy_company_details = vacancy_company.find('span',
                                                               class_="bloko-header-section-2 bloko-header-section-2_lite")
                vacancy_company_details_text = vacancy_company_details.text.replace('\xa0', '')
                vacancy_city = vacancy_inside_soup.find('a',
                                                        class_="bloko-link bloko-link_kind-tertiary"
                                                               " bloko-link_disable-visited")
                if vacancy_city:
                    vacancy_city_text = vacancy_city.text
                    pattern_city = r'^\w+'
                    vacancy_city_details = (re.match(pattern_city, vacancy_city_text)).group()
                else:
                    vacancy_city_details = "Город не указан"

                vac_info = {
                    "link": link,
                    "salary": vacancy_salary_text,
                    "company_name": vacancy_company_details_text,
                    "city": vacancy_city_details
                }
                vac_info_list.append(vac_info)
        page_number += 1
        time.sleep(0.5)

    with open("vacancies_full.json", 'w', encoding='utf-8') as f:
        json.dump(vac_info_list, f, ensure_ascii=False)

if __name__ == "__main__":
    start = time.perf_counter()
    get_vacancies()
    end = time.perf_counter()
    print(f'Time taken is {end - start}')