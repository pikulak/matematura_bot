#!C:/Python34/python.exe

import requests
from bs4 import BeautifulSoup
from time import sleep

login_url = "https://matematura.gwo.pl/users/login"
exams_url = "https://matematura.apps.gwo.pl/app_data/c6ba7e4cd9f3/examSets/sets"
new_exam_url = "https://matematura.apps.gwo.pl/app_data/c6ba7e4cd9f3/examSets/generateSet"
finish_exam_url = "https://matematura.apps.gwo.pl/app_data/c6ba7e4cd9f3/examSets/finishSet"
exam_report_url = "https://matematura.apps.gwo.pl/app_data/c6ba7e4cd9f3/examSets/setReport/1"
my_apps_url = "https://matematura.gwo.pl/users/myGwo/tab:my_apps/subtab:7"
exam_url = "https://matematura.apps.gwo.pl/app_data/c6ba7e4cd9f3/examSets/testAll"
save_all_url = "https://matematura.apps.gwo.pl/app_data/c6ba7e4cd9f3/examSets/saveAll"
exam_repeat_url = "https://matematura.apps.gwo.pl/app_data/c6ba7e4cd9f3/examSets/setRepeat/1"
login_data = {
	"login": "LO3iuczen17",
	"password": "SECURED",
	"moveon": "/"}

session = requests.Session()
solutions = {}

def login(session):
	session.post(login_url, login_data)

def go_to_my_apps(session):
	return session.get(my_apps_url)

def go_to_list_exams(session):
	apps = go_to_my_apps(session).text
	bs = BeautifulSoup(apps, "html5lib")
	run_url = "https://" + bs.find("div", class_="button-kafelka").a.get("href")[2:]
	session.get(run_url)
	exams = session.get(exams_url).text
	return exams

def generate_new_exam(session):
	session.get(new_exam_url)

def finish_exam(session):
	session.get(finish_exam_url)

def get_report(session):
	return session.get(exam_report_url).text

def is_solution(choice):
	img = choice.find("img", {"alt": "box"})
	if "green" in img.get("src"):
		return True

def get_solution(exercise_bs):
	try:
		solutions_table = exercise_bs.find("table")
		choices = solutions_table.find_all("tr")
		for i, choice in enumerate(choices):
			if is_solution(choice):
				return i + 1
	except AttributeError:
		return False


def parse_report(session):
	report_view = get_report(session)
	bs = BeautifulSoup(report_view, "html5lib")
	cont_exercise = bs.find("div", id="cont-exercise")
	cont_all_exercises = cont_exercise.find_all("div", class_="exercise-content")
	for no, exercise in enumerate(cont_all_exercises):
		solutions[no + 1] = get_solution(exercise)

def get_exam(session):
	return session.get(exam_url).text

def parse_answer(exercise, exercise_id):
	try:
		post_data = {}
		solution = solutions[exercise_id]
		choice = exercise.find_all("input", {"class": "sinput"})[solution - 1]
	except IndexError:
		return False

	post_data[choice.get("name")] = choice.get("value")
	for field in exercise.find_all("input", {"type": "hidden"}):
		post_data[field.get("name")] = field.get("value")

	return post_data

def save_answer(session, answer_data):
	session.post(save_all_url, answer_data)

def do_exam(session):
	exam = get_exam(session)
	exercises = BeautifulSoup(exam, "html5lib").find_all("form", {"name": "f_solution"})
	for exercise_id, exercise in enumerate(exercises):
		answer_data = parse_answer(exercise, exercise_id + 1)
		if answer_data:
			save_answer(session, answer_data)


def repeat_exam(session):
	session.get(exam_repeat_url)

login(session)
go_to_list_exams(session)
for i in range(5):
	print("Egzamin nr:", i + 1)
	generate_new_exam(session)
	finish_exam(session)
	parse_report(session)
	repeat_exam(session)
	do_exam(session)
	finish_exam(session)
	solutions = {}