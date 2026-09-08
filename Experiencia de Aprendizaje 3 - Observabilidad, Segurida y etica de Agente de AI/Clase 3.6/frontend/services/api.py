import requests

CATEGORY_EMOJI = {
    "trabajo": "🔵",
    "salud": "🟢",
    "familia": "🟡",
    "dinero": "🟠",
    "casa": "🔴",
    "ocio": "🟣",
    "autocuidado": "🩷",
    "amor": "❤️",
}

CATEGORIES = list(CATEGORY_EMOJI.keys())
STATUSES = ["todo", "doing", "done"]
IMPORTANCES = ["low", "high"]


class TaskAPI:
    def __init__(self, base_url: str):
        self.base_url = base_url

    def get_tasks(self, status=None, category=None, importance=None):
        params = {}
        if status:
            params["status"] = status
        if category:
            params["category"] = category
        if importance:
            params["importance"] = importance
        r = requests.get(f"{self.base_url}/tasks/", params=params)
        r.raise_for_status()
        return r.json()

    def create_task(self, data: dict):
        r = requests.post(f"{self.base_url}/tasks/", json=data)
        r.raise_for_status()
        return r.json()

    def update_task(self, task_id: int, data: dict):
        r = requests.put(f"{self.base_url}/tasks/{task_id}", json=data)
        r.raise_for_status()
        return r.json()

    def patch_status(self, task_id: int, status: str):
        r = requests.patch(f"{self.base_url}/tasks/{task_id}/status", json={"status": status})
        r.raise_for_status()
        return r.json()

    def delete_task(self, task_id: int):
        r = requests.delete(f"{self.base_url}/tasks/{task_id}")
        r.raise_for_status()

    def get_matrix(self):
        r = requests.get(f"{self.base_url}/analytics/matrix")
        r.raise_for_status()
        return r.json()

    def get_weekly(self):
        r = requests.get(f"{self.base_url}/analytics/weekly")
        r.raise_for_status()
        return r.json()


api = TaskAPI(base_url="http://localhost:8000")
