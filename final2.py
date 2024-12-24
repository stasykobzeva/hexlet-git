from http.server import BaseHTTPRequestHandler, HTTPServer
import json
from requests import get, post

def run(handler_class=BaseHTTPRequestHandler):
    server_address = ('', 8010)
    httpd = HTTPServer(server_address, handler_class)
    #print("Я работаю")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        httpd.server_close()


def tasks_reading():
    try:
        with open('tasks.txt', 'r') as file:
            return [
    Task(
        task_data['title'],
        task_data['priority'],
        task_data['id'],
        task_data['isDone']
    )
    for line in file
    if (task_data := json.loads(line.strip())) ]
    except FileNotFoundError:
        return []


def write_to_file(tasks):
    with open('tasks.txt', 'w') as file:
        file.write("\n".join([task.to_json() for task in tasks]))


class Task:
    def __init__(self, title, priority, id, isDone=False):
        self.title = title
        self.priority = priority
        self.isDone = isDone
        self.id = id

    def to_json(self):
        return json.dumps({"title" : self.title, "priority" : self.priority, "isDone" : self.isDone, "id" : self.id})


class TaskServer(BaseHTTPRequestHandler):
    tasks = tasks_reading()
    n_id = 1

    if (tasks):
        n_id = max(task.id for task in tasks) + 1

    def do_GET(self): # получаем список задач
        if self.path == '/tasks':
            self.get_list()

    def do_POST(self):
        if self.path == '/tasks':
            print("a")
            self.task_creatinon()


        elif self.path.startswith('/tasks/'):
            self.task_marking()


    def task_creatinon(self):
        content_len = int(self.headers['Content-Length']) # длина тела запроса
        post_data = self.rfile.read(content_len) # считываем столько же байтов
        

        try:
            data = json.loads(post_data) # json ответ преобразовывается в словарьs
            title = data.get('title') # поле title
            priority = data.get('priority') # поле priority

            if not title or not priority: # проверка наличия обязательных полей
                raise ValueError("нет поля 'title' и/или 'priority'")

            task = Task(title, priority, TaskServer.n_id) # создается экземпляр задачи
            TaskServer.tasks.append(task) # добавляется в список
            TaskServer.n_id += 1 # уникальный номер для следующей задачи +1
            assert(task.isDone == False)
            write_to_file(TaskServer.tasks)

            self.send_response(201) # создано
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(task.to_json().encode())

        except (json.JSONDecodeError, ValueError):
            self.send_response(400)



    def get_list(self):
        self.send_response(200) # успещно
        self.send_header('Content-type', 'application/json')
        self.end_headers()

        tasks_json = [task.to_json() for task in TaskServer.tasks]
        self.wfile.write((f"[{', '.join(tasks_json)}]").encode())

    def task_marking(self):
        ur_elems = self.path.split('/')

        if (len(ur_elems) <= 2):
            self.send_response(400)
            return
        try:
            ur_id = int(ur_elems[2])
        except Exception as e:
            self.send_response(400)
            return
        
        task = None

        for cur_task in TaskServer.tasks:
            if cur_task.id == ur_id:
                task = cur_task

        if task is None:
                self.send_response(404)
        else:
            task.isDone = True
            write_to_file(TaskServer.tasks)
            self.send_response(200)
        self.end_headers()





    



    




run(handler_class=TaskServer)