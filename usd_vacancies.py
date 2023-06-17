import requests
import re
from fake_headers import Headers
import bs4
import json

headers = Headers(browser='firefox', os='win')
headers_data = headers.generate()


def get_vacancies():
    main_html = requests.get("https://spb.hh.ru/search/vacancy?text=python&area=1&area=2", headers=headers_data).text
    main_soup = bs4.BeautifulSoup(main_html, 'lxml')

    div_main_content = main_soup.find('div', id="HH-React-Root")
    vacancies = div_main_content.find('main', class_="vacancy-serp-content")
    vacancy_list = vacancies.find_all('div', class_='serp-item')
    vac_info_list = []
    for i in vacancy_list:
        vacancy_list_link = i.find('a', class_="serp-item__title")
        link = vacancy_list_link['href']
        vacancy_inside_html = requests.get(link, headers=headers_data).text
        vacancy_inside_soup = bs4.BeautifulSoup(vacancy_inside_html, 'lxml')
        vacancy_description = vacancy_inside_soup.find('div', class_="vacancy-description")
        vacancy_description_text = vacancy_description.text

        pattern_skill = r'^.*(Django).*(Flask).*|.*(Flask).*(Django).*'
        g = re.match(pattern_skill, vacancy_description_text)
        if g:
            vacancy_title = vacancy_inside_soup.find('div', class_="vacancy-title")
            vacancy_salary = vacancy_title.find('span', class_="bloko-header-section-2 bloko-header-section-2_lite")
            pattern_usd_salary = r'^.*(USD).*'
            if vacancy_salary:
                check_usd = re.match(pattern_usd_salary, vacancy_salary.text)
                if check_usd:
                    vacancy_salary_text = vacancy_salary.text.replace('\xa0', '')
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
                else:
                    pass
            else:
                pass
    with open("vacancies_usd.json", 'w', encoding='utf-8') as f:
        json.dump(vac_info_list, f, ensure_ascii=False)


if __name__ == "__main__":
    get_vacancies()
