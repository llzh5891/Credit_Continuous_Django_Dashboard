"""
客户匹配逻辑 - 将解析的协议与现有客户数据库匹配
"""

import re
import logging
from typing import Dict, List, Tuple, Optional, Any
from difflib import SequenceMatcher
from decimal import Decimal
from datetime import datetime, date
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class MatchStrategy(Enum):
    """匹配策略枚举"""
    EXACT = "exact"  # 精确匹配
    FUZZY = "fuzzy"  # 模糊匹配
    COMBINED = "combined"  # 组合匹配

class MatchResult(Enum):
    """匹配结果枚举"""
    EXACT_MATCH = "exact_match"
    HIGH_CONFIDENCE = "high_confidence"
    MEDIUM_CONFIDENCE = "medium_confidence"
    LOW_CONFIDENCE = "low_confidence"
    NO_MATCH = "no_match"
    MANUAL_REVIEW = "manual_review"

@dataclass
class Customer:
    """客户数据类"""
    id: int
    name: str
    name_aliases: List[str] = None
    registration_number: Optional[str] = None
    tax_id: Optional[str] = None
    industry: Optional[str] = None
    country: Optional[str] = None
    
    def __post_init__(self):
        if self.name_aliases is None:
            self.name_aliases = []

@dataclass
class AgreementData:
    """协议数据类"""
    borrower_name: Optional[str]
    agreement_date: Optional[date]
    facility_amount: Optional[Decimal]
    currency: Optional[str]
    parsed_text: Optional[str]
    confidence_scores: Optional[Dict[str, float]] = None
    
    def __post_init__(self):
        if self.confidence_scores is None:
            self.confidence_scores = {}

@dataclass
class MatchCandidate:
    """匹配候选类"""
    customer: Customer
    confidence: float
    match_type: str
    matched_fields: List[str]
    reasoning: str
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "customer_id": self.customer.id,
            "customer_name": self.customer.name,
            "confidence": self.confidence,
            "match_type": self.match_type,
            "matched_fields": self.matched_fields,
            "reasoning": self.reasoning
        }

class CustomerMatcher:
    """客户匹配器"""
    
    def __init__(self, config: Optional[Dict] = None):
        """
        初始化客户匹配器
        
        Args:
            config: 匹配配置
        """
        self.config = config or self._get_default_config()
        self.logger = logging.getLogger(self.__class__.__name__)
        
    def _get_default_config(self) -> Dict:
        """获取默认配置"""
        return {
            # 匹配阈值
            "confidence_thresholds": {
                "exact_match": 0.95,
                "auto_match": 0.85,
                "manual_review": 0.70,
                "no_match": 0.0
            },
            
            # 字段权重
            "field_weights": {
                "name": 0.7,
                "registration_number": 0.2,
                "other_fields": 0.1
            },
            
            # 名称匹配配置
            "name_matching": {
                "min_similarity": 0.8,
                "remove_common_suffixes": True,
                "normalize_chinese": True,
                "ignore_case": True
            },
            
            # 模糊匹配配置
            "fuzzy_matching": {
                "enable": True,
                "max_edit_distance": 3,
                "use_soundex": False,
                "use_metaphone": False
            },
            
            # 日志配置
            "log_level": "INFO",
            "log_matching_details": True
        }
    
    def find_matches(
        self, 
        agreement_data: AgreementData, 
        customers: List[Customer],
        strategy: MatchStrategy = MatchStrategy.COMBINED
    ) -> List[MatchCandidate]:
        """
        查找匹配的客户
        
        Args:
            agreement_data: 协议数据
            customers: 客户列表
            strategy: 匹配策略
            
        Returns:
            匹配候选列表，按置信度降序排序
        """
        self.logger.info(f"开始客户匹配，策略: {strategy.value}")
        self.logger.info(f"协议借款人: {agreement_data.borrower_name}")
        self.logger.info(f"客户库数量: {len(customers)}")
        
        if not agreement_data.borrower_name:
            self.logger.warning("协议中没有借款人名称，无法进行匹配")
            return []
        
        candidates = []
        
        for customer in customers:
            try:
                candidate = self._match_customer(agreement_data, customer, strategy)
                if candidate:
                    candidates.append(candidate)
                    
            except Exception as e:
                self.logger.error(f"匹配客户 {customer.id} 时出错: {e}")
                continue
        
        # 按置信度排序
        candidates.sort(key=lambda x: x.confidence, reverse=True)
        
        self.logger.info(f"匹配完成，找到 {len(candidates)} 个候选")
        return candidates
    
    def _match_customer(
        self, 
        agreement_data: AgreementData, 
        customer: Customer,
        strategy: MatchStrategy
    ) -> Optional[MatchCandidate]:
        """
        匹配单个客户
        
        Args:
            agreement_data: 协议数据
            customer: 客户
            strategy: 匹配策略
            
        Returns:
            匹配候选或None
        """
        if strategy == MatchStrategy.EXACT:
            return self._exact_match(agreement_data, customer)
        elif strategy == MatchStrategy.FUZZY:
            return self._fuzzy_match(agreement_data, customer)
        elif strategy == MatchStrategy.COMBINED:
            return self._combined_match(agreement_data, customer)
        else:
            raise ValueError(f"不支持的匹配策略: {strategy}")
    
    def _exact_match(
        self, 
        agreement_data: AgreementData, 
        customer: Customer
    ) -> Optional[MatchCandidate]:
        """
        精确匹配
        
        Args:
            agreement_data: 协议数据
            customer: 客户
            
        Returns:
            匹配候选或None
        """
        agreement_name = self._normalize_name(agreement_data.borrower_name)
        customer_names = [self._normalize_name(customer.name)] + \
                        [self._normalize_name(alias) for alias in customer.name_aliases]
        
        matched_fields = []
        reasoning = []
        
        # 检查精确匹配
        if agreement_name in customer_names:
            confidence = 1.0
            match_type = "exact_name_match"
            matched_fields.append("name")
            reasoning.append("名称精确匹配")
            
            return MatchCandidate(
                customer=customer,
                confidence=confidence,
                match_type=match_type,
                matched_fields=matched_fields,
                reasoning="; ".join(reasoning)
            )
        
        return None
    
    def _fuzzy_match(
        self, 
        agreement_data: AgreementData, 
        customer: Customer
    ) -> Optional[MatchCandidate]:
        """
        模糊匹配
        
        Args:
            agreement_data: 协议数据
            customer: 客户
            
        Returns:
            匹配候选或None
        """
        agreement_name = self._normalize_name(agreement_data.borrower_name)
        customer_names = [self._normalize_name(customer.name)] + \
                        [self._normalize_name(alias) for alias in customer.name_aliases]
        
        best_similarity = 0.0
        best_customer_name = ""
        matched_fields = []
        reasoning = []
        
        # 计算名称相似度
        for cust_name in customer_names:
            similarity = self._calculate_name_similarity(agreement_name, cust_name)
            
            if similarity > best_similarity:
                best_similarity = similarity
                best_customer_name = cust_name
        
        # 如果相似度足够高
        if best_similarity >= self.config["name_matching"]["min_similarity"]:
            confidence = best_similarity
            match_type = f"fuzzy_name_match_{best_similarity:.2f}"
            matched_fields.append("name")
            reasoning.append(f"名称模糊匹配 (相似度: {best_similarity:.2f})")
            
            # 计算其他字段匹配
            other_fields_confidence = self._match_other_fields(agreement_data, customer)
            if other_fields_confidence > 0:
                confidence = confidence * 0.7 + other_fields_confidence * 0.3
                reasoning.append("其他字段匹配加分")
            
            return MatchCandidate(
                customer=customer,
                confidence=confidence,
                match_type=match_type,
                matched_fields=matched_fields,
                reasoning="; ".join(reasoning)
            )
        
        return None
    
    def _combined_match(
        self, 
        agreement_data: AgreementData, 
        customer: Customer
    ) -> Optional[MatchCandidate]:
        """
        组合匹配（精确 + 模糊）
        
        Args:
            agreement_data: 协议数据
            customer: 客户
            
        Returns:
            匹配候选或None
        """
        # 先尝试精确匹配
        exact_match = self._exact_match(agreement_data, customer)
        if exact_match:
            return exact_match
        
        # 再尝试模糊匹配
        fuzzy_match = self._fuzzy_match(agreement_data, customer)
        if fuzzy_match:
            return fuzzy_match
        
        # 尝试其他匹配方法
        return self._alternative_matching(agreement_data, customer)
    
    def _alternative_matching(
        self, 
        agreement_data: AgreementData, 
        customer: Customer
    ) -> Optional[MatchCandidate]:
        """
        替代匹配方法
        
        Args:
            agreement_data: 协议数据
            customer: 客户
            
        Returns:
            匹配候选或None
        """
        agreement_name = agreement_data.borrower_name
        customer_name = customer.name
        
        matched_fields = []
        reasoning = []
        confidence = 0.0
        
        # 1. 检查是否包含关系
        if (agreement_name in customer_name or customer_name in agreement_name) and \
           len(agreement_name) > 3 and len(customer_name) > 3:
            confidence = 0.75
            match_type = "name_containment"
            matched_fields.append("name")
            reasoning.append("名称包含关系匹配")
        
        # 2. 检查公司类型后缀是否相同
        elif self._has_same_company_suffix(agreement_name, customer_name):
            # 移除后缀后比较
            name1_no_suffix = self._remove_company_suffix(agreement_name)
            name2_no_suffix = self._remove_company_suffix(customer_name)
            
            if name1_no_suffix and name2_no_suffix:
                similarity = self._calculate_name_similarity(name1_no_suffix, name2_no_suffix)
                if similarity > 0.7:
                    confidence = 0.7
                    match_type = "same_suffix_similar_name"
                    matched_fields.append("name")
                    reasoning.append(f"相同公司类型后缀，名称相似度: {similarity:.2f}")
        
        # 3. 检查是否有共同的关键词
        common_keywords = self._find_common_keywords(agreement_name, customer_name)
        if len(common_keywords) >= 2:
            confidence = 0.65
            match_type = "common_keywords"
            matched_fields.append("name")
            reasoning.append(f"共同关键词: {', '.join(common_keywords)}")
        
        if confidence > 0:
            # 添加其他字段匹配
            other_fields_confidence = self._match_other_fields(agreement_data, customer)
            if other_fields_confidence > 0:
                confidence = confidence * 0.8 + other_fields_confidence * 0.2
                reasoning.append("其他字段匹配加分")
            
            return MatchCandidate(
                customer=customer,
                confidence=confidence,
                match_type=match_type,
                matched_fields=matched_fields,
                reasoning="; ".join(reasoning)
            )
        
        return None
    
    def _match_other_fields(
        self, 
        agreement_data: AgreementData, 
        customer: Customer
    ) -> float:
        """
        匹配其他字段
        
        Args:
            agreement_data: 协议数据
            customer: 客户
            
        Returns:
            其他字段匹配置信度
        """
        confidence = 0.0
        max_confidence_per_field = 0.3
        
        # 从解析的文本中提取可能的注册号/税号
        extracted_numbers = self._extract_numbers_from_text(agreement_data.parsed_text or "")
        
        # 检查注册号
        if customer.registration_number and extracted_numbers:
            for number in extracted_numbers:
                if customer.registration_number in number or number in customer.registration_number:
                    confidence += max_confidence_per_field * 0.8
                    break
        
        # 检查税号
        if customer.tax_id and extracted_numbers:
            for number in extracted_numbers:
                if customer.tax_id in number or number in customer.tax_id:
                    confidence += max_confidence_per_field * 0.7
                    break
        
        return min(confidence, 0.3)  # 其他字段最多贡献30%的置信度
    
    def _normalize_name(self, name: str) -> str:
        """
        标准化名称
        
        Args:
            name: 原始名称
            
        Returns:
            标准化后的名称
        """
        if not name:
            return ""
        
        normalized = name.strip()
        
        # 忽略大小写
        if self.config["name_matching"]["ignore_case"]:
            normalized = normalized.lower()
        
        # 标准化中文
        if self.config["name_matching"]["normalize_chinese"]:
            # 全角转半角
            normalized = self._full_to_half(normalized)
            
            # 统一中文标点
            chinese_punctuations = {
                "，": ",",
                "。": ".",
                "：": ":",
                "；": ";",
                "！": "!",
                "？": "?",
                "（": "(",
                "）": ")",
                "【": "[",
                "】": "]",
                "「": "<",
                "」": ">"
            }
            
            for chinese, ascii_char in chinese_punctuations.items():
                normalized = normalized.replace(chinese, ascii_char)
        
        # 移除常见后缀
        if self.config["name_matching"]["remove_common_suffixes"]:
            normalized = self._remove_company_suffix(normalized)
        
        # 移除多余空格
        normalized = re.sub(r'\s+', ' ', normalized).strip()
        
        return normalized
    
    def _calculate_name_similarity(self, name1: str, name2: str) -> float:
        """
        计算名称相似度
        
        Args:
            name1: 名称1
            name2: 名称2
            
        Returns:
            相似度 (0-1)
        """
        if not name1 or not name2:
            return 0.0
        
        # 使用SequenceMatcher计算相似度
        similarity = SequenceMatcher(None, name1, name2).ratio()
        
        # 如果启用了模糊匹配，考虑编辑距离
        if self.config["fuzzy_matching"]["enable"]:
            edit_distance = self._calculate_edit_distance(name1, name2)
            max_length = max(len(name1), len(name2))
            if max_length > 0:
                edit_similarity = 1.0 - (edit_distance / max_length)
                # 取两种方法的平均值
                similarity = (similarity + edit_similarity) / 2
        
        return similarity
    
    def _calculate_edit_distance(self, s1: str, s2: str) -> int:
        """
        计算编辑距离
        
        Args:
            s1: 字符串1
            s2: 字符串2
            
        Returns:
            编辑距离
        """
        if len(s1) < len(s2):
            return self._calculate_edit_distance(s2, s1)
        
        if len(s2) == 0:
            return len(s1)
        
        previous_row = range(len(s2) + 1)
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row
        
        return previous_row[-1]
    
    def _remove_company_suffix(self, name: str) -> str:
        """
        移除公司类型后缀
        
        Args:
            name: 公司名称
            
        Returns:
            移除后缀后的名称
        """
        if not name:
            return name
        
        # 常见公司后缀
        suffixes = [
            # 中文后缀
            "有限公司", "有限责任公司", "股份有限公司", "集团公司", "集团",
            "公司", "厂", "店", "行", "所", "中心", "工作室",
            
            # 英文后缀
            "limited", "ltd.", "ltd", "incorporated", "inc.",
            "inc", "company", "co.", "co", "corporation", "corp.",
            "corp", "group", "holding", "holdings", "plc",
            
            # 香港后缀
            "香港", "香港公司",
            
            # 其他
            "国际", "科技", "技术", "发展", "实业", "投资", "金融", "银行"
        ]
        
        normalized = name
        for suffix in suffixes:
            # 检查后缀（考虑空格和标点）
            patterns = [
                rf'\s*{re.escape(suffix)}\s*$',
                rf'[{re.escape("，,。.;:：")}]\s*{re.escape(suffix)}\s*$',
                rf'\({re.escape(suffix)}\)$',
                rf'\[{re.escape(suffix)}\]$'
            ]
            
            for pattern in patterns:
                normalized = re.sub(pattern, '', normalized, flags=re.IGNORECASE)
        
        return normalized.strip()
    
    def _has_same_company_suffix(self, name1: str, name2: str) -> bool:
        """
        检查是否有相同的公司后缀
        
        Args:
            name1: 名称1
            name2: 名称2
            
        Returns:
            是否有相同后缀
        """
        # 提取后缀
        def extract_suffix(name):
            suffixes = [
                "有限公司", "有限责任公司", "股份有限公司", "集团公司", "集团",
                "limited", "ltd.", "ltd", "incorporated", "inc."
            ]
            
            for suffix in suffixes:
                if name.lower().endswith(suffix.lower()):
                    return suffix.lower()
            
            return None
        
        suffix1 = extract_suffix(name1)
        suffix2 = extract_suffix(name2)
        
        return suffix1 and suffix2 and suffix1 == suffix2
    
    def _find_common_keywords(self, name1: str, name2: str) -> List[str]:
        """
        查找共同关键词
        
        Args:
            name1: 名称1
            name2: 名称2
            
        Returns:
            共同关键词列表
        """
        # 分割名称为关键词
        def extract_keywords(name):
            # 移除标点和后缀
            clean_name = re.sub(r'[^\w\u4e00-\u9fff]+', ' ', name.lower())
            clean_name = self._remove_company_suffix(clean_name)
            
            # 分割
            keywords = set()
            
            # 中文：按字分割（对于短词）
            chinese_chars = re.findall(r'[\u4e00-\u9fff]', clean_name)
            for char in chinese_chars:
                if len(char) == 1 and char not in ["公", "司", "集", "团", "有", "限"]:
                    keywords.add(char)
            
            # 英文：按单词分割
            english_words = re.findall(r'[a-z]{2,}', clean_name)
            keywords.update(english_words)
            
            return keywords
        
        keywords1 = extract_keywords(name1)
        keywords2 = extract_keywords(name2)
        
        return list(keywords1.intersection(keywords2))
    
    def _extract_numbers_from_text(self, text: str) -> List[str]:
        """
        从文本中提取数字（可能为注册号、税号等）
        
        Args:
            text: 文本
            
        Returns:
            提取的数字列表
        """
        if not text:
            return []
        
        # 匹配各种格式的号码
        patterns = [
            r'\b\d{8,15}\b',  # 8-15位数字
            r'\b[A-Z]{2}\d{6,10}\b',  # 字母开头+数字
            r'\b\d{2,4}[-]\d{6,8}\b',  # 带分隔符
            r'\b(?:注册号|税号|登記號碼|商業登記證)[:：]\s*(\S{6,20})'  # 带标签
        ]
        
        numbers = []
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            numbers.extend(matches)
        
        return numbers
    
    def _full_to_half(self, text: str) -> str:
        """
        全角转半角
        
        Args:
            text: 文本
            
        Returns:
            转换后的文本
        """
        if not text:
            return text
        
        result = ""
        for char in text:
            code = ord(char)
            if code == 0x3000:  # 全角空格
                result += ' '
            elif 0xFF01 <= code <= 0xFF5E:  # 全角字符
                result += chr(code - 0xFEE0)
            else:
                result += char
        
        return result
    
    def get_match_result(self, confidence: float) -> MatchResult:
        """
        根据置信度获取匹配结果
        
        Args:
            confidence: 置信度
            
        Returns:
            匹配结果
        """
        thresholds = self.config["confidence_thresholds"]
        
        if confidence >= thresholds["exact_match"]:
            return MatchResult.EXACT_MATCH
        elif confidence >= thresholds["auto_match"]:
            return MatchResult.HIGH_CONFIDENCE
        elif confidence >= thresholds["manual_review"]:
            return MatchResult.MEDIUM_CONFIDENCE
        elif confidence > thresholds["no_match"]:
            return MatchResult.LOW_CONFIDENCE
        else:
            return MatchResult.NO_MATCH

class DjangoCustomerMatcher(CustomerMatcher):
    """Django集成的客户匹配器"""
    
    def __init__(self, config: Optional[Dict] = None):
        """
        初始化Django客户匹配器
        
        Args:
            config: 匹配配置
        """
        super().__init__(config)
        
    def match_agreement_to_customers(
        self, 
        agreement_pdf,
        use_cached: bool = True
    ) -> Dict[str, Any]:
        """
        匹配协议到客户数据库
        
        Args:
            agreement_pdf: AgreementPDF实例
            use_cached: 是否使用缓存
            
        Returns:
            匹配结果
        """
        from django.core.cache import cache
        from django.db.models import Q
        
        self.logger.info(f"开始匹配协议: {agreement_pdf.id}")
        
        # 检查缓存
        cache_key = f"agreement_match_{agreement_pdf.id}"
        if use_cached:
            cached_result = cache.get(cache_key)
            if cached_result:
                self.logger.info(f"使用缓存的匹配结果: {agreement_pdf.id}")
                return cached_result
        
        # 准备协议数据
        agreement_data = AgreementData(
            borrower_name=agreement_pdf.borrower_name,
            agreement_date=agreement_pdf.agreement_date,
            facility_amount=agreement_pdf.facility_amount,
            currency=agreement_pdf.currency,
            parsed_text=agreement_pdf.parsed_text
        )
        
        # 获取客户列表
        try:
            from credit_app.models import Customer as CustomerModel
            
            # 如果有借款人名称，先尝试精确匹配
            if agreement_data.borrower_name:
                # 构建查询条件
                query = Q(name__iexact=agreement_data.borrower_name)
                
                # 检查别名
                query |= Q(aliases__alias__iexact=agreement_data.borrower_name)
                
                # 获取客户
                customers_qs = CustomerModel.objects.filter(query).distinct()
                
                # 如果没有精确匹配，获取所有客户进行模糊匹配
                if not customers_qs.exists():
                    customers_qs = CustomerModel.objects.all()[:100]  # 限制数量
            else:
                customers_qs = CustomerModel.objects.all()[:100]
            
            # 转换为Customer对象列表
            customers = []
            for cust in customers_qs:
                # 获取别名
                aliases = list(cust.aliases.values_list('alias', flat=True))
                
                customer = Customer(
                    id=cust.id,
                    name=cust.name,
                    name_aliases=aliases,
                    registration_number=cust.registration_number,
                    tax_id=cust.tax_id,
                    industry=cust.industry,
                    country=cust.country
                )
                customers.append(customer)
            
            self.logger.info(f"获取到 {len(customers)} 个客户进行匹配")
            
        except ImportError as e:
            self.logger.error(f"导入Customer模型失败: {e}")
            return {
                "status": "error",
                "message": "Customer model not found"
            }
        
        except Exception as e:
            self.logger.error(f"获取客户数据失败: {e}")
            return {
                "status": "error",
                "message": f"Failed to get customers: {str(e)}"
            }
        
        # 执行匹配
        try:
            candidates = self.find_matches(
                agreement_data=agreement_data,
                customers=customers,
                strategy=MatchStrategy.COMBINED
            )
            
            # 构建结果
            result = {
                "agreement_id": agreement_pdf.id,
                "borrower_name": agreement_data.borrower_name,
                "total_candidates": len(customers),
                "matches_found": len(candidates),
                "candidates": [],
                "best_match": None,
                "match_result": MatchResult.NO_MATCH.value,
                "recommendation": "no_match"
            }
            
            if candidates:
                # 添加候选
                for candidate in candidates[:5]:  # 只返回前5个
                    result["candidates"].append(candidate.to_dict())
                
                # 最佳匹配
                best_candidate = candidates[0]
                result["best_match"] = best_candidate.to_dict()
                
                # 确定匹配结果
                match_result = self.get_match_result(best_candidate.confidence)
                result["match_result"] = match_result.value
                
                # 生成推荐
                if match_result in [MatchResult.EXACT_MATCH, MatchResult.HIGH_CONFIDENCE]:
                    result["recommendation"] = "auto_match"
                    result["recommended_customer_id"] = best_candidate.customer.id
                elif match_result == MatchResult.MEDIUM_CONFIDENCE:
                    result["recommendation"] = "manual_review"
                else:
                    result["recommendation"] = "no_match"
            
            # 更新数据库状态
            self._update_agreement_status(agreement_pdf, result)
            
            # 缓存结果
            cache.set(cache_key, result, timeout=3600)  # 缓存1小时
            
            self.logger.info(f"协议匹配完成: {agreement_pdf.id}")
            return result
            
        except Exception as e:
            self.logger.error(f"匹配过程失败: {e}", exc_info=True)
            return {
                "status": "error",
                "message": f"Matching failed: {str(e)}"
            }
    
    def _update_agreement_status(self, agreement_pdf, match_result: Dict[str, Any]):
        """
        更新协议状态
        
        Args:
            agreement_pdf: AgreementPDF实例
            match_result: 匹配结果
        """
        try:
            # 更新匹配状态
            if match_result.get("recommendation") == "auto_match":
                agreement_pdf.match_status = "matched"
                agreement_pdf.match_type = "auto"
                agreement_pdf.match_confidence = match_result["best_match"]["confidence"]
                
                # 设置客户
                customer_id = match_result.get("recommended_customer_id")
                if customer_id:
                    from credit_app.models import Customer
                    try:
                        customer = Customer.objects.get(id=customer_id)
                        agreement_pdf.customer = customer
                    except Customer.DoesNotExist:
                        self.logger.warning(f"客户不存在: {customer_id}")
            
            elif match_result.get("recommendation") == "manual_review":
                agreement_pdf.match_status = "manual_review"
                agreement_pdf.match_type = "candidate"
                agreement_pdf.match_confidence = match_result["best_match"]["confidence"]
            
            else:
                agreement_pdf.match_status = "unmatched"
                agreement_pdf.match_type = None
                agreement_pdf.match_confidence = None
            
            # 保存匹配结果到JSON字段（如果有）
            if hasattr(agreement_pdf, 'match_result'):
                agreement_pdf.match_result = {
                    "match_details": match_result,
                    "matched_at": datetime.now().isoformat()
                }
            
            agreement_pdf.save()
            
            self.logger.info(f"更新协议状态: {agreement_pdf.id} -> {agreement_pdf.match_status}")
            
        except Exception as e:
            self.logger.error(f"更新协议状态失败: {e}")

# Django管理命令
def match_all_pending_agreements():
    """
    匹配所有待处理的协议
    """
    from django.core.management.base import BaseCommand
    from agreement_parser.models import AgreementPDF
    
    class Command(BaseCommand):
        help = '匹配所有待处理的协议'
        
        def handle(self, *args, **options):
            matcher = DjangoCustomerMatcher()
            
            # 获取所有待匹配的协议
            pending_agreements = AgreementPDF.objects.filter(
                parsing_status='parsed',
                match_status='pending'
            )
            
            self.stdout.write(f"找到 {pending_agreements.count()} 个待匹配的协议")
            
            success = 0
            failed = 0
            
            for agreement in pending_agreements:
                try:
                    result = matcher.match_agreement_to_customers(agreement)
                    
                    if result.get("status") == "error":
                        self.stdout.write(self.style.ERROR(f"协议 {agreement.id} 匹配失败: {result.get('message')}"))
                        failed += 1
                    else:
                        self.stdout.write(self.style.SUCCESS(f"协议 {agreement.id} 匹配完成: {result.get('match_result')}"))
                        success += 1
                        
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"协议 {agreement.id} 匹配异常: {e}"))
                    failed += 1
            
            self.stdout.write(self.style.SUCCESS(f"\n匹配完成: 成功={success}, 失败={failed}"))

# 异步任务
def async_match_agreement(agreement_id: int):
    """
    异步匹配协议
    
    Args:
        agreement_id: 协议ID
    """
    from celery import shared_task
    
    @shared_task(bind=True, max_retries=3)
    def match_agreement_task(self, agreement_id):
        from agreement_parser.models import AgreementPDF
        
        try:
            agreement = AgreementPDF.objects.get(id=agreement_id)
            matcher = DjangoCustomerMatcher()
            
            result = matcher.match_agreement_to_customers(agreement)
            
            logger.info(f"异步匹配完成: {agreement_id}, 结果: {result.get('match_result')}")
            
            return {
                "status": "success",
                "agreement_id": agreement_id,
                "match_result": result
            }
            
        except AgreementPDF.DoesNotExist:
            logger.error(f"协议不存在: {agreement_id}")
            raise
            
        except Exception as e:
            logger.error(f"异步匹配失败: {agreement_id}, 错误: {e}")
            
            # 重试
            raise self.retry(exc=e, countdown=60)
    
    return match_agreement_task.delay(agreement_id)
