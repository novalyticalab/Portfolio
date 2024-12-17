import logging
from app.core.config import settings
from app.crud.chat_history import update_user_chat, save_user_chat, find_chat_by_chat_id, get_chats_by_user_id
from app.custom_exceptions.exceptions import UserHasNoChatHistoryException, ChatWithChatIDNotAvailavleException
from app.models.user import User
from app.schemas.chat_history_schemas import ChatRequest, ChatResponse, AllChatsResponse, SaveChatResponse
from app.schemas.common_schemas import GeneralResponse
from app.services.auth_service import get_current_user
from fastapi import APIRouter, Depends, Request
from typing import Annotated

logger = logging.getLogger(__name__)

router = APIRouter()

# API endpoint to save chat. 
@router.post(settings.USER_SAVE_CHAT_PATH, response_model=SaveChatResponse)
async def save_chat(chat_request: ChatRequest, request: Request, current_user: Annotated[User, Depends(get_current_user)]):
    logger.info("Saving/Updating chat from user.")

    chat_id = chat_request.chat_id
    if chat_id:
        logger.info("Chat id provided. Attempting to update chat.")
        existing_chat = await find_chat_by_chat_id(chat_id)

        if not existing_chat:
            logger.error("Chat with given chat id not found.")
            raise ChatWithChatIDNotAvailavleException("No chat found with given chat id.")
        else:   
            await update_user_chat(chat_request)
            logger.info("Chat with given chat id updated.")
    else:
        chat_id = await save_user_chat(current_user, chat_request)
        logger.info("New chat saved.")
    
    return SaveChatResponse(
        saved_chat_id=chat_id,
        detail=GeneralResponse(msg="Chat saved to history successfully.")
    )

# API endpoint to retrieve all chats saved by a user.
@router.get(settings.USER_GET_CHAT_HISTORY_PATH, response_model=AllChatsResponse)
async def get_chats(request: Request, current_user: Annotated[User, Depends(get_current_user)]):
    logger.info("Retrieving saved chats for user.")
    chat_histories = await get_chats_by_user_id(str(current_user.id))
    if not chat_histories:
        logger.error("User does not saved chat history.")
        raise UserHasNoChatHistoryException("No chat history found for this user.")
    
    chats = [ChatResponse(chat_id=chat.chat_id, chat=chat.chat) for chat in chat_histories]
    return AllChatsResponse(chats=chats)
