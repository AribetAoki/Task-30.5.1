import chromedriver_autoinstaller
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

chromedriver_autoinstaller.install()


@pytest.fixture(autouse=True)
def web_driver():
    driver = webdriver.Chrome()
    driver.implicitly_wait(3)
    # Переходим на страницу авторизации
    driver.get('https://petfriends.skillfactory.ru/login')
    driver.maximize_window()
    yield driver
    driver.quit()


def test_show_all_pets(web_driver):
    # Вводим email, заменить на свой email для того чтобы получить свой список питомцев
    web_driver.find_element(By.ID, 'email').send_keys('slavovna@rb.ru')
    # Вводим пароль
    web_driver.find_element(By.ID, 'pass').send_keys('123456')
    # Нажимаем на кнопку входа в аккаунт
    web_driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()
    # Проверяем, что мы оказались на главной странице пользователя
    assert web_driver.find_element(By.TAG_NAME, 'h1').text == "PetFriends"

    images = web_driver.find_elements(By.CSS_SELECTOR, '.card.card-img-top')
    names = web_driver.find_elements(By.CSS_SELECTOR, '.card-body.card-title')
    descriptions = web_driver.find_elements(By.CSS_SELECTOR, '.card-body.card-text')

    for i in range(len(names)):
        assert images[i].get_attribute('src') != ''
        assert names[i].text != ''
        assert descriptions[i].text != ''
        assert ', ' in descriptions[i]
        parts = descriptions[i].text.split(", ")
        assert len(parts[0]) > 0
        assert len(parts[1]) > 0


def test_show_my_pets(web_driver):
    wait = WebDriverWait(web_driver, 5).until(EC.presence_of_element_located((By.ID, 'email')))
    web_driver.find_element(By.ID, 'email').send_keys('slavovna@rb.ru')
    # Вводим пароль
    web_driver.find_element(By.ID, 'pass').send_keys('123456')
    # Нажимаем на кнопку входа в аккаунт
    web_driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()
    # Проверяем, что мы оказались на главной странице пользователя
    # Проверяем, что мы оказались на главной странице сайта.
    assert web_driver.find_element(By.TAG_NAME, 'h1').text == "PetFriends"
    # Ожидаем в течение 5с, что на странице есть тег h1 с текстом "PetFriends"
    # Открываем страницу /my_pets.
    web_driver.find_element(By.CSS_SELECTOR, 'a[href="/my_pets"]').click()

    # Проверяем, что мы оказались на  странице пользователя.
    # Ожидаем на странице есть тег h2 с текстом имени пользователя
    wait.until(EC.text_to_be_present_in_element((By.TAG_NAME, 'h2'), "Yana Azarova"))

    class element_has_css_class(object):
        def __init__(self, locator, css_class):
            self.locator = locator
            self.css_class = css_class

        def __call__(self, driver):
            element = driver.find_element(*self.locator)
            if self.css_class in element.get_attribute("class"):
                return element
            else:
                return False

    css_locator = 'tbody>tr'
    data_my_pets = web_driver.find_element(By.CSS_SELECTOR, css_locator)

    # Ожидаем, что данные всех питомцев, найденных локатором css_locator = 'tbody>tr', видны на странице:
    for i in range(len(data_my_pets)):
        wait.until(EC.visibility_of(data_my_pets[i]))

    # Ищем в теле таблицы все фотографии питомцев и ожидаем, что все загруженные фото, видны на странице:
    image_my_pets = web_driver.find_element(By.CSS_SELECTOR, 'img[style="max-width: 100px; max-height: 100px;"]')
    for i in range(len(image_my_pets)):
        if image_my_pets[i].get_attribute('src') != '':
            wait.until(EC.visibility_of(image_my_pets[i]))

    # Ищем в теле таблицы все имена питомцев и ожидаем увидеть их на странице:
    name_my_pets = web_driver.find_element(By.XPATH, '//tbody/tr/td[1]')
    for i in range(len(name_my_pets)):
        wait.until(EC.visibility_of(name_my_pets[i]))

    # Ищем в теле таблицы все породы питомцев и ожидаем увидеть их на странице:
    type_my_pets = web_driver.find_element(By.XPATH, '//tbody/tr/td[2]')
    for i in range(len(type_my_pets)):
        wait.until(EC.visibility_of(type_my_pets[i]))

        # Ищем в теле таблицы все данные возраста питомцев и ожидаем увидеть их на странице:
        age_my_pets = web_driver.find_element(By.XPATH, '//tbody/tr/td[3]')
        for i in range(len(age_my_pets)):
            wait.until(EC.visibility_of(age_my_pets[i]))

        # Ищем на странице /my_pets всю статистику пользователя,
        # и вычленяем из полученных данных количество питомцев пользователя:
        pets_number = web_driver.find_element(By.XPATH, '//div[@class=".col-sm-4 left"]').text.split('\n')[1].split(': ')[1]
        pets_count = web_driver.find_elements(By.XPATH, '//table[@class="table table-hover"]/tbody/tr')

        # Проверяем, что количество строк в таблице с моими питомцами равно общему количеству питомцев,
        # указанному в статистике пользователя:
        assert int(pets_number) == len(pets_count)

        # Проверяем, что хотя бы у половины питомцев есть фото:
        m = 0
        for i in range(len(image_my_pets)):
            if image_my_pets[i].get_attribute('src') != '':
                m += 1
        assert m >= pets_count / 2

        # Проверяем, что у всех питомцев есть имя:
        for i in range(len(name_my_pets)):
            assert name_my_pets[i].text != ''

        # Проверяем, что у всех питомцев есть порода:
        for i in range(len(type_my_pets)):
            assert type_my_pets[i].text != ''

        # Проверяем, что у всех питомцев есть возраст:
        for i in range(len(age_my_pets)):
            assert age_my_pets[i].text != ''

        # Проверяем, что у всех питомцев разные имена:
        list_name_my_pets = []
        for i in range(len(name_my_pets)):
            list_name_my_pets.append(name_my_pets[i].text)
        set_name_my_pets = set(list_name_my_pets)  # преобразовываем список в множество
        assert len(list_name_my_pets) == len(
            set_name_my_pets)  # сравниваем длину списка и множества: без повторов должны совпасть

        # Проверяем, что в списке нет повторяющихся питомцев:
        list_data_my_pets = []
        for i in range(len(data_my_pets)):
            list_data = data_my_pets[i].text.split("\n")  # отделяем от данных питомца "х" удаления питомца
            list_data_my_pets.append(list_data[0])  # выбираем элемент с данными питомца и добавляем его в список
        set_data_my_pets = set(list_data_my_pets)  # преобразовываем список в множество
        assert len(list_data_my_pets) == len(
            set_data_my_pets)  # сравниваем длину списка и множества: без повторов должны совпасть
