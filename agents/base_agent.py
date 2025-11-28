from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
import logging
import google.generativeai as genai
import os

class BaseAgent(ABC):
    """Base class for all agents using Google ADK"""
    
    def __init__(self, name: str, model: str = "gemini-2.0-flash-exp"):
        self.name = name
        self.model = model
        self.logger = logging.getLogger(name)
        
        # Configure the API key
        api_key = os.getenv('GOOGLE_API_KEY')
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment variables")
        
        genai.configure(api_key=api_key)
        
    @abstractmethod
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process input and return output"""
        pass
    
    async def _generate_response(self, 
                                prompt: str, 
                                system_instruction: str,
                                temperature: float = 1.0) -> str:
        """Generate response using Google Generative AI"""
        try:
            model = genai.GenerativeModel(
                model_name=self.model,
                system_instruction=system_instruction,
                generation_config=genai.GenerationConfig(
                    temperature=temperature,
                )
            )
            
            response = model.generate_content(prompt)
            
            return response.text
            
        except Exception as e:
            self.log_error(f"Error generating response: {str(e)}")
            raise
    
    async def _generate_response_with_tools(self,
                                           prompt: str,
                                           system_instruction: str,
                                           tools: list,
                                           temperature: float = 1.0) -> Dict[str, Any]:
        """Generate response with tool usage"""
        try:
            model = genai.GenerativeModel(
                model_name=self.model,
                system_instruction=system_instruction,
                tools=tools,
                generation_config=genai.GenerationConfig(
                    temperature=temperature,
                )
            )
            
            response = model.generate_content(prompt)
            
            # Handle tool calls if any
            tool_calls = []
            if hasattr(response, 'candidates'):
                for candidate in response.candidates:
                    if hasattr(candidate.content, 'parts'):
                        for part in candidate.content.parts:
                            if hasattr(part, 'function_call'):
                                tool_calls.append({
                                    'name': part.function_call.name,
                                    'args': dict(part.function_call.args)
                                })
            
            return {
                'text': response.text if hasattr(response, 'text') else '',
                'tool_calls': tool_calls
            }
            
        except Exception as e:
            self.log_error(f"Error generating response with tools: {str(e)}")
            raise
    
    def log_info(self, message: str):
        """Log info message"""
        self.logger.info(f"[{self.name}] {message}")
    
    def log_error(self, message: str):
        """Log error message"""
        self.logger.error(f"[{self.name}] {message}")
    
    def log_debug(self, message: str):
        """Log debug message"""
        self.logger.debug(f"[{self.name}] {message}")