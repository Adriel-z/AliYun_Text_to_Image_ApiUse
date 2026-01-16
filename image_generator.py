"""
阿里云百炼平台图像生成程序 - 匹配官方API格式
使用多模态生成API，支持qwen-image-max模型
"""

import os
import json
import time
import requests
from datetime import datetime
from pathlib import Path
import logging
import hashlib

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

class ConfigManager:
    """配置文件管理器"""
    
    def __init__(self, config_path='config.json'):
        self.config_path = config_path
        self.config = self._load_config()
    
    def _load_config(self):
        """加载配置文件"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # 验证必要配置项
            if 'DASHSCOPE_API_KEY' not in config:
                raise ValueError("配置文件中缺少必要字段: DASHSCOPE_API_KEY")
            
            logger.info("配置文件加载成功")
            return config
            
        except FileNotFoundError:
            logger.error(f"配置文件 {self.config_path} 不存在")
            raise
        except json.JSONDecodeError:
            logger.error(f"配置文件 {self.config_path} JSON格式错误")
            raise
    
    def get_api_key(self):
        """获取API密钥"""
        return self.config['DASHSCOPE_API_KEY']
    
    def get_model(self):
        """获取模型名称"""
        return self.config.get('MODEL', 'qwen-image-max')


class PromptParser:
    """Prompt解析器 - 支持官方API格式"""
    
    def __init__(self, prompt_path='prompt.txt'):
        self.prompt_path = prompt_path
        self.prompt_data = self._parse_prompt_file()
    
    def _parse_prompt_file(self):
        """解析prompt.txt文件"""
        try:
            with open(self.prompt_path, 'r', encoding='utf-8') as f:
                content = f.read().strip()
            
            data = {
                'prompt': '',
                'size': '1024*1024',
                'negative_prompt': '',
                'prompt_extend': True,
                'watermark': False
            }
            
            lines = content.split('\n')
            current_section = None
            
            for line in lines:
                line = line.strip()
                
                # 跳过空行和注释
                if not line or line.startswith('#'):
                    continue
                
                # 检测段落标题
                if line.endswith(':'):
                    current_section = line[:-1].lower()
                    continue
                
                # 如果是键值对格式
                if '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip().lower()
                    value = value.strip()
                    
                    if key in ['size', 'n']:
                        data[key] = value
                    elif key == 'prompt_extend':
                        data[key] = value.lower() in ['true', 'yes', '1', 'on']
                    elif key == 'watermark':
                        data[key] = value.lower() in ['true', 'yes', '1', 'on']
                    elif key == 'negative_prompt':
                        data[key] = value
                else:
                    # 文本内容，添加到当前段落或prompt
                    if current_section == 'prompt':
                        data['prompt'] += line + ' '
                    elif current_section == 'negative_prompt':
                        data['negative_prompt'] += line + ' '
                    elif not data['prompt']:
                        # 如果没有明确段落，第一段文本作为prompt
                        data['prompt'] = line
            
            # 清理空格
            data['prompt'] = data['prompt'].strip()
            data['negative_prompt'] = data['negative_prompt'].strip()
            
            if not data['prompt']:
                raise ValueError("prompt.txt中未找到有效的prompt内容")
            
            logger.info(f"Prompt解析成功")
            logger.info(f"  Prompt长度: {len(data['prompt'])} 字符")
            if data['negative_prompt']:
                logger.info(f"  负面提示长度: {len(data['negative_prompt'])} 字符")
            
            return data
            
        except FileNotFoundError:
            logger.error(f"prompt文件 {self.prompt_path} 不存在")
            raise
    
    def get_prompt(self):
        """获取prompt文本"""
        return self.prompt_data['prompt']
    
    def get_negative_prompt(self):
        """获取负面提示词"""
        return self.prompt_data['negative_prompt']
    
    def get_size(self):
        """获取图片尺寸"""
        return self.prompt_data.get('size', '1024*1024')
    
    def get_prompt_extend(self):
        """获取是否扩展prompt"""
        return self.prompt_data.get('prompt_extend', True)
    
    def get_watermark(self):
        """获取是否添加水印"""
        return self.prompt_data.get('watermark', False)


class BailianImageGenerator:
    """阿里云百炼图像生成器 - 完全匹配官方API"""
    
    def __init__(self, config_manager):
        self.config = config_manager
        self.api_url = "https://dashscope.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation"
        self.headers = {
            'Authorization': f'Bearer {self.config.get_api_key()}',
            'Content-Type': 'application/json'
        }
    
    def generate_image(self, prompt, size='1024*1024', negative_prompt='', 
                      prompt_extend=True, watermark=False):
        """生成图像 - 完全匹配官方API格式"""
        
        # 构建与官方示例完全一致的请求体
        request_body = {
            "model": self.config.get_model(),
            "input": {
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "text": prompt
                            }
                        ]
                    }
                ]
            },
            "parameters": {
                "size": size,
                "prompt_extend": prompt_extend,
                "watermark": watermark
            }
        }
        
        # 添加可选参数
        if negative_prompt:
            request_body["parameters"]["negative_prompt"] = negative_prompt
        
        # 调试信息
        logger.debug(f"请求体结构: {json.dumps(request_body, ensure_ascii=False, indent=2)}")
        
        try:
            logger.info("正在调用阿里云百炼API生成图像...")
            logger.info(f"使用模型: {self.config.get_model()}")
            logger.info(f"图片尺寸: {size}")
            
            start_time = time.time()
            response = requests.post(
                self.api_url,
                headers=self.headers,
                json=request_body,
                timeout=60  # 图像生成可能需要更长时间
            )
            
            elapsed_time = time.time() - start_time
            logger.info(f"API请求耗时: {elapsed_time:.2f}秒")
            
            # 检查响应状态
            if response.status_code != 200:
                logger.error(f"API请求失败，状态码: {response.status_code}")
                logger.error(f"错误详情: {response.text}")
                
                # 尝试解析错误信息
                try:
                    error_data = response.json()
                    if 'message' in error_data:
                        logger.error(f"错误信息: {error_data['message']}")
                except:
                    pass
                
                response.raise_for_status()
            
            # 解析响应
            result = response.json()
            logger.debug(f"API响应: {json.dumps(result, ensure_ascii=False)}")
            
            # 提取图片信息
            images = self._extract_images_from_response(result)
            
            if not images:
                logger.error("API响应中未找到图片数据")
                logger.error(f"响应内容: {result}")
                raise ValueError("API响应中未找到有效的图片数据")
            
            logger.info(f"成功获取 {len(images)} 张图片")
            return images
            
        except requests.exceptions.Timeout:
            logger.error("API请求超时，请稍后重试")
            raise
        except requests.exceptions.RequestException as e:
            logger.error(f"网络请求失败: {e}")
            raise
    
    def _extract_images_from_response(self, result):
        """从API响应中提取图片信息"""
        images = []
        
        try:
            # 根据官方响应格式提取图片
            if 'output' in result and 'choices' in result['output']:
                for choice in result['output']['choices']:
                    if 'message' in choice and 'content' in choice['message']:
                        for content_item in choice['message']['content']:
                            if 'image' in content_item:
                                images.append({
                                    'url': content_item['image']
                                })
            elif 'output' in result and 'results' in result['output']:
                # 备用格式
                for result_item in result['output']['results']:
                    if 'url' in result_item:
                        images.append({
                            'url': result_item['url']
                        })
            
            # 记录请求ID供调试使用
            if 'request_id' in result:
                logger.info(f"请求ID: {result['request_id']}")
            
            # 记录使用情况
            if 'usage' in result:
                usage = result['usage']
                logger.info(f"使用统计: 宽度={usage.get('width', 'N/A')}, "
                          f"高度={usage.get('height', 'N/A')}, "
                          f"图片数量={usage.get('image_count', len(images))}")
            
        except Exception as e:
            logger.error(f"解析API响应失败: {e}")
        
        return images
    
    def download_image(self, image_info, save_path):
        """下载图片到本地"""
        try:
            if 'url' not in image_info:
                logger.error(f"图片信息中缺少URL: {image_info}")
                return False
            
            image_url = image_info['url']
            logger.info(f"正在下载图片: {image_url[:80]}...")
            
            # 设置下载超时
            response = requests.get(image_url, stream=True, timeout=30)
            response.raise_for_status()
            
            # 获取文件大小
            file_size = int(response.headers.get('content-length', 0))
            
            # 保存文件
            with open(save_path, 'wb') as f:
                downloaded = 0
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        
                        # 显示下载进度
                        if file_size > 0:
                            percent = (downloaded / file_size) * 100
                            logger.debug(f"下载进度: {percent:.1f}%")
            
            # 验证文件大小
            actual_size = os.path.getsize(save_path)
            if file_size > 0 and actual_size != file_size:
                logger.warning(f"文件大小不匹配: 预期={file_size}, 实际={actual_size}")
            
            logger.info(f"图片已保存: {save_path} ({actual_size:,} 字节)")
            return True
            
        except requests.exceptions.RequestException as e:
            logger.error(f"下载图片失败: {e}")
            return False
        except Exception as e:
            logger.error(f"保存图片失败: {e}")
            return False


class FileManager:
    """文件管理器"""
    
    def __init__(self, output_dir='./output'):
        self.output_dir = Path(output_dir)
        self._ensure_output_dir()
    
    def _ensure_output_dir(self):
        """确保输出目录存在"""
        self.output_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"输出目录: {self.output_dir.absolute()}")
    
    def generate_filename(self, index=0, base_name=None):
        """生成带时间戳的文件名"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # 使用prompt的部分内容作为文件名（如果有）
        if base_name and len(base_name) > 0:
            # 取前20个字符，移除非字母数字字符
            safe_name = ''.join(c for c in base_name[:20] if c.isalnum() or c in [' ', '-', '_'])
            safe_name = safe_name.replace(' ', '_')
            if safe_name:
                filename = f"{timestamp}_{safe_name}_{index}.png"
            else:
                filename = f"image_{timestamp}_{index}.png"
        else:
            filename = f"image_{timestamp}_{index}.png"
        
        return self.output_dir / filename


def validate_config():
    """验证配置文件"""
    try:
        with open('config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        required_fields = ['DASHSCOPE_API_KEY']
        missing_fields = []
        
        for field in required_fields:
            if field not in config:
                missing_fields.append(field)
        
        if missing_fields:
            logger.error(f"配置文件缺少必要字段: {', '.join(missing_fields)}")
            return False
        
        # 检查API密钥格式
        api_key = config['DASHSCOPE_API_KEY']
        if not api_key.startswith('sk-'):
            logger.warning("API密钥通常以'sk-'开头，请确认密钥正确性")
        
        return True
        
    except Exception as e:
        logger.error(f"验证配置文件失败: {e}")
        return False


def main():
    """主函数"""
    try:
        logger.info("=" * 60)
        logger.info("阿里云百炼图像生成程序 v2.0")
        logger.info("基于多模态生成API (qwen-image-max模型)")
        logger.info("=" * 60)
        
        # 验证配置文件
        if not validate_config():
            return []
        
        # 1. 初始化管理器
        config_manager = ConfigManager('config.json')
        prompt_parser = PromptParser('prompt.txt')
        file_manager = FileManager('./output')
        
        # 2. 获取生成参数
        prompt = prompt_parser.get_prompt()
        negative_prompt = prompt_parser.get_negative_prompt()
        size = prompt_parser.get_size()
        prompt_extend = prompt_parser.get_prompt_extend()
        watermark = prompt_parser.get_watermark()
        
        logger.info("生成参数:")
        logger.info(f"  Prompt: {prompt[:80]}..." if len(prompt) > 80 else f"  Prompt: {prompt}")
        logger.info(f"  尺寸: {size}")
        logger.info(f"  Prompt扩展: {'是' if prompt_extend else '否'}")
        logger.info(f"  水印: {'是' if watermark else '否'}")
        if negative_prompt:
            logger.info(f"  负面提示: {negative_prompt[:80]}..." if len(negative_prompt) > 80 else f"  负面提示: {negative_prompt}")
        
        # 3. 创建图像生成器
        generator = BailianImageGenerator(config_manager)
        
        # 4. 生成图像
        logger.info("开始生成图像...")
        images = generator.generate_image(
            prompt=prompt,
            size=size,
            negative_prompt=negative_prompt,
            prompt_extend=prompt_extend,
            watermark=watermark
        )
        
        # 5. 下载并保存图片
        logger.info(f"开始保存 {len(images)} 张图片...")
        saved_files = []
        
        for i, image_info in enumerate(images):
            # 使用prompt的一部分作为文件名
            save_path = file_manager.generate_filename(i, prompt[:20])
            
            if generator.download_image(image_info, save_path):
                saved_files.append(save_path)
        
        # 6. 输出结果摘要
        logger.info("=" * 60)
        logger.info("🎉 图像生成任务完成！")
        logger.info(f"✅ 成功保存 {len(saved_files)} 张图片:")
        for file_path in saved_files:
            logger.info(f"   📄 {file_path.name}")
        
        total_size = sum(os.path.getsize(f) for f in saved_files)
        logger.info(f"💾 总大小: {total_size:,} 字节 ({total_size/1024/1024:.2f} MB)")
        logger.info("=" * 60)
        
        return saved_files
        
    except KeyboardInterrupt:
        logger.info("\n程序被用户中断")
        return []
    except Exception as e:
        logger.error(f"程序执行失败: {e}")
        logger.error("💡 故障排除建议:")
        logger.error("  1. 检查config.json中的API密钥是否正确")
        logger.error("  2. 确认API密钥有足够的余额和权限")
        logger.error("  3. 检查网络连接是否正常")
        logger.error("  4. 查看prompt.txt格式是否正确")
        logger.error("  5. 尝试简化prompt内容")
        return []


if __name__ == "__main__":
    # 可以设置日志级别为DEBUG以查看更多详细信息
    # logging.getLogger().setLevel(logging.DEBUG)
    
    main()