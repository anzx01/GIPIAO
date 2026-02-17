"""
输入验证工具
"""

import re
from typing import Optional
from fastapi import HTTPException, status


def validate_stock_code(code: str) -> str:
    """
    验证股票代码格式
    
    Args:
        code: 股票代码
        
    Returns:
        str: 标准化后的股票代码
        
    Raises:
        HTTPException: 如果股票代码格式无效
    """
    if not code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="股票代码不能为空"
        )
    
    code = code.strip().upper()
    
    pattern = r'^\d{6}(\.(SH|SZ))?$'
    
    if not re.match(pattern, code):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"无效的股票代码格式: {code}。正确格式应为: 600519.SH 或 000858.SZ"
        )
    
    if len(code) == 6:
        if code.startswith(('600', '601', '603', '605')):
            code = f"{code}.SH"
        elif code.startswith(('000', '001', '002', '003', '300')):
            code = f"{code}.SZ"
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"无法识别股票代码: {code}"
            )
    
    return code


def validate_date_format(date_str: str, format: str = "%Y%m%d") -> str:
    """
    验证日期格式
    
    Args:
        date_str: 日期字符串
        format: 日期格式
        
    Returns:
        str: 标准化后的日期字符串
        
    Raises:
        HTTPException: 如果日期格式无效
    """
    if not date_str:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="日期不能为空"
        )
    
    try:
        from datetime import datetime
        datetime.strptime(date_str, format)
        return date_str
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"无效的日期格式: {date_str}。正确格式应为: {format}"
        )


def validate_pagination(page: int, page_size: int) -> tuple:
    """
    验证分页参数
    
    Args:
        page: 页码
        page_size: 每页数量
        
    Returns:
        tuple: (page, page_size)
        
    Raises:
        HTTPException: 如果分页参数无效
    """
    if page < 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="页码必须大于0"
        )
    
    if page_size < 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="每页数量必须大于0"
        )
    
    if page_size > 100:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="每页数量不能超过100"
        )
    
    return page, page_size


def validate_portfolio_weights(stocks: dict) -> dict:
    """
    验证投资组合权重
    
    Args:
        stocks: 股票代码及权重字典
        
    Returns:
        dict: 验证后的投资组合
        
    Raises:
        HTTPException: 如果权重无效
    """
    if not stocks:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="投资组合不能为空"
        )
    
    total_weight = 0.0
    validated_stocks = {}
    
    for code, weight in stocks.items():
        validated_code = validate_stock_code(code)
        
        if not isinstance(weight, (int, float)):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"股票 {code} 的权重必须是数字"
            )
        
        if weight <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"股票 {code} 的权重必须大于0"
            )
        
        if weight > 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"股票 {code} 的权重不能超过1"
            )
        
        validated_stocks[validated_code] = float(weight)
        total_weight += weight
    
    if abs(total_weight - 1.0) > 0.01:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"投资组合权重总和必须为1，当前总和为: {total_weight:.2f}"
        )
    
    return validated_stocks


def validate_username(username: str) -> str:
    """
    验证用户名
    
    Args:
        username: 用户名
        
    Returns:
        str: 验证后的用户名
        
    Raises:
        HTTPException: 如果用户名无效
    """
    if not username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名不能为空"
        )
    
    username = username.strip()
    
    if len(username) < 3:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名长度至少为3个字符"
        )
    
    if len(username) > 20:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名长度不能超过20个字符"
        )
    
    pattern = r'^[a-zA-Z0-9_\u4e00-\u9fa5]+$'
    if not re.match(pattern, username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名只能包含字母、数字、下划线和中文"
        )
    
    return username


def validate_email(email: Optional[str]) -> Optional[str]:
    """
    验证邮箱地址
    
    Args:
        email: 邮箱地址
        
    Returns:
        Optional[str]: 验证后的邮箱地址
        
    Raises:
        HTTPException: 如果邮箱格式无效
    """
    if not email:
        return None
    
    email = email.strip()
    
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="邮箱格式无效"
        )
    
    return email


def validate_password(password: str) -> str:
    """
    验证密码强度
    
    Args:
        password: 密码
        
    Returns:
        str: 验证后的密码
        
    Raises:
        HTTPException: 如果密码强度不足
    """
    if not password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="密码不能为空"
        )
    
    if len(password) < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="密码长度至少为6个字符"
        )
    
    if len(password) > 50:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="密码长度不能超过50个字符"
        )
    
    return password


def sanitize_string(input_str: str, max_length: int = 1000) -> str:
    """
    清理字符串输入
    
    Args:
        input_str: 输入字符串
        max_length: 最大长度
        
    Returns:
        str: 清理后的字符串
    """
    if not input_str:
        return ""
    
    input_str = input_str.strip()
    
    if len(input_str) > max_length:
        input_str = input_str[:max_length]
    
    dangerous_chars = ['<', '>', '"', "'", '&', '\x00', '\n', '\r']
    for char in dangerous_chars:
        input_str = input_str.replace(char, '')
    
    return input_str
