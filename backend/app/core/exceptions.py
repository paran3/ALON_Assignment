class AppException(Exception):
    pass


class UnregisteredSensorError(AppException):
    def __init__(self, serial_number: str):
        self.serial_number = serial_number
        super().__init__(f"{serial_number}: unregistered sensor")


class SensorNotFoundError(AppException):
    def __init__(self, serial_number: str):
        self.serial_number = serial_number
        super().__init__(f"Sensor not found: {serial_number}")


class SensorAlreadyExistsError(AppException):
    def __init__(self, serial_number: str):
        self.serial_number = serial_number
        super().__init__(f"Sensor already registered: {serial_number}")


class TaskNotFoundError(AppException):
    def __init__(self, task_id: str):
        self.task_id = task_id
        super().__init__(f"Task not found: {task_id}")


class DataProcessingError(AppException):
    def __init__(self, serial_number: str, detail: str):
        self.serial_number = serial_number
        super().__init__(f"{serial_number}: {detail}")
