import pytest
from rest_framework.test import APIClient
from model_bakery import baker

from django_testing.settings import MAX_STUDENTS_PER_COURSE
from students.models import Course, Student


# заведите фикстуры для API клиента
@pytest.fixture
def client():
    return APIClient()


@pytest.fixture
def course():
    return Course.objects.create(name='course 1')


# Заведите фикстуры для фабрики курсов
@pytest.fixture
def course_factory():
    def factory(*args, **kwargs):
        return baker.make(Course, *args, **kwargs)

    return factory


# Заведите фикстуры для фабрики студентов
@pytest.fixture
def student_factory():
    def factory(*args, **kwargs):
        return baker.make(Student, *args, **kwargs)

    return factory


# фикстура для кол-ва студентов
@pytest.fixture
def settings() -> int:

    max_students_per_course = MAX_STUDENTS_PER_COURSE
    return max_students_per_course


# тест успешного получения первого курса  и его названия + тест API
@pytest.mark.django_db
def test_get_first_course(client, course_factory, student_factory):
    # Arrange
    courses = course_factory(_quantity=10)

    # Act
    response = client.get('/courses/', {'id': courses[0].id})
    data = response.json()

    # Assert
    assert response.status_code == 200
    assert data[0]['id'] == courses[0].id
    assert data[0]['name'] == courses[0].name


# тест успешного получения списка курсов  + названий курсов + тест API
@pytest.mark.django_db
def test_get_courses_list(client, course_factory):
    # Arrange
    courses = course_factory(_quantity=10)

    # Act
    response = client.get('/courses/')
    data = response.json()

    # Assert
    assert response.status_code == 200
    assert len(data) == len(courses)
    for i, m in enumerate(data):
        assert m['name'] == courses[i].name
        assert m['id'] == courses[i].id


# проверка фильтрации списка курсов по id + тест API
@pytest.mark.django_db
def test_filter_courses_id(client, course_factory):
    # Arrange
    courses = course_factory(_quantity=10)
    id = courses[0].id

    # Act
    response = client.get(f'/courses/?id={id}')
    data = response.json()

    # Assert
    assert response.status_code == 200
    assert data[0]['name'] == courses[0].name


# проверка фильтрации списка курсов по name + тест API
@pytest.mark.django_db
def test_filter_courses_name(client, course_factory):
    # Arrange
    courses = course_factory(_quantity=10)
    name = courses[0].name

    # Act
    response = client.get(f'/courses/?name={name}')
    data = response.json()

    # Assert
    assert response.status_code == 200
    assert data[0]['id'] == courses[0].id


# проверка создания курса + тест API
@pytest.mark.django_db
def test_create_course(client, course_factory):
    # Arrange
    count = Course.objects.count()

    # Act
    response = client.post('/courses/', data={'name': 'курс 1'})

    # Assert
    assert response.status_code == 201
    assert Course.objects.count() == count + 1


# проверка обновления курса + тест API
@pytest.mark.django_db
def test_update_course(client, course_factory):
    # Arrange
    courses = course_factory(_quantity=10)
    id = courses[0].id
    new_name = 'Новый курс'

    # Act
    update_response = client.patch(f'/courses/?id={id}', data={'name': new_name})
    response = client.get(f'/courses/?id={id}')
    data = response.json()

    # Assert
    assert response.status_code == 200
    assert data[0]['name'] == courses[0].name


@pytest.mark.django_db
def test_delete_course(client, course_factory):
    # Arrange
    courses = course_factory(_quantity=10)
    id = courses[0].id
    count = Course.objects.count()

    # Act
    response = client.delete(f'/courses/{id}/')

    # Assert
    assert response.status_code == 204
    assert Course.objects.count() == count - 1


# тестирование кол-ва студентов на курсе без settings
# @pytest.mark.django_db
# def test_student_number(client, student_factory):
#     # Arrange
#     max_students_per_course = 20
#     students = student_factory(_quantity=20)
#     students_ids = []
#     for student in students:
#         students_ids.append(student.id)
#     json_data = {'name': 'Курс 1', 'students': students_ids}
#
#     # Act
#     post_response = client.post('/courses/', data=json_data)
#
#     # Assert
#     assert post_response.status_code == 201
#     assert max_students_per_course == Student.objects.count()

# тестирование кол-ва студентов на курсе c settings
@pytest.mark.django_db
def test_student_number(client, student_factory, settings):
    # Arrange
    students = student_factory(_quantity=10)
    students_ids = []
    for student in students:
        students_ids.append(student.id)
    json_data = {'name': 'Курс 1', 'students': students_ids}

    # Act
    post_response = client.post('/courses/', data=json_data)

    # Assert
    assert post_response.status_code == 201
    assert settings == Student.objects.count()
