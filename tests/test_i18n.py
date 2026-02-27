#!/usr/bin/env python3
"""
Uni-Lab-OS i18n 国际化支持测试

测试内容：
1. 语言切换功能
2. 翻译字符串匹配
3. 翻译文件加载
"""

import os
import sys
import unittest

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from unilabos.i18n import _, ngettext, set_language, get_current_language, SUPPORTED_LANGUAGES


class TestI18n(unittest.TestCase):
    """i18n 功能测试"""
    
    def setUp(self):
        """测试前设置默认语言"""
        set_language("en_US")
    
    def tearDown(self):
        """测试后恢复默认语言"""
        set_language("en_US")
    
    def test_supported_languages(self):
        """测试支持的语言列表"""
        self.assertIn("en_US", SUPPORTED_LANGUAGES)
        self.assertIn("zh_CN", SUPPORTED_LANGUAGES)
        self.assertEqual(SUPPORTED_LANGUAGES["en_US"], "English")
        self.assertEqual(SUPPORTED_LANGUAGES["zh_CN"], "中文")
    
    def test_set_language(self):
        """测试语言切换"""
        # 测试有效语言
        self.assertTrue(set_language("en_US"))
        self.assertEqual(get_current_language(), "en_US")
        
        self.assertTrue(set_language("zh_CN"))
        self.assertEqual(get_current_language(), "zh_CN")
        
        # 测试无效语言
        self.assertFalse(set_language("invalid_lang"))
        # 语言应该保持之前的设置
        self.assertEqual(get_current_language(), "zh_CN")
    
    def test_english_translation(self):
        """测试英文翻译（默认语言，应返回原字符串）"""
        set_language("en_US")
        
        # 英文是默认语言，应该返回原字符串
        self.assertEqual(_("Version:"), "Version:")
        self.assertEqual(_("System:"), "System:")
        self.assertEqual(_("Configuration:"), "Configuration:")
    
    def test_chinese_translation(self):
        """测试中文翻译"""
        set_language("zh_CN")
        
        # 测试已翻译的字符串
        self.assertEqual(_("Version:"), "版本：")
        self.assertEqual(_("System:"), "系统：")
        self.assertEqual(_("Configuration:"), "配置：")
        self.assertEqual(_("Backend:"), "后端：")
        self.assertEqual(_("INFO"), "信息")
        self.assertEqual(_("SUCCESS"), "成功")
        self.assertEqual(_("WARNING"), "警告")
        self.assertEqual(_("ERROR"), "错误")
    
    def test_missing_translation(self):
        """测试缺失翻译时应返回原字符串"""
        set_language("zh_CN")
        
        # 测试未翻译的字符串应该返回原字符串
        untranslated = "This string does not exist in translations"
        self.assertEqual(_(untranslated), untranslated)
    
    def test_formatted_strings(self):
        """测试格式化字符串翻译"""
        set_language("zh_CN")
        
        # 测试带格式的字符串
        result = _("发现 {count} 个缺失的包").format(count=5)
        self.assertEqual(result, "发现 5 个缺失的包")
        
        result = _("设备信息已保存到 {path}").format(path="/tmp/test.json")
        self.assertEqual(result, "设备信息已保存到 /tmp/test.json")
    
    def test_ngettext(self):
        """测试复数形式翻译"""
        # 英文测试
        set_language("en_US")
        self.assertEqual(ngettext("One item", "{n} items", 1), "One item")
        self.assertEqual(ngettext("One item", "{n} items", 5), "{n} items")
        
        # 中文测试（中文没有复数变化，应该返回复数形式）
        set_language("zh_CN")
        result = ngettext("One item", "{n} items", 1)
        # 中文应该使用复数形式
        self.assertIn(result, ["{n} items"])  # 如果未翻译则返回原字符串
    
    def test_translation_files_exist(self):
        """测试翻译文件是否存在"""
        from unilabos.i18n import get_locale_dir
        
        locale_dir = get_locale_dir()
        
        # 检查英文翻译文件
        en_po = os.path.join(locale_dir, "en_US", "LC_MESSAGES", "messages.po")
        en_mo = os.path.join(locale_dir, "en_US", "LC_MESSAGES", "messages.mo")
        self.assertTrue(os.path.exists(en_po), f"English PO file not found: {en_po}")
        self.assertTrue(os.path.exists(en_mo), f"English MO file not found: {en_mo}")
        
        # 检查中文翻译文件
        zh_po = os.path.join(locale_dir, "zh_CN", "LC_MESSAGES", "messages.po")
        zh_mo = os.path.join(locale_dir, "zh_CN", "LC_MESSAGES", "messages.mo")
        self.assertTrue(os.path.exists(zh_po), f"Chinese PO file not found: {zh_po}")
        self.assertTrue(os.path.exists(zh_mo), f"Chinese MO file not found: {zh_mo}")
    
    def test_translation_content(self):
        """测试翻译文件内容"""
        from unilabos.i18n import get_locale_dir, _load_po_file
        
        # 加载中文翻译
        zh_translations = _load_po_file("zh_CN")
        
        # 验证关键翻译存在
        self.assertIn("Version:", zh_translations)
        self.assertEqual(zh_translations["Version:"], "版本：")
        
        self.assertIn("INFO", zh_translations)
        self.assertEqual(zh_translations["INFO"], "信息")
    
    def test_environment_variable(self):
        """测试环境变量设置语言"""
        import importlib
        
        # 保存原始环境变量
        original_lang = os.environ.get("UNILABOS_LANGUAGE")
        
        try:
            # 设置中文环境变量
            os.environ["UNILABOS_LANGUAGE"] = "zh_CN"
            
            # 重新加载模块以触发 _init_language
            if "unilabos.i18n" in sys.modules:
                del sys.modules["unilabos.i18n"]
            
            from unilabos.i18n import get_current_language
            
            # 验证语言已切换
            self.assertEqual(get_current_language(), "zh_CN")
            
        finally:
            # 恢复原始环境变量
            if original_lang is not None:
                os.environ["UNILABOS_LANGUAGE"] = original_lang
            elif "UNILABOS_LANGUAGE" in os.environ:
                del os.environ["UNILABOS_LANGUAGE"]
            
            # 恢复默认语言
            set_language("en_US")


class TestI18nIntegration(unittest.TestCase):
    """i18n 集成测试 - 测试实际使用场景"""
    
    def setUp(self):
        """测试前设置为英文"""
        set_language("en_US")
    
    def tearDown(self):
        """测试后恢复默认语言"""
        set_language("en_US")
    
    def test_banner_print_integration(self):
        """测试横幅打印功能存在并可调用"""
        from unilabos.utils.banner_print import print_status
        
        # 简单测试函数可以被调用不抛出异常
        import io
        import sys
        
        captured = io.StringIO()
        old_stdout = sys.stdout
        sys.stdout = captured
        
        try:
            print_status("Test message", "info")
            output = captured.getvalue()
            # 只要有输出即可，不管语言
            self.assertTrue(len(output) > 0)
            self.assertIn("Test message", output)
        finally:
            sys.stdout = old_stdout
    
    def test_i18n_core_functionality(self):
        """测试 i18n 核心功能 - 语言切换"""
        # 测试语言切换功能
        set_language("en_US")
        self.assertEqual(get_current_language(), "en_US")
        
        set_language("zh_CN")
        self.assertEqual(get_current_language(), "zh_CN")
        
        # 测试翻译
        set_language("en_US")
        self.assertEqual(_("Version:"), "Version:")
        
        set_language("zh_CN")
        self.assertEqual(_("Version:"), "版本：")


def run_tests():
    """运行所有测试"""
    # 创建测试套件
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # 添加测试类
    suite.addTests(loader.loadTestsFromTestCase(TestI18n))
    suite.addTests(loader.loadTestsFromTestCase(TestI18nIntegration))
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # 返回测试结果
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
