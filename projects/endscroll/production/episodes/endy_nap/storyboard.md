# Endy & Shelly · I Took A Nap（翻拍 @sadgoose42）

- **参考**：@sadgoose42「I Took A Nap」https://www.tiktok.com/@sadgoose42/video/7693257487427865889 · 10-05 发 · 9 秒 · 140 万播放 / 18.3 万赞 / 6.4 万分享（4.6%）/ 2.2 万收藏。和 Keep going 是同一个作者。拆解在 `references/sadgoose42_7693257487427865889/`（notes.md、contact_sheet.jpg、ref.mp4）。
- **为什么做**：老板 10-17 点名。原片很短（9 秒），一个固定镜头，歌词就是字幕，一个爆点，结尾治愈，分享率很高，正好是 IG 推 Keep going 的那种东西。
- **测试的假设**：把 140 万播放的热门原声短片换成我们的两只海龟，IG 分享和收藏能达到 Keep going 的一半（分享 ≥0.8%、收藏 ≥0.7%）。
- **预测分 66（hold）**，目前最高（打气 2 号 56）。预估：3 秒留存 0.78 · 平均观看 0.85 · 完播 0.45 · 分享 0.01 · 收藏 0.007 · 点赞 0.05 · 评论 0.001 · 关注 0.002。依据是 Keep going 在 IG 24 小时的实测，分享和收藏打对折；时长只有 10 秒，所以完播估得比以往高很多。

## 固定不变的（freeze list）

| 项目 | 定死为 |
| --- | --- |
| 角色 | **Endy**（绿色毛绒海龟，不戴帽子，浅蓝小围巾，一个橄榄色壳，参考 `characters/shelly.png`，job `332f4e7f-…`）；**Shelly**（紫色，睫毛和腮红，不戴花，参考 `characters/coral.png`，job `83b8aa07-…`）。两只一样大。画面里最多两只，第 6 秒前只有 Endy。 |
| 画风 | 和 Keep going 一样：毛绒 3D、暖色柔光、浅景深（`goose_keep_going/keyframes/K1_bike.png`） |
| 场景 | 温暖的小客厅，按我们的画风重画，不照搬原片：米黄色竖条纹墙纸、一盏暖黄吊灯、墙上一块小搁板放一盆小绿植、橄榄绿单人沙发在后面、暖红棕色地板。三张关键帧用同一个场景。 |
| 机位 | 正面平视全景，**全程不动**，没有剪切（原片也没有切点）。角色站在画面中间偏下，头顶上方留出放字的空间。 |
| 声音 | 原曲「I Took A Nap」— gunnarolla。不加别的音乐和音效。 |
| 字幕 | 歌词逐词亮起（assemble 的 karaoke「lit」样式，和 Keep going 一致），白字，画面上方居中，一次一行。 |
| 时长 | 约 10 秒：9 秒的歌，加最后 1 秒定格，方便循环。 |
| 不出现 | 手机、logo、任何文字（纸上也是空白或只有看不清的横线）。 |

## 分镜（时间按原曲逐词对齐）

| 秒 | 歌词（逐词亮起） | 画面 | 观众此刻注意的一件事 |
| --- | --- | --- | --- |
| 0.0–2.1 | I had a lot of things to do today, | Endy 站在正中，双手抱着一摞比他头还高的白纸，下巴抬着，闭眼，很自豪。几乎不动，只有呼吸。 | 读这一句 |
| 2.1–3.7 | but you know what I did? | 同上，憋着，眼睛睁开一条缝，往旁边瞄一下 | 读这一句 |
| 3.7–4.6 | I…（拖长） | **纸往上炸开**，Endy 往后一倒 | 看纸炸开 |
| 4.6–6.4 | took a nap. | 头和四肢缩进壳里，壳平躺在地上，纸慢慢飘落一地。从壳口能看到他闭着眼在笑。 | 看他缩进壳里 |
| 6.4–8.0 | It was a very good nap | Shelly 从画面右边走进来，手里抱一条暖色格子小毯子，轻轻盖在 Endy 的壳上，唱到「nap」时正好盖好 | 看 Shelly 盖毯子 |
| 8.0–10.0 | （歌停） | 定格：Endy 盖着毯子睡着，Shelly 蹲在旁边看着他，纸散在地上 | 一个安静的画面，接回开头循环 |

- **和原片的不同**：原片里鹅软成一摊，被挪到沙发上盖毯子。我们换成**缩进壳里睡觉**，只有海龟能做；盖毯子的人换成 Shelly，给情侣号留一点甜。其余的节奏、构图、字幕都照原片。
- **注意力**：每一刻只发生一件事：读字 → 纸炸开 → 缩进壳 → Shelly 盖毯子。Shelly 在第 6.4 秒才进来，那时 Endy 已经不动了。

## 生成计划（批准前不花任何积分）

**关键帧**（GPT Image 2.5，竖版 9:16，每张约 1 积分）。三张用同一段场景描述，Endy 和 Shelly 的参考图作为 `image_references` 传入：

- **K1 抱纸**：`Front-on static wide shot of a cosy small living room: cream vertical-striped wallpaper, a warm pendant lamp, a small wall shelf with a potted plant, an olive-green armchair behind. Exactly 1 character: Endy, a fluffy lime-green plush turtle with an olive shell and a light-blue scarf, no hat, standing in the centre, proudly hugging a tall stack of blank white papers taller than his head, chin up, eyes closed, content smile. Warm soft light, shallow depth of field, plush 3D style. Empty space above his head. No text, no logos, no phone.`
- **K2 睡在壳里**：同一个场景；`Endy has pulled his head and limbs into his shell and lies on the floor fast asleep, sleepy smiling face just visible at the shell opening; blank papers scattered across the floor around him. Exactly 1 character.`
- **K3 盖好毯子**：同一个场景；`Endy asleep in his shell on the floor, now covered by a small warm plaid blanket; Shelly, a fluffy purple plush turtle with a deep-purple shell, eyelashes and blush, the same size as Endy, crouches beside him looking at him fondly. Exactly 2 characters, one green, one purple. Papers scattered.`

**视频**（Seedance 2.0 Mini，720p，每段 5 秒，约 5 积分）：

| 段 | 起始帧 → 结束帧 | 动作提示词 | 用在 |
| --- | --- | --- | --- |
| S1 | K1 → K1 | Endy holds still, gentle breathing; near the end he opens one eye and glances to the side. Camera locked. | 0–3.7 秒 |
| S2 | K1 → K2 | The paper stack bursts upward; Endy flops backwards, pulls his head and limbs into his shell and falls asleep on the floor; papers flutter down. Camera locked. | 3.7–6.4 秒（动作太慢就加速到 1.3 倍左右） |
| S3 | K2 → K3 | Shelly walks in from the right holding a small plaid blanket and gently drapes it over Endy's shell, then crouches beside him. Camera locked. | 6.4–10 秒，最后一帧定格 |

- S2、S3 各出两条备选。所有提示词都写「Camera locked, no cuts」，以及当时画面里角色的确切数量。
- **成本**：关键帧约 3–5 积分，视频约 25 积分（S1 一条，S2、S3 各两条），合计**约 30 积分**。本周会花到约 347（上限 250），要老板点头。

## 剪辑和发布

- `assemble.py`：三段接成一条，把原曲放在下面，按上面的逐词时间出 karaoke 字幕。
- **原声**：IG 和 FB 发布时先在音乐库里搜「I Took A Nap gunnarolla」，用平台的原声（这样能吃到这首歌的推流）。搜不到的话，就和 Keep going 一样把声音直接放进视频，文案注明 `original audio: "I Took A Nap" – gunnarolla`。
- **发布**：IG（ray162106）和 FB Endy & Shelly 主页。AI 标签打开。TikTok 暂时没有能正常推流的号，不发。
- **文案草稿**：`had a whole list today. anyway 😴 tell me I'm not the only one` + `#naptime #takeanap #relatable #tired`，再加原声注明那一行。
- **封面**：Endy 抱着那摞纸（K1）。
