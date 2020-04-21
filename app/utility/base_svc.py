import logging
import datetime


class BaseService:

    _services = dict()

    def add_service(self, name, svc):
        self.__class__._services[name] = svc
        return self.create_logger(name)

    @classmethod
    def get_service(cls, name):
        return cls._services.get(name)

    @classmethod
    def get_services(cls):
        return cls._services

    @staticmethod
    def create_logger(name):
        return logging.getLogger(name)

    @staticmethod
    def get_current_timestamp(date_format='%Y-%m-%d %H:%M:%S'):
        return datetime.now().strftime(date_format)