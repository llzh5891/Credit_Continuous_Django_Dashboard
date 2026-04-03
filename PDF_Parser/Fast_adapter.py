"""
适配器：将FastLoanAgreementParser适配到Django模型
"""

from django.db import transaction
from django.utils import timezone
from datetime import datetime
from decimal import Decimal
import logging
from typing import Dict, Any

# 从你的fast_loan_parser导入
try:
    from .fast_loan_parser import FastLoanAgreementParser
    HAS_FAST_PARSER = True
except ImportError as e:
    HAS_FAST_PARSER = False
    logging.warning(f"无法导入FastLoanAgreementParser: {e}")

logger = logging.getLogger(__name__)


class FastParserAdapter:
    """
    FastLoanAgreementParser适配器
    将快速解析器的结果适配到Django AgreementPDF模型
    """
    
    def __init__(self, config=None):
        """
        初始化适配器
        
        Args:
            config: 配置字典，可选
        """
        if not HAS_FAST_PARSER:
            raise ImportError("FastLoanAgreementParser未找到，请确保fast_loan_parser.py在parsers目录中")
        
        self.parser = FastLoanAgreementParser(config)
        logger.info("✅ FastParserAdapter初始化成功")
    
    def parse_pdf(self, pdf_path: str) -> Dict[str, Any]:
        """
        解析PDF并返回适配后的结果
        
        Args:
            pdf_path: PDF文件路径
            
        Returns:
            适配到Django模型的字典
        """
        try:
            # 调用快速解析器
            raw_result = self.parser.parse(pdf_path)
            
            # 适配到数据库字段
            adapted_result = self._adapt_to_model(raw_result)
            
            return adapted_result
            
        except Exception as e:
            logger.error(f"PDF解析失败: {str(e)}", exc_info=True)
            return self._create_error_result(str(e))
    
    def _adapt_to_model(self, raw_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        将原始解析结果适配到Django模型字段
        
        Args:
            raw_result: 快速解析器的原始结果
            
        Returns:
            适配后的字典，可直接用于Django模型
        """
        adapted = {
            # 核心字段
            'success': raw_result.get('success', False),
            'processing_mode': 'fast_parser',
            
            # 解析详情
            'raw_result': raw_result,  # 保存原始结果用于调试
            
            # 性能信息
            'performance_metrics': raw_result.get('performance', {}),
        }
        
        # 处理借款人信息
        borrower_name = raw_result.get('borrower_name')
        if borrower_name:
            adapted['borrower_name'] = borrower_name
            adapted['borrower_confidence'] = raw_result.get('borrower_confidence', 0.0)
            adapted['all_borrowers'] = raw_result.get('borrowers', [])
        else:
            adapted['borrower_name'] = None
            adapted['borrower_confidence'] = 0.0
        
        # 处理金额
        facility_amount = raw_result.get('facility_amount')
        currency = raw_result.get('currency', 'HKD')
        
        if facility_amount:
            try:
                # 转换为Decimal
                adapted['facility_amount'] = Decimal(str(facility_amount))
                adapted['currency'] = currency.upper() if currency else 'HKD'
                adapted['amount_confidence'] = raw_result.get('amount_confidence', 0.0)
            except (ValueError, InvalidOperation) as e:
                logger.warning(f"金额转换失败: {facility_amount}, 错误: {e}")
                adapted['facility_amount'] = None
                adapted['currency'] = 'HKD'
        else:
            adapted['facility_amount'] = None
            adapted['currency'] = 'HKD'
        
        # 处理日期
        agreement_date_str = raw_result.get('agreement_date')
        if agreement_date_str:
            date_obj = self._parse_date(agreement_date_str)
            if date_obj:
                adapted['agreement_date'] = date_obj
                adapted['date_confidence'] = raw_result.get('date_confidence', 0.0)
            else:
                adapted['agreement_date'] = None
        else:
            adapted['agreement_date'] = None
        
        # 处理文本
        if 'text' in raw_result:
            adapted['parsed_text'] = raw_result['text']
        elif 'parsed_text' in raw_result:
            adapted['parsed_text'] = raw_result['parsed_text']
        else:
            # 从原始结果构建文本
            adapted['parsed_text'] = self._build_text_summary(raw_result)
        
        # 错误和警告
        if 'error' in raw_result:
            adapted['error_message'] = raw_result['error']
        if 'warnings' in raw_result:
            adapted['warnings'] = raw_result['warnings']
        
        return adapted
    
    def _parse_date(self, date_str: str):
        """
        解析日期字符串为date对象
        
        Args:
            date_str: 日期字符串
            
        Returns:
            date对象或None
        """
        if not date_str:
            return None
        
        date_str = str(date_str).strip()
        
        # 常见日期格式
        date_formats = [
            '%Y-%m-%d',      # 2024-01-15
            '%Y/%m/%d',      # 2024/01/15
            '%Y年%m月%d日',  # 2024年01月15日
            '%d/%m/%Y',      # 15/01/2024
            '%d-%m-%Y',      # 15-01-2024
            '%Y.%m.%d',      # 2024.01.15
        ]
        
        for fmt in date_formats:
            try:
                # 替换中文分隔符
                normalized = date_str.replace('年', '-').replace('月', '-').replace('日', '')
                date_obj = datetime.strptime(normalized, '%Y-%m-%d').date()
                return date_obj
            except ValueError:
                try:
                    date_obj = datetime.strptime(date_str, fmt).date()
                    return date_obj
                except ValueError:
                    continue
        
        # 尝试正则表达式提取
        import re
        date_patterns = [
            r'(\d{4})[-/年](\d{1,2})[-/月](\d{1,2})',
            r'(\d{1,2})[-/](\d{1,2})[-/](\d{4})',
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, date_str)
            if match:
                try:
                    groups = match.groups()
                    if len(groups) == 3:
                        if len(groups[0]) == 4:  # YYYY-MM-DD
                            year, month, day = int(groups[0]), int(groups[1]), int(groups[2])
                        else:  # DD-MM-YYYY
                            day, month, year = int(groups[0]), int(groups[1]), int(groups[2])
                        
                        from datetime import date
                        return date(year, month, day)
                except (ValueError, IndexError):
                    continue
        
        logger.warning(f"无法解析日期: {date_str}")
        return None
    
    def _build_text_summary(self, result: Dict[str, Any]) -> str:
        """从结果构建文本摘要"""
        summary_parts = []
        
        if result.get('borrower_name'):
            summary_parts.append(f"借款人: {result['borrower_name']}")
        
        if result.get('facility_amount') and result.get('currency'):
            summary_parts.append(f"金额: {result['facility_amount']} {result['currency']}")
        
        if result.get('agreement_date'):
            summary_parts.append(f"日期: {result['agreement_date']}")
        
        if summary_parts:
            return " | ".join(summary_parts)
        
        return "PDF解析完成，但未提取到关键信息"
    
    def _create_error_result(self, error_msg: str) -> Dict[str, Any]:
        """创建错误结果"""
        return {
            'success': False,
            'error_message': error_msg,
            'borrower_name': None,
            'facility_amount': None,
            'currency': 'HKD',
            'agreement_date': None,
            'parsed_text': f"解析失败: {error_msg}",
            'processing_mode': 'fast_parser',
        }
