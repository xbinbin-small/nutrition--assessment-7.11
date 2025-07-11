from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import uuid
import logging
from datetime import datetime

class BaseAgent(ABC):
    """
    智能体基类，定义统一的接口规范
    
    所有CNA智能体都应继承此基类，确保接口一致性
    """
    
    def __init__(self, agent_name: str, llm_config: Dict[str, Any], system_message: str):
        """
        初始化基础智能体
        
        Args:
            agent_name: 智能体名称
            llm_config: LLM配置
            system_message: 系统消息
        """
        self.agent_name = agent_name
        self.llm_config = llm_config
        self.system_message = system_message
        self.agent_id = str(uuid.uuid4())
        
        # 设置日志
        self.logger = logging.getLogger(f"CNA.{agent_name}")
        
        # 初始化autogen agent
        self._initialize_agent()
        
    def _initialize_agent(self):
        """初始化autogen智能体"""
        import autogen
        self.agent = autogen.AssistantAgent(
            name=self.agent_name,
            llm_config=self.llm_config,
            system_message=self.system_message
        )
    
    @abstractmethod
    def process(self, input_data: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        处理输入数据的抽象方法
        
        Args:
            input_data: 输入数据
            context: 可选的上下文信息（如其他智能体的结果）
            
        Returns:
            处理结果，包含数据和元信息
        """
        pass
    
    def _safe_generate_reply(self, prompt: str) -> str:
        """
        安全的生成回复方法，包含错误处理
        
        Args:
            prompt: 输入提示
            
        Returns:
            生成的回复文本
        """
        try:
            response = self.agent.generate_reply(messages=[{"role": "user", "content": prompt}])
            
            # 处理不同类型的响应
            if isinstance(response, str):
                return response
            elif isinstance(response, dict) and "content" in response:
                return response["content"]
            else:
                return str(response)
                
        except Exception as e:
            self.logger.error(f"生成回复时发生错误: {str(e)}")
            return f"处理过程中发生错误: {str(e)}"
    
    def _create_result(self, data: Any, success: bool = True, error_message: str = None) -> Dict[str, Any]:
        """
        创建标准化的结果格式
        
        Args:
            data: 处理结果数据
            success: 是否成功
            error_message: 错误消息（如果有）
            
        Returns:
            标准化结果
        """
        result = {
            "agent_name": self.agent_name,
            "agent_id": self.agent_id,
            "timestamp": datetime.now().isoformat(),
            "success": success,
            "data": data
        }
        
        if error_message:
            result["error"] = error_message
            
        return result
    
    def validate_input(self, input_data: Dict[str, Any]) -> tuple[bool, str]:
        """
        验证输入数据
        
        Args:
            input_data: 要验证的输入数据
            
        Returns:
            (是否有效, 错误信息)
        """
        if not isinstance(input_data, dict):
            return False, "输入数据必须是字典格式"
        
        if not input_data:
            return False, "输入数据不能为空"
            
        return True, ""
    
    def get_agent_info(self) -> Dict[str, Any]:
        """
        获取智能体信息
        
        Returns:
            智能体信息
        """
        return {
            "agent_name": self.agent_name,
            "agent_id": self.agent_id,
            "llm_config": self.llm_config,
            "system_message": self.system_message
        }