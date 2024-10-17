from collections import OrderedDict

class LRUCache:
    def __init__(self, capacity: int):
        """
        Initialize the cache with a given capacity.
        Both keys and values are expected to be strings.
        """
        self.cache = OrderedDict()
        self.capacity = capacity

    def get(self, key: str) -> str:
        """
        Retrieve the value for the given key if present in the cache.
        If the key is not found, return an empty string.
        """
        if key not in self.cache:
            return ""  # Key not found
        # Move the key to the end to mark it as recently used
        self.cache.move_to_end(key)
        return self.cache[key]

    def set(self, key: str, value: str) -> None:
        """
        Add a new key-value pair to the cache. If the cache exceeds its capacity,
        the least recently used entry is removed.
        """
        if key in self.cache:
            # If key exists, move it to the end (recently used)
            self.cache.move_to_end(key)
        self.cache[key] = value  # Add or update the value

        # If the cache exceeds capacity, remove the least recently used item
        if len(self.cache) > self.capacity:
            self.cache.popitem(last=False)

    def get_all_keys(self) -> list:
        """
        Return a list of all keys currently contained in the cache.
        """
        return list(self.cache.keys())