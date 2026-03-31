# enhanced_loan_parser.py
"""
基于银行信贷协议特点优化的解析器
"""

import re
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, date
from decimal import Decimal, InvalidOperation
from .loan_agreement_parser import LoanAgreementParser
from .config import PatternConfig
from .utils import parse_date_from_text

class EnhancedLoanAgreementParser(LoanAgreementParser):
    """针对银行信贷协议优化的解析器"""
    
    def __init__(self, config=None, use_ocr=False):
        super().__init__(config, use_ocr)
        self._setup_enhanced_rules()
    
    def _setup_enhanced_rules(self):
        """设置增强规则"""
        # 1. 借款人提取增强（支持多个borrower）
        self._add_borrower_patterns()
        
        # 2. 金额提取增强
        self._add_amount_patterns()
        
        # 3. 日期提取增强
        self._add_date_patterns()
    
    def _add_borrower_patterns(self):
        """添加借款人匹配模式（支持多个borrower）"""
        enhanced_patterns = [
            # 格式: "ABC Co., Ltd. as borrower"
            PatternConfig(r'([^,\n]+?)(?:,\s*[^,\n]+)*\s+as\s+borrower', 1.0, re.IGNORECASE),
            
            # 格式: "as borrower: ABC Co., Ltd."
            PatternConfig(r'as\s+borrower[：:]\s*([^\n,]+)', 0.95, re.IGNORECASE),
            
            # 格式: "Borrower: ABC Co., Ltd., DEF Inc. as co-borrower"
            PatternConfig(r'Borrower[：:]\s*([^\n]+?)(?=\n\n|\n[A-Z]|$)', 0.9, re.IGNORECASE),
            
            # 格式: "xxx, xxx as borrower, xxx as facility agent"
            PatternConfig(r'([^,\n]+?)(?:,\s*[^,\n]+)*\s*,\s*([^,\n]+?)\s+as\s+borrower', 0.85, re.IGNORECASE),
        ]
        
        # 添加到配置
        self.config.borrower_patterns.extend(enhanced_patterns)
    
    def _add_amount_patterns(self):
        """添加金额匹配模式"""
        enhanced_patterns = [
            # 货币+千位分割数字: HKD 500,000,000
            PatternConfig(r'([A-Z]{3})\s+([0-9]{1,3}(?:,[0-9]{3})+(?:\.[0-9]{2})?)', 1.0),
            
            # 货币符号: HK$ 500,000,000
            PatternConfig(r'([A-Z]{2}\$)\s+([0-9]{1,3}(?:,[0-9]{3})+(?:\.[0-9]{2})?)', 0.9),
            
            # 中文货币: 港币 500,000,000
            PatternConfig(r'(港币|港元|美元|人民币|欧元|英镑)\s+([0-9]{1,3}(?:,[0-9]{3})+(?:\.[0-9]{2})?)', 0.9),
            
            # 信贷协议特定关键词
            PatternConfig(r'(?:Facility Amount|Loan Amount|Principal Amount)[：:]\s*([A-Z]{3})\s+([0-9,]+(?:\.[0-9]{2})?)', 1.0, re.IGNORECASE),
        ]
        
        self.config.amount_patterns.extend(enhanced_patterns)
    
    def _add_date_patterns(self):
        """添加日期匹配模式"""
        enhanced_patterns = [
            # 独立日期行
            PatternConfig(r'^\s*(\d{4}[-/年]\d{1,2}[-/月]\d{1,2}日?)\s*$', 0.9),
            PatternConfig(r'^\s*(\d{1,2}/\d{1,2}/\d{4})\s*$', 0.9),
            PatternConfig(r'^\s*(\d{1,2}\s+[A-Za-z]+\s+\d{4})\s*$', 0.9, re.IGNORECASE),
        ]
        
        self.config.date_patterns.extend(enhanced_patterns)
    
    def parse(self, file_path: str) -> Dict[str, Any]:
        """
        增强解析方法
        """
        # 先进行基础解析
        base_result = super().parse(file_path)
        text = base_result["raw_text"]
        
        if not text or len(text.strip()) < 10:
            return base_result
        
        # 清理文本
        cleaned_text = self._preprocess_text(text)
        
        # 1. 识别协议类型
        agreement_type = self._identify_agreement_type(cleaned_text)
        base_result["agreement_type"] = agreement_type
        
        # 2. 提取参与方（支持多个borrower）
        parties_result = self._extract_parties_enhanced(cleaned_text)
        base_result.update(parties_result)
        
        # 3. 增强金额提取
        amount_result = self._extract_facility_amount_enhanced(cleaned_text)
        base_result.update(amount_result)
        
        # 4. 增强日期提取
        date_result = self._extract_agreement_date_enhanced(cleaned_text)
        base_result.update(date_result)
        
        # 5. 重新计算置信度
        base_result["overall_confidence"] = self._calculate_enhanced_confidence(base_result)
        
        return base_result
    
    def _extract_parties_enhanced(self, text: str) -> Dict[str, Any]:
        """
        增强的参与方提取
        """
        result = {
            "borrowers": [],
            "primary_borrower": None,
            "lenders": [],
            "facility_agents": [],
            "guarantors": [],
            "parties_confidence": 0.0,
        }
        
        # 查找所有"as borrower"出现的位置
        borrower_pattern = re.compile(r'([^,\n]+?)(?:,\s*[^,\n]+)*\s+as\s+borrower', re.IGNORECASE)
        
        borrowers = []
        for match in borrower_pattern.finditer(text):
            # 提取borrower前的公司名称
            borrower_text = match.group(0)
            # 清理"as borrower"后缀
            company_name = re.sub(r'\s+as\s+borrower.*$', '', borrower_text, flags=re.IGNORECASE)
            company_name = self._clean_company_name(company_name.strip())
            
            if company_name and company_name not in borrowers:
                borrowers.append(company_name)
        
        if borrowers:
            result["borrowers"] = borrowers
            result["primary_borrower"] = borrowers[0]
            result["parties_confidence"] = 0.9 if len(borrowers) > 0 else 0.7
        
        # 提取其他参与方
        result.update(self._extract_other_parties_enhanced(text))
        
        return result
    
    def _extract_other_parties_enhanced(self, text: str) -> Dict[str, Any]:
        """
        提取其他参与方
        """
        result = {}
        
        # 提取facility agent
        agent_pattern = re.compile(r'([^,\n]+?)(?:,\s*[^,\n]+)*\s+as\s+facility\s+agent', re.IGNORECASE)
        agents = []
        for match in agent_pattern.finditer(text):
            agent_text = match.group(0)
            company_name = re.sub(r'\s+as\s+facility\s+agent.*$', '', agent_text, flags=re.IGNORECASE)
            company_name = self._clean_company_name(company_name.strip())
            if company_name and company_name not in agents:
                agents.append(company_name)
        
        if agents:
            result["facility_agents"] = agents
        
        # 提取guarantor
        guarantor_pattern = re.compile(r'([^,\n]+?)(?:,\s*[^,\n]+)*\s+as\s+guarantor', re.IGNORECASE)
        guarantors = []
        for match in guarantor_pattern.finditer(text):
            guarantor_text = match.group(0)
            company_name = re.sub(r'\s+as\s+guarantor.*$', '', guarantor_text, flags=re.IGNORECASE)
            company_name = self._clean_company_name(company_name.strip())
            if company_name and company_name not in guarantors:
                guarantors.append(company_name)
        
        if guarantors:
            result["guarantors"] = guarantors
        
        return result
    
    def _clean_company_name(self, name: str) -> str:
        """
        清理公司名称
        """
        if not name:
            return ""
        
        # 移除末尾的逗号和空格
        name = name.rstrip(' ,.;:')
        
        # 移除常见的法律实体后缀
        suffixes = [
            'limited', 'ltd.', 'ltd', 'incorporated', 'inc.',
            'company', 'co.', 'co', 'corporation', 'corp.',
            'group', 'holding', 'holdings', 'plc',
            '有限公司', '有限责任公司', '股份有限公司', '集团公司',
        ]
        
        cleaned = name.strip()
        for suffix in suffixes:
            if cleaned.lower().endswith(suffix.lower()):
                cleaned = cleaned[:-len(suffix)].rstrip()
                break
        
        return cleaned
    
    def _extract_facility_amount_enhanced(self, text: str) -> Dict[str, Any]:
        """
        增强的融资金额提取
        """
        # 优先查找大金额
        large_amount_patterns = [
            # 匹配信贷协议特有的大金额格式
            re.compile(r'([A-Z]{3})\s+([0-9]{1,3}(?:,[0-9]{3}){2,}(?:\.[0-9]{2})?)'),
            re.compile(r'([A-Z]{2}\$)\s+([0-9]{1,3}(?:,[0-9]{3}){2,}(?:\.[0-9]{2})?)'),
        ]
        
        best_amount = None
        best_currency = None
        best_confidence = 0.0
        
        for pattern in large_amount_patterns:
            for match in pattern.finditer(text):
                groups = match.groups()
                if len(groups) >= 2:
                    currency = groups[0]
                    amount_str = groups[1].replace(',', '')
                    
                    try:
                        amount = Decimal(amount_str)
                        # 信贷协议金额通常较大，百万级别以上
                        if amount > 1000000:  # 100万以上
                            confidence = 0.95
                            
                            # 金额越大，置信度越高
                            if amount > 10000000:  # 1000万以上
                                confidence = 0.98
                            elif amount > 100000000:  # 1亿以上
                                confidence = 0.99
                            
                            if confidence > best_confidence:
                                best_confidence = confidence
                                best_amount = amount
                                best_currency = self._normalize_currency(currency)
                    except:
                        continue
        
        if best_amount and best_confidence > 0:
            return {
                "facility_amount": float(best_amount),
                "amount_confidence": best_confidence,
                "currency": best_currency,
                "currency_confidence": best_confidence * 0.95,
            }
        
        # 如果没找到大金额，回退到父类方法
        return super()._extract_facility_amount(text)
    
    def _extract_agreement_date_enhanced(self, text: str) -> Dict[str, Any]:
        """
        增强的协议日期提取
        """
        # 策略1: 查找首页/第二页的独立日期行
        first_two_pages = text[:6000]
        lines = first_two_pages.split('\n')
        
        for i, line in enumerate(lines):
            line = line.strip()
            if 5 < len(line) < 30:  # 日期行通常在5-30字符之间
                parsed_date = parse_date_from_text(line)
                if parsed_date and self._validate_date(parsed_date):
                    # 检查是否是独立行
                    is_standalone = True
                    if i > 0 and lines[i-1].strip():
                        prev_line_lower = lines[i-1].strip().lower()
                        date_keywords = ['date', 'dated', '日期', '签订', 'executed']
                        if not any(keyword in prev_line_lower for keyword in date_keywords):
                            is_standalone = False
                    
                    if is_standalone:
                        return {
                            "agreement_date": parsed_date,
                            "date_confidence": 0.9,
                            "date_source": "standalone_line",
                        }
        
        # 策略2: 回退到父类方法
        return super()._extract_agreement_date(text)
    
    def _normalize_currency(self, currency: str) -> str:
        """
        标准化货币代码
        """
        currency = currency.upper()
        
        currency_map = {
            'HK$': 'HKD',
            'USD': 'USD',
            'CNY': 'CNY',
            'RMB': 'CNY',
            '人民币': 'CNY',
            '港元': 'HKD',
            '港币': 'HKD',
            '美元': 'USD',
            '欧元': 'EUR',
            '英镑': 'GBP',
        }
        
        return currency_map.get(currency, currency)
    
    def _calculate_enhanced_confidence(self, result: Dict[str, Any]) -> float:
        """
        计算增强的置信度
        """
        weights = {
            "borrower_confidence": 0.4,  # 借款人最重要
            "date_confidence": 0.3,
            "amount_confidence": 0.3,
        }
        
        confidences = []
        for field, weight in weights.items():
            confidence = result.get(field, 0.0)
            confidences.append(confidence * weight)
        
        overall = sum(confidences) / sum(weights.values()) if confidences else 0.0
        
        # 如果有多个borrower，增加置信度
        if result.get("borrowers") and len(result["borrowers"]) > 0:
            overall = min(1.0, overall * 1.1)
        
        return round(overall, 3)
