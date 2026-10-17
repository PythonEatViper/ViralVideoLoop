# Endy · I Took A Nap（翻拍 @sadgoose42）

- **参考**：@sadgoose42「I Took A Nap」https://www.tiktok.com/@sadgoose42/video/7693257487427865889 · 10-05 发 · 9 秒 · 140 万播放 / 18.3 万赞 / 6.4 万分享（4.6%）/ 2.2 万收藏。和 Keep going 是同一个作者。拆解在 `references/sadgoose42_7693257487427865889/`（notes.md、contact_sheet.jpg、ref.mp4；每 0.5 秒一帧的单张图在 `frames/f00–f17.jpg`）。
- **为什么做**：老板 10-17 点名。原片很短（9 秒），一个固定镜头，歌词就是字幕，一个爆点，结尾治愈，分享率很高，正好是 IG 推 Keep going 的那种东西。
- **测试的假设**：把 140 万播放的热门原声短片换成 Endy，IG 分享和收藏能达到 Keep going 的一半（分享 ≥0.8%、收藏 ≥0.7%）。
- **预测分 66（hold）**，目前最高（打气 2 号 56）。预估：3 秒留存 0.78 · 平均观看 0.85 · 完播 0.45 · 分享 0.01 · 收藏 0.007 · 点赞 0.05 · 评论 0.001 · 关注 0.002。依据是 Keep going 在 IG 24 小时的实测，分享和收藏打对折；时长只有 10 秒，所以完播估得比以往高很多。

## 原片为什么火（逐帧量出来的，10-17）

1. **第一帧就读得懂**：画面中间只有一个角色，抱着一摞比自己还高的纸，一脸自豪，后面是一张空沙发。还没开口，观众已经知道「这家伙今天很忙」。0.22 秒开唱，0.3 秒第一个词亮起，没有任何铺垫。
2. **一直跟着节拍弹**（老板说的「扭动」）：前 4.4 秒，鹅整个身子跟着歌**每 0.6 秒上下弹一次**（约 100 BPM），一边弹一边对口型唱。位置几乎不动（喙的左右位置只差 1%），只是有节奏地一伸一缩。画面不是死的，但也没有新信息，观众只盯着字和节奏。
3. **歌词就是字幕，逐词亮起**：后面的词先浅灰预显，唱到才变白。眼睛跟着读，脑子在猜下一个词，所以留得住人。实际歌词是 "but you know what I did **instead**? I took a nap."
4. **一个爆点，然后几乎全静止**：4.7–5.0 秒，纸炸飞（只用了 0.3 秒）；5.0–7.2 秒，瘫坐在地上一动不动（每帧几乎没变化）；7.3 秒一帧硬切成「软面条挂在沙发上」；7.9 秒再硬切成「盖毯子睡着」，一直定格到结尾。**一共只有 4 个姿势，靠硬切换，不是连续动画**。笑点就在这种「啪」的一下。
5. **结尾能循环**：最后 1 秒定格在舒服的画面，重播时接回自豪抱纸，反差再来一次。
6. **情绪是「允许自己偷懒」**：不说教，看完想转给朋友说「这就是我」，所以分享率有 4.6%。文案 "Tell me, I'm not the only one🙏" 引大家来评论认同。
7. **热门原声**：这首歌本身在推，挂同一个声音能进它的推流池。

我们复制得了的是 1–6；7 要靠发布时在 IG 用平台原声。原作者的粉丝基础我们没有，所以「同样 140 万」不能保证，及格线按我们自己的 Keep going 定。

## 固定不变的（freeze list）

| 项目 | 定死为 |
| --- | --- |
| 角色 | **只有 Endy 一个**（老板 10-17）：绿色毛绒海龟，不戴帽子，浅蓝小围巾，一个橄榄色壳，参考 `characters/shelly.png`，job `332f4e7f-…`。 |
| 画风 | 和 Keep going 一样：毛绒 3D、暖色柔光（`goose_keep_going/keyframes/K1_bike.png`） |
| 场景 | 温暖的小客厅，按我们的画风重画，不照搬原片：米黄色竖条纹墙纸、一盏暖黄吊灯、墙上一块小搁板放一盆小绿植、橄榄绿单人沙发在后面（扶手上搭一条红绿格子小毯子）、暖红棕色地板。所有画面用同一个场景、同一个构图。 |
| 机位 | 正面平视全景，**全程不动**，没有剪切。Endy 站在画面中间偏下，头顶上方留出放字的空间。 |
| 声音 | 原曲「I Took A Nap」— gunnarolla。不加别的音乐和音效。 |
| 字幕 | 歌词逐词亮起，后面的词浅灰预显（assemble 的 karaoke「lit」样式），白字，画面上方居中，一次一行。 |
| 动作 | 学原片：**几个姿势之间硬切换**，不做连续动画。只有两处会动：开头跟着节拍弹，纸炸开那 0.3 秒。 |
| 时长 | 约 10 秒：9 秒的歌，加最后 1 秒定格，方便循环。 |
| 不出现 | 手机、logo、任何文字（纸是空白的）。 |

## 分镜（时间按原曲逐词对齐）

| 秒 | 歌词（逐词亮起） | 画面 | 观众此刻注意的一件事 |
| --- | --- | --- | --- |
| 0.0–4.6 | I had a lot of things to do today, / but you know what I did instead? | **P1** Endy 站在正中，双手抱着一摞比他头还高的白纸，下巴抬起，闭着眼，很自豪。**整个身子每 0.6 秒跟着节拍上下弹一次**，嘴跟着唱一开一合。 | 读字、跟节奏 |
| 4.6–5.0 | I | **P2** 纸往上炸开，Endy 往后一倒（0.3–0.4 秒） | 看纸炸开 |
| 5.0–7.3 | took a nap. | **P3** 头和四肢缩进壳里，壳在地上，纸散一地，一张纸搭在壳上。完全不动，只有很轻的呼吸。 | 看他缩进壳里 |
| 7.3–7.9 | It was a very | **P4** 硬切：Endy 软趴趴地挂在沙发扶手上，四肢耷拉着（原片里「软面条」那一帧） | 看他怎么到了沙发上 |
| 7.9–10.0 | good nap | **P5** 硬切：Endy 躺在沙发上，盖着红绿格子小毯子，头枕着小黄靠枕，睡得很香，纸还散在地上。定格到结尾。 | 一个安静的画面，接回开头循环 |

- **和原片的不同**：只改一处：原片里鹅瘫坐在地上、书盖在头上，我们换成**缩进壳里睡觉**，只有海龟能做。其余的节奏、构图、姿势、字幕都照原片。
- **注意力**：每一刻只发生一件事：读字 → 纸炸开 → 缩进壳 → 挂在沙发上 → 睡着。全程只有 Endy 一个。

## 怎么做（批准前不花任何积分）

**4 张关键帧 + 1 段短视频**，其余靠剪辑做出来：

| 画面 | 做法 | 积分 |
| --- | --- | --- |
| P1 抱纸 | GPT Image 2.5 出一张（提示词见下）。**跟拍弹跳不让 AI 生成**：AI 视频对不上节拍。剪辑时用代码让这张图每 0.6 秒做一次轻微的压扁再弹起（高度缩约 2%，脚底固定），正好落在节拍上。嘴的一开一合用两张图交替：P1a 闭嘴、P1b 张嘴（同一张图局部重绘）。**只弹 Endy，不弹背景**：另出一张没有角色的空客厅底图，把 Endy 抠出来（remove_background）叠在上面弹。已用占位图试过，弹跳能卡在 0.6 秒的节拍上；整张图一起弹会把背景也压扁，所以要分层。 | 约 3–4 |
| P2 纸炸开 | Seedance 2.0 Mini 一段 5 秒视频，起始帧 P1，只取纸炸开的 0.3–0.4 秒 | 约 5 |
| P3 壳里睡着 | GPT Image 2.5，同一场景 | 约 1 |
| P4 挂在沙发上 | GPT Image 2.5，同一场景 | 约 1 |
| P5 盖毯子睡着 | GPT Image 2.5，同一场景 | 约 1 |

- 合计**约 12 积分**（留几次重出的余量），比原来逐段生成视频的方案（约 30）少很多，也更像原片。本周会花到约 329（上限 250），还是要老板点头。
- 静止的画面（P3、P5）加一点很轻的呼吸（同样用代码，幅度约 1%），不让画面完全死掉。

**关键帧提示词**（Endy 的参考图作为 `image_references` 传入；每张都写 `Exactly 1 character (Endy), nobody else. Front-on static wide shot, same room and framing as the reference keyframe. No text, no logos, no phone.`）

- 场景（每张共用）：`A cosy small living room in plush 3D style: cream vertical-striped wallpaper, a warm pendant lamp, a small wall shelf with a potted plant, an olive-green armchair with a red-and-green plaid blanket on its arm, warm red-brown floor. Warm soft light. Empty space at the top of the frame.`
- **P1a**：`Endy, a fluffy lime-green plush turtle with an olive shell and a light-blue scarf, no hat, stands in the centre in front of the armchair, proudly hugging a tall stack of blank white papers taller than his head, chin up, eyes closed, mouth closed, content smile.`
- **P1b**：P1a 局部重绘，只把嘴改成张开唱歌的样子。
- **P3**：`Endy has pulled his head and limbs into his shell and lies on the floor fast asleep, sleepy smiling face just visible at the shell opening; blank papers scattered across the floor, one resting on his shell.`
- **P4**：`Endy hangs limply over the arm of the armchair like a floppy plush toy, arms and legs dangling, eyes closed; papers scattered on the floor.`
- **P5**：`Endy lies asleep on the armchair, head on a small yellow cushion, tucked under the red-and-green plaid blanket, peaceful smile; papers still scattered on the floor.`
- **P2 视频**：起始帧 P1a；`The paper stack bursts upward and papers fly into the air; Endy tips backwards. Camera locked, no cuts.`

## 剪辑和发布

- `assemble.py` 按上面的时间把五个画面接起来，加跟拍弹跳、呼吸和逐词亮起的字幕，原曲放在下面。剪辑里每次切换都卡在歌词的那个字上。
- **原声**：IG 和 FB 发布时先在音乐库里搜「I Took A Nap gunnarolla」，用平台的原声（这样能吃到这首歌的推流）。搜不到的话，就和 Keep going 一样把声音直接放进视频，文案注明 `original audio: "I Took A Nap" – gunnarolla`。
- **发布**：IG（ray162106）和 FB Endy & Shelly 主页。AI 标签打开。TikTok 暂时没有能正常推流的号，不发。
- **文案**：第一行就点题，再邀请大家认同：`had a whole list today. anyway 😴` / `tell me I'm not the only one 🙏` + `#naptime #takeanap #relatable #tired`，再加原声注明那一行。
- **封面**：P1，Endy 抱着那摞纸。
