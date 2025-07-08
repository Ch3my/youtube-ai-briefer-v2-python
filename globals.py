class SingletonMeta(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]

class Globals(metaclass=SingletonMeta):
    bm25_retriever = None
    faiss_vectorstore = None
    store = {}
    chat_id = ""
    connected_clients = set()
    app_data_dir = None