import __main__
def is_map_manager_running() -> bool:
    return any(
        t.name == "map_manager" and t.is_alive()
        for t in __main__.threading.enumerate()
    )
