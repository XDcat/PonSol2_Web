from concurrent.futures.thread import ThreadPoolExecutor


class ThreadPool:
    def __init__(self, max_thread=10):
        self.executor = ThreadPoolExecutor(max_thread)  # thread pool
        self.future_dict = {}  # task list

    def is_project_thread_running(self, task_id):
        """check whether the task of task_id is running"""
        future = self.future_dict.get(task_id, None)
        if future and future.running():
            return True
        else:
            return False

    def check_future(self):
        """
        check the status of all tasks
            1. if the task is running, add it in a list and return
            2. if the task is done, remove it from self.future_dict
        """
        data = []
        for task_id, future in list(self.future_dict.items()):
            if self.is_project_thread_running(task_id):
                data.append(task_id)
            else:
                self.future_dict.pop(task_id)
        return data

    def add_task(self, task_id, fun, *args, **kwargs):
        """ add one predict task into thread pool"""
        self.check_future()
        future = self.executor.submit(fun, *args, **kwargs)
        self.future_dict[task_id] = future

    def __del__(self):
        self.executor.shutdown()


# global thread pool
global_thread_pool = ThreadPool(10)  # 普通预测任务
global_protein_all_thread_pool = ThreadPool(2)  # 全序列预测任务

global_mail_thread_pool = ThreadPool(max_thread=1)  # 发送邮件
