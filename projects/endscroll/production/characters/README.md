# 角色参考图（第 1 季，风格 A：皮克斯 3D）

生成视频时，把对应的 Higgsfield job id 作为 `image_references` 传入，保持角色一致。

| 角色 | 文件 | Higgsfield job id |
| --- | --- | --- |
| 风格基准帧（Scroll 采访间） | style_test/A_pixar3d.png | e39d6598-f228-48dd-aaa7-46d78357bbfd |
| Scroll | scroll.png | cf8b3933-2047-4710-bfc4-6ed989e7b61f |
| Filter | filter.png | 39450f7d-c7f6-4f80-8666-c807f7c49aab |
| Autoplay | autoplay.png | 3e1c7e20-5c9b-4bb3-9225-a68a2a6313e8 |
| Phoebe（主持人） | phoebe.png | 9c52116f-091a-4b1e-a34d-e19e35074ea0 |
| Lucky（手游，抽卡女孩） | lucky.png | a0cbe544-dd1a-41cb-a36c-b6cd9a566558 |
| Alarm | alarm.png | 9d22f14c-f540-4a5a-8194-44c8f7cfd993 |
| Weekly Report | weekly_report.png | 2f7d377a-02d7-4148-91a7-26a6e36dfa13 |
| Shelly（第 4 集登场，未做） | — | 海龟参考 media 34676454-7298-4e5e-aaf0-b52da564e46c |

- Phoebe v1 太性感（低胸短裙），会被 TikTok 判为性暗示、不推给未成年人，已改成亮片西装，旧图在 `rejected/`。
- 风格 B（黏土）没选：和 app 海龟不统一，Seedance 动起来不稳。

## 暗示规则（10-10 定）

不说名字，靠服饰和道具让人一眼认出；用品牌主色 + 通用符号，但组合方式和 logo 不同。不复制 logo，不改字母，不投广告。主页简介加 `parody · not affiliated with any app`。

| 角色 | 暗示 | 线索 | 避开 |
| --- | --- | --- | --- |
| Scroll | TikTok | 黑夹克 + 青、粉两道分开的霓虹边，白色音符项链，单只耳机，屏幕脸后有竖屏小视频，招牌动作「拇指上弹」 | 青红错位叠影、logo 音符形状 |
| Filter | Instagram | 紫粉橙日落渐变衣服，复古实物相机，光环，自拍杆，心形墨镜 | 渐变圆角方框相机图标 |
| Autoplay | YouTube / Netflix | 全身红，播放三角形镜片墨镜，爆米花，遥控器，屏幕边倒计时圈 | 红色圆角矩形里放白三角、字母 N |
| Lucky | 手游 | 宝石蓝金色手机头，星星眼，体力条发卡，宝箱手提包，彩色宝石耳环，稀有度光效裙子 | 赌场筹码、现金、老虎机、方块人 |
| Phoebe | 手机通知 | 红色通知角标耳环 | — |
| Weekly Report | 屏幕使用时间 | 秒表，柱状图写字板 | 沙漏 |

旧版（暗示太弱）在 `v1/`。

## 阵容（10-11 定）

- 固定嘉宾（两男两女）：Scroll（坏男孩）、Autoplay（暖男，已改成熟版）、Filter、Lucky
- 主持人：Phoebe；配角：Alarm、Weekly Report
- 炸弹嘉宾：ep4 Shelly，中期 Streak（Snapchat 火花，黏人女友），后半季 AI 伴侣（不碰自伤），黑五购物狂客串
- 不做：约会 app（观众 18+、性暗示限流）、体育博彩、学习 app

## 海龟主角候选（10-13，待老板选）

老板 10-13 同意试海龟当主角，要求比 app 里的扁平版更可爱，参考毛绒盲盒玩具和 Calmlings 的质感。三个方向都保留了 app 海龟的脸（大白眼、小鼻孔、弯嘴）和亮绿色。对比图：`shelly_options/options.jpg`。

| 方向 | 文件 | Higgsfield job id |
| --- | --- | --- |
| A 羊毛毡玩具 | shelly_options/A_felt.png | d812ac4d-ffd9-409f-abaa-90f64b6f63aa |
| B 毛绒小生物（最接近 Calmlings） | shelly_options/B_fluffy.png | ba0bc778-e35c-4cfe-9e2c-53b2d700370d |
| C 软胶盲盒，戴睡帽（最接近 app 原图） | shelly_options/C_vinyl.png | f7cbfbee-d866-4e05-bb61-e735a3a2b8f0 |

**10-13 老板选了 B。** 四视图角色参考：`shelly.png`，Higgsfield job id `332f4e7f-0b47-4c08-bfa1-7622be8467a0`。以后生成海龟的镜头，把这个 id 作为 `image_references` 传入。

海龟系列的规则（老板 10-13）：

- 先拍没有产品、没有负担的治愈小场景，用来检验这个形象；不放广告。
- 发在新建的 TikTok 账号和 Facebook 公共主页上，和之前 App Island 的账号分开。
- 一个角色、一个注意点、一句观众自己会说的话（`knowledge/attention.md`）。
