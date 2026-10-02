::ILANG
[TYPE:instructions][PROJECT:vps-deals][LANG:zh]
::STATE{@PROJECT, purpose:公开官方来源的VPS优惠与价格监测, runtime:Python标准库静态站}
::RULE{配置唯一真源⇒.ilang/site.ilang;scraper.py与build.py都必须读取}
::RULE{允许⇒修复解析器 改模板 增加公开官方来源 测试 部署}
::RULE{来源⇒只读公开官方价格页feed或sitemap;先检查robots;失败不绕过}
::RULE{单条记录⇒厂商+真实方案名+币种去重;必须有当期价来源和购买条件}
::RULE{改配置⇒重跑抓取与构建;测试移除厂商后页面和导航都消失}
::RULE{域名切换⇒实际Pages域名或已激活自定义域名回写base_url与@SITE.domain;生成canonical/sitemap/robots后从外部验证}
::RULE{联盟⇒仅使用已获批准的正规联盟链接;没有批准时保持官网裸链并明确无佣金}
::BOUNDARY{never:编优惠价格佣金期限 刷量 买粉 绕反爬 品牌词竞价 cookie注入 自买自推|scope:permanent}
::BOUNDARY{never:把凭据或令牌提交仓库;发布未经核验优惠;宣称域名年龄保证排名|scope:permanent}
::RULE{验证⇒python -m unittest discover -s tests;python scraper.py;python build.py;核查线上schema与sitemap}
