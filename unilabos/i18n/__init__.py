"""
Uni-Lab-OS i18n 国际化支持模块

提供多语言支持，支持英文和中文。
使用方式：
    from unilabos.i18n import _, ngettext
    
    # 简单翻译
    print(_("Hello World"))
    
    # 复数形式
    print(ngettext("One item", "{count} items", count).format(count=count))
"""

import gettext
import os
import re
from typing import Optional, Dict

# 当前语言设置
_current_language: str = "en_US"
_translation: Optional[gettext.GNUTranslations] = None
_po_translations: Dict[str, str] = {}

# 支持的语言
SUPPORTED_LANGUAGES = {
    "en_US": "English",
    "zh_CN": "中文",
}

DEFAULT_LANGUAGE = "en_US"


def get_locale_dir() -> str:
    """获取本地化文件目录"""
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "locales")


def _load_po_file(lang_code: str) -> Dict[str, str]:
    """
    从 PO 文件加载翻译
    
    Args:
        lang_code: 语言代码
        
    Returns:
        翻译字典 {msgid: msgstr}
    """
    translations = {}
    po_path = os.path.join(get_locale_dir(), lang_code, "LC_MESSAGES", "messages.po")
    
    if not os.path.exists(po_path):
        return translations
    
    try:
        with open(po_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 使用正则表达式解析 PO 文件
        # 匹配 msgid "..." 和 msgstr "..." 对
        pattern = r'msgid\s+"([^"]*)"\s+msgstr\s+"([^"]*)"'
        matches = re.findall(pattern, content, re.DOTALL)
        
        for msgid, msgstr in matches:
            # 处理多行字符串（去掉换行符）
            msgid = msgid.replace('"\n"', '')
            msgstr = msgstr.replace('"\n"', '')
            if msgstr:  # 只保存有翻译的
                translations[msgid] = msgstr
                
    except Exception as e:
        print(f"Warning: Failed to load PO file: {e}")
    
    return translations


def set_language(lang_code: str) -> bool:
    """
    设置当前语言
    
    Args:
        lang_code: 语言代码，如 "en_US", "zh_CN"
        
    Returns:
        是否设置成功
    """
    global _current_language, _translation, _po_translations
    
    if lang_code not in SUPPORTED_LANGUAGES:
        return False
    
    _current_language = lang_code
    _po_translations = {}
    
    if lang_code == DEFAULT_LANGUAGE:
        _translation = None
        return True
    
    locale_dir = get_locale_dir()
    
    # 首先尝试加载 MO 文件
    mo_path = os.path.join(locale_dir, lang_code, "LC_MESSAGES", "messages.mo")
    if os.path.exists(mo_path):
        try:
            with open(mo_path, 'rb') as f:
                _translation = gettext.GNUTranslations(f)
            return True
        except Exception:
            pass
    
    # 如果 MO 文件不存在或加载失败，加载 PO 文件
    _po_translations = _load_po_file(lang_code)
    _translation = None  # 使用 PO 文件翻译
    
    return True


def get_current_language() -> str:
    """获取当前语言代码"""
    return _current_language


def _(message: str) -> str:
    """
    翻译字符串
    
    Args:
        message: 要翻译的字符串
        
    Returns:
        翻译后的字符串
    """
    global _translation, _po_translations
    
    if _translation is not None:
        return _translation.gettext(message)
    elif _po_translations:
        return _po_translations.get(message, message)
    return message


def ngettext(singular: str, plural: str, n: int) -> str:
    """
    翻译复数形式的字符串
    
    Args:
        singular: 单数形式
        plural: 复数形式
        n: 数量
        
    Returns:
        根据数量选择合适的翻译
    """
    global _translation, _po_translations
    
    if _translation is not None:
        return _translation.ngettext(singular, plural, n)
    elif _po_translations:
        # 中文没有复数变化，英文按数量判断
        if _current_language == "zh_CN":
            return _po_translations.get(plural, plural)
        else:
            return _po_translations.get(singular if n == 1 else plural, 
                                      singular if n == 1 else plural)
    return singular if n == 1 else plural


# 便捷别名
gettext = _
N = ngettext


# 初始化：尝试从环境变量读取语言设置
def _init_language():
    """初始化语言设置"""
    import os
    env_lang = os.environ.get("UNILABOS_LANGUAGE", "")
    if env_lang in SUPPORTED_LANGUAGES:
        set_language(env_lang)
    else:
        # 尝试从系统环境变量推断
        sys_lang = os.environ.get("LANG", "")
        if "zh" in sys_lang.lower():
            set_language("zh_CN")
        else:
            set_language(DEFAULT_LANGUAGE)


# 模块导入时初始化
_init_language()
