# -*- coding: utf-8 -*-
"""UTF-8 真实评分测试"""
import urllib.request, json

def post(url, data, token):
    req = urllib.request.Request(url, data=json.dumps(data).encode('utf-8'),
        headers={'Content-Type': 'application/json', 'Authorization': 'Bearer ' + token})
    return json.loads(urllib.request.urlopen(req, timeout=300).read().decode('utf-8'))

login = post('http://127.0.0.1:8090/prod-api/login', {'username': 'admin', 'password': 'admin123', 'code': '', 'uuid': ''}, '')
token = login['token']

content = {
    '1': 'N市积极落实惠企政策：一是开设绿色通道，资金直达快兑，实现“秒兑”；二是推出“免申即享”服务，由“人找政策”变“政策找人”；三是搭建“亲清家园”智慧服务平台，植入智慧监督功能，全程无纸化在线审批；四是实现涉税业务全国通办、跨省通办。成效：为企业纾困解难，构建亲清政商关系，增强企业获得感，提升政务服务效率。',
    '2': '这句话指政府服务不仅要撤掉“眼中的柜台”（物理柜台），更要撤掉“心中的柜台”——转变服务观念，提升业务能力，真正贴近群众，让改革红利惠及更多群众。',
    '3': '关于巩固税收服务成果的建议：一、推动服务智能化，构建集成服务应用平台；二、创新“线上+线下”陪办服务新模式并常态化；三、完善二维码一次性告知与巡回指导；四、开展党员服务队活动与热线服务；五、推出“办税指南针”与第三方“一对一”辅导。',
    '4': 'L海关工作经验提纲：一、形成科学完备的检疫监管体系；二、积极应对国外技术性贸易措施变化；三、发挥重点实验室科技引领作用；四、实施针对性帮扶解决引种难题；五、创新预约通关等监管模式提升效率。',
    '5': '致广大市民朋友的一封公开信：说明执法初衷与依据，正视执法标准问题，承诺完善配套细则、优化执法方式、引导商家自律、畅通监督渠道，号召全社会共同节约粮食。'
}
r = post('http://127.0.0.1:8090/prod-api/shenlun/answer/grade', {'paperId': 1, 'content': json.dumps(content, ensure_ascii=False)}, token)
d = r['data']
print('success:', d.get('success'), '| 总分:', d.get('grade', {}).get('totalScore'), '/', d.get('grade', {}).get('maxScore'))
for g in d.get('grade', {}).get('grades', []):
    print('第%d题: %s/%s' % (g['qno'], g['score'], g['maxScore']))
    print('  分析:', g['analysis'][:120])
