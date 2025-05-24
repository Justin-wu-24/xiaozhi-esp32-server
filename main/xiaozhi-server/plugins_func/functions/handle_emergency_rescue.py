import aiohttp

from config.logger import setup_logging
from plugins_func.register import register_function, ToolType, ActionResponse, Action

TAG = __name__
logger = setup_logging()

handle_emergency_rescue_function_desc = {
    "type": "function",
    "function": {
        "name": "handle_emergency_rescue",
        "description": "This function is called when the user expresses the need to start rescuing the patient or enter the rescue mode",
        "parameters": {
            "type": "object",
            "properties": {
                "response_message": {
                    "type": "string",
                    "description": "A reply message confirming to the user that the rescue mode has been activated",
                }
            },
            "required": ["response_message"],
        },
    },
}

@register_function(
    "handle_emergency_rescue", handle_emergency_rescue_function_desc, ToolType.SYSTEM_CTL
)
async def handle_emergency_rescue(conn, response_message: str | None = None):
    try:
        # 构建完整的URL
        client_ip = conn.client_ip
        url = f"http://{client_ip}:8087/tierLock/open"
        
        # 发送HTTP请求到抢救模式接口
        async with aiohttp.ClientSession() as session:
            async with session.post(url) as response:
                if response.status == 200:
                    if response_message is None:
                        response_message = "The rescue mode has been activated and relevant personnel are being notified"
                    logger.bind(tag=TAG).info(f"抢救模式已启动，调用地址: {url}")
                    return ActionResponse(
                        action=Action.RESPONSE,
                        result="The rescue mode was successfully activated",
                        response=response_message
                    )
                else:
                    error_msg = f"启动抢救模式失败，HTTP状态码: {response.status}, URL: {url}"
                    logger.bind(tag=TAG).error(error_msg)
                    return ActionResponse(
                        action=Action.ERROR,
                        result=error_msg,
                        response="Sorry, the rescue mode failed to be activated. Please try again later"
                    )
    except Exception as e:
        error_msg = f"启动抢救模式时发生错误: {str(e)}, URL: {url}"
        logger.bind(tag=TAG).error(error_msg)
        return ActionResponse(
            action=Action.ERROR,
            result=error_msg,
            response="Sorry, an error occurred when initiating the rescue mode. Please try again later"
        ) 