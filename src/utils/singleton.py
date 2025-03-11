"""
Singleton pattern implementation.

This module provides a metaclass for implementing the Singleton pattern.
"""

from typing import Any, Dict, Type


class Singleton(type):
    """
    Metaclass for implementing the Singleton pattern.
    
    This metaclass ensures that only one instance of a class exists.
    """
    
    _instances: Dict[Type, Any] = {}
    
    def __call__(cls, *args: Any, **kwargs: Any) -> Any:
        """
        Return the singleton instance of the class.
        
        If an instance doesn't exist, it is created and stored.
        
        Args:
            args: Positional arguments for the class constructor
            kwargs: Keyword arguments for the class constructor
            
        Returns:
            The singleton instance
        """
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]