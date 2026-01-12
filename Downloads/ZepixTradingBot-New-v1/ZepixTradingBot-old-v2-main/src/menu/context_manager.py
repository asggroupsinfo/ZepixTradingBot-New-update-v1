"""
User Context Manager for Menu System
Stores user's current menu state and selected parameters
"""
from typing import Dict, Any, Optional
import time

class ContextManager:
    """
    Manages user context for multi-step command execution
    Stores current menu, pending command, and selected parameters
    """
    
    def __init__(self, expiration_minutes: int = 30):
        self.user_contexts: Dict[int, Dict[str, Any]] = {}
        self.context_expiration: Dict[int, float] = {}  # user_id -> expiration timestamp
        self.expiration_minutes = expiration_minutes
    
    def get_context(self, user_id: int) -> Dict[str, Any]:
        """Get user's current context"""
        # Check expiration
        if self._is_expired(user_id):
            self.clear_context(user_id)
        
        context = self.user_contexts.get(user_id, {
            "current_menu": "menu_main",
            "pending_command": None,
            "params": {},
            "menu_history": [],
            "created_at": time.time()
        })
        
        # CRITICAL FIX: Ensure params always exists (never return None)
        if "params" not in context:
            context["params"] = {}
        
        return context
    
    def set_context(self, user_id: int, context: Dict[str, Any]):
        """Set user's context - preserves existing params unless explicitly cleared"""
        # Preserve existing params if not explicitly cleared
        old_context = self.user_contexts.get(user_id)
        if old_context and "params" in old_context and old_context["params"]:
            # Only preserve if new context doesn't have params or has empty params
            if "params" not in context or not context.get("params"):
                context["params"] = old_context["params"].copy()
        
        # Ensure params always exists
        if "params" not in context:
            context["params"] = {}
        
        context["created_at"] = time.time()
        context.setdefault("last_updated", time.time())
        context["last_updated"] = time.time()
        self.user_contexts[user_id] = context
        self._update_expiration(user_id)
    
    def update_context(self, user_id: int, **updates):
        """Update specific fields in user's context - merges params instead of replacing"""
        context = self.get_context(user_id)
        
        # Special handling for params: merge instead of replace
        if "params" in updates and isinstance(updates["params"], dict):
            existing_params = context.get("params", {})
            existing_params.update(updates["params"])
            updates["params"] = existing_params
        
        context.update(updates)
        self.set_context(user_id, context)
    
    def add_param(self, user_id: int, param_name: str, param_value: Any):
        """Add a parameter to user's context"""
        context = self.get_context(user_id)
        if "params" not in context:
            context["params"] = {}
        context["params"][param_name] = param_value
        self.set_context(user_id, context)
    
    def get_param(self, user_id: int, param_name: str) -> Optional[Any]:
        """Get a parameter from user's context"""
        context = self.get_context(user_id)
        return context.get("params", {}).get(param_name)
    
    def clear_params(self, user_id: int):
        """Clear all parameters from user's context"""
        context = self.get_context(user_id)
        context["params"] = {}
        self.set_context(user_id, context)
    
    def push_menu(self, user_id: int, menu_name: str):
        """Push menu to history stack"""
        context = self.get_context(user_id)
        if "menu_history" not in context:
            context["menu_history"] = []
        context["menu_history"].append(context.get("current_menu", "menu_main"))
        context["current_menu"] = menu_name
        self.set_context(user_id, context)
    
    def pop_menu(self, user_id: int) -> Optional[str]:
        """Pop menu from history stack and return previous menu"""
        context = self.get_context(user_id)
        if "menu_history" not in context or not context["menu_history"]:
            return "menu_main"
        
        previous_menu = context["menu_history"].pop()
        context["current_menu"] = previous_menu
        self.set_context(user_id, context)
        return previous_menu
    
    def clear_context(self, user_id: int):
        """Clear all context for user"""
        if user_id in self.user_contexts:
            del self.user_contexts[user_id]
        if user_id in self.context_expiration:
            del self.context_expiration[user_id]
    
    def _update_expiration(self, user_id: int):
        """Update expiration timestamp for user context"""
        self.context_expiration[user_id] = time.time() + (self.expiration_minutes * 60)
    
    def _is_expired(self, user_id: int) -> bool:
        """Check if user context has expired"""
        if user_id not in self.context_expiration:
            return False
        return time.time() > self.context_expiration[user_id]
    
    def cleanup_expired_contexts(self):
        """Clean up all expired contexts"""
        expired_users = [uid for uid in self.context_expiration.keys() if self._is_expired(uid)]
        for user_id in expired_users:
            self.clear_context(user_id)
    
    def recover_context(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Attempt to recover context from partial failure"""
        context = self.get_context(user_id)
        
        # If context exists but seems incomplete, try to recover
        if context.get("pending_command") and not context.get("params"):
            # Command was selected but no params collected - reset
            context["pending_command"] = None
            self.set_context(user_id, context)
            return context
        
        return context
    
    def set_pending_command(self, user_id: int, command: str):
        """Set pending command for user"""
        self.update_context(user_id, pending_command=command)
    
    def get_pending_command(self, user_id: int) -> Optional[str]:
        """Get pending command for user"""
        context = self.get_context(user_id)
        return context.get("pending_command")
    
    def clear_pending_command(self, user_id: int):
        """Clear pending command for user"""
        self.update_context(user_id, pending_command=None)
    
    def preserve_params(self, user_id: int, new_context: Dict[str, Any]):
        """Preserve existing parameters when updating context"""
        old_context = self.get_context(user_id)
        if "params" in old_context and old_context["params"]:
            new_context["params"] = old_context["params"].copy()
        self.set_context(user_id, new_context)
    
    def get_all_params(self, user_id: int) -> Dict[str, Any]:
        """Get all parameters for debugging"""
        context = self.get_context(user_id)
        return context.get("params", {}).copy()

