"""
Module to patch plankapy library to handle extra fields in API responses.
"""

import logging
from plankapy.models import Project_, User_, Board_, List_, Card_

logger = logging.getLogger(__name__)


def patch_plankapy():
    """
    Patch plankapy library to handle extra fields in API responses.
    
    The Planka API returns more fields than the dataclass definitions in plankapy,
    which causes instantiation errors. This patch modifies the classes to accept
    and store extra fields as attributes.
    """
    
    try:
        # Save the original __init__ methods
        original_project_init = Project_.__init__
        original_user_init = User_.__init__
        original_board_init = Board_.__init__
        original_list_init = List_.__init__
        original_card_init = Card_.__init__
        
        # Monkey patch the Project_ class to handle extra fields
        def patched_project_init(self, **kwargs):
            # Filter out extra fields that aren't part of the dataclass
            allowed_fields = {
                'id', 'name', 'background', 'backgroundImage', 
                'createdAt', 'updatedAt'
            }
            filtered_kwargs = {k: v for k, v in kwargs.items() if k in allowed_fields}
            
            # Call the original __init__ with only allowed fields
            original_project_init(self, **filtered_kwargs)
            
            # Store extra fields as attributes
            for k, v in kwargs.items():
                if k not in allowed_fields:
                    setattr(self, k, v)
        
        # Monkey patch the User_ class to handle extra fields
        def patched_user_init(self, **kwargs):
            # Filter out extra fields that aren't part of the dataclass
            allowed_fields = {
                'id', 'name', 'username', 'email', 'language', 'organization', 'phone',
                'avatarUrl', 'isSso', 'isAdmin', 'isDeletionLocked', 'isLocked',
                'isRoleLocked', 'isUsernameLocked', 'subscribeToOwnCards',
                'createdAt', 'updatedAt', 'deletedAt'
            }
            filtered_kwargs = {k: v for k, v in kwargs.items() if k in allowed_fields}
            
            # Call the original __init__ with only allowed fields
            original_user_init(self, **filtered_kwargs)
            
            # Store extra fields as attributes
            for k, v in kwargs.items():
                if k not in allowed_fields:
                    setattr(self, k, v)
        
        # Monkey patch the Board_ class to handle extra fields
        def patched_board_init(self, **kwargs):
            # Filter out extra fields that aren't part of the dataclass
            allowed_fields = {
                'id', 'name', 'position', 'projectId', 'createdAt', 'updatedAt'
            }
            filtered_kwargs = {k: v for k, v in kwargs.items() if k in allowed_fields}
            
            # Call the original __init__ with only allowed fields
            original_board_init(self, **filtered_kwargs)
            
            # Store extra fields as attributes
            for k, v in kwargs.items():
                if k not in allowed_fields:
                    setattr(self, k, v)
        
        # Monkey patch the List_ class to handle extra fields
        def patched_list_init(self, **kwargs):
            # Filter out extra fields that aren't part of the dataclass
            allowed_fields = {
                'id', 'name', 'position', 'boardId', 'color', 'createdAt', 'updatedAt'
            }
            filtered_kwargs = {k: v for k, v in kwargs.items() if k in allowed_fields}
            
            # Call the original __init__ with only allowed fields
            original_list_init(self, **filtered_kwargs)
            
            # Store extra fields as attributes
            for k, v in kwargs.items():
                if k not in allowed_fields:
                    setattr(self, k, v)
        
        # Monkey patch the Card_ class to handle extra fields
        def patched_card_init(self, **kwargs):
            # Filter out extra fields that aren't part of the dataclass
            allowed_fields = {
                'id', 'name', 'position', 'description', 'dueDate', 'isDueDateCompleted',
                'stopwatch', 'boardId', 'listId', 'creatorUserId', 'coverAttachmentId',
                'isSubscribed', 'createdAt', 'updatedAt'
            }
            filtered_kwargs = {k: v for k, v in kwargs.items() if k in allowed_fields}
            
            # Call the original __init__ with only allowed fields
            original_card_init(self, **filtered_kwargs)
            
            # Store extra fields as attributes
            for k, v in kwargs.items():
                if k not in allowed_fields:
                    setattr(self, k, v)
        
        # Apply the monkey patches
        Project_.__init__ = patched_project_init
        User_.__init__ = patched_user_init
        Board_.__init__ = patched_board_init
        List_.__init__ = patched_list_init
        Card_.__init__ = patched_card_init
        
        logger.info("Successfully patched plankapy library")
        return True
        
    except Exception as e:
        logger.error(f"Error patching plankapy library: {e}")
        return False


# Apply the patches when this module is imported
patch_plankapy()