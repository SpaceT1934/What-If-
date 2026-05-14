import type { Card } from '../types/card'

export const mockCards: Card[] = [
  {
    id: 'main-city-choice',
    title: '从北上广到小城生活的重新选择',
    time_range: '2026-02-08 ~ 2026-04-26',
    tags: ['城市选择', '大城市小城市', '人生节奏', '生活重估'],
    nodes: [
      {
        id: 'city-choice-1',
        title: '第一次认真搜索“要不要回小城市”',
        description: '连续加班几周后，他在凌晨搜索“毕业后去大城市还是回小城市”。过去他一直觉得留在大城市才算上进，但房租、通勤、孤独和长期紧绷的生活，让他开始怀疑自己是不是只是在惯性里坚持。',
        emotion: '疲惫、摇摆',
        reading_links: ['https://www.zhihu.com/en/answer/224037289'],
      },
      {
        id: 'city-choice-2',
        title: '被两种生活同时吸引',
        description: '大城市意味着机会、资源和不甘心；小城市意味着家人、稳定和可呼吸的生活。他发现真正难选的不是城市，而是自己想成为什么样的人：是继续追逐更高的平台，还是先把生活还给自己。',
        emotion: '比较、拉扯',
        reading_links: ['https://www.zhihu.com/en/answer/1920835235'],
      },
      {
        id: 'city-choice-3',
        title: '回家一周后的现实校准',
        description: '清明假期回家时，他久违地晚上七点就吃完饭，陪父母散步，睡了几个完整的觉。但几天后，他也感受到小城的信息密度、职业机会和社交边界。小城不是避风港，大城市也不是唯一答案。',
        emotion: '松弛、清醒',
      },
      {
        id: 'city-choice-4',
        title: '选择变成阶段性安排',
        description: '最后他没有立刻离开大城市，而是给自己设定一年观察期：减少无意义加班，储蓄更多现金，探索远程机会，同时认真评估回小城的行业路径。人生不是非此即彼，而是可以为自己争取缓冲区。',
        emotion: '释然、规划',
      },
    ],
    summary: '这段星尘记录的是一次关于城市与人生节奏的重新判断。知乎内容让他意识到，城市选择不是面子问题，而是机会、关系、身体状态和长期生活质量之间的权衡。',
    liu_kanshan_state: '我不是逃离大城市，我只是开始认真选择自己的生活半径。',
    liu_kanshan_image: '/images/liukanshan/city-choice.png',
  },
  {
    id: 'main-career-burnout',
    title: '职业倦怠后，我重新找回工作的边界',
    time_range: '2026-01-18 ~ 2026-04-06',
    tags: ['职业倦怠', '工作边界', '情绪修复', '职场成长'],
    nodes: [
      {
        id: 'career-burnout-1',
        title: '早上醒来就开始害怕上班',
        description: '她发现自己不是单纯不想工作，而是听到消息提示音就心跳加速。每天都在处理需求、改方案、对齐目标，却越来越感受不到价值。于是她开始在知乎搜索“职业倦怠到底是什么”。',
        emotion: '疲惫、麻木',
        reading_links: [
          'https://www.zhihu.com/en/answer/3428960630',
          'https://www.zhihu.com/en/answer/3299714302',
        ],
      },
      {
        id: 'career-burnout-2',
        title: '发现问题不只是“太累”',
        description: '她原本以为自己只是休息不够，但越看越发现，真正消耗她的是失控感：需求总变、评价标准模糊、没有成长反馈。她第一次把“我不行”改成“这个工作状态需要被调整”。',
        emotion: '识别、清醒',
        reading_links: ['https://www.zhihu.com/en/answer/3244533450'],
      },
      {
        id: 'career-burnout-3',
        title: '开始给工作重新划边界',
        description: '她开始做三件事：下班后不再秒回非紧急消息；把模糊任务拆成可确认的交付物；每周给自己留一个不被工作占用的晚上。刚开始很不习惯，但她慢慢发现，边界不是懒惰，而是为了持续工作。',
        emotion: '试探、恢复',
      },
      {
        id: 'career-burnout-4',
        title: '从“逃离工作”到“重建掌控感”',
        description: '两个月后，她没有立刻辞职，但不再每天被工作情绪牵着走。她重新学习沟通、拒绝和反馈，也开始思考下一阶段想积累的能力。工作仍然有压力，但她不再把全部自我价值压在工作表现上。',
        emotion: '稳定、复原',
      },
    ],
    summary: '这段星尘从职业倦怠开始，经过识别问题、调整边界和重建掌控感，呈现了一个职场人从情绪耗竭中慢慢恢复的过程。知乎内容没有直接替她解决工作，但让她学会把痛苦具体化。',
    liu_kanshan_state: '我不是不想努力了，我只是终于学会保护自己的能量。',
    liu_kanshan_image: '/images/liukanshan/confusion.png',
  },
  {
    id: 'main-english-learning',
    title: '从零基础英语，到第一次听懂原声片段',
    time_range: '2026-02-01 ~ 2026-05-12',
    tags: ['英语自学', '学习方法', '长期主义', '技能成长'],
    nodes: [
      {
        id: 'english-learning-1',
        title: '被一次面试英文问题卡住',
        description: '一次面试中，面试官让他简单用英文介绍项目。他脑子里有很多内容，却一句完整的话都说不出来。回家后，他开始搜索“英语零基础怎么自学”，第一次认真承认：英语不是证书问题，而是自己职业上的短板。',
        emotion: '受挫、不甘',
        reading_links: [
          'https://www.zhihu.com/question/36449108/answer/1915082312',
          'https://www.zhihu.com/en/answer/1485420102',
        ],
      },
      {
        id: 'english-learning-2',
        title: '从背单词焦虑，到建立学习路径',
        description: '一开始他下载了很多背词软件，每天背几十个单词，但很快忘掉。后来他在知乎看到音标、基础语法、听读输入的重要性，开始把目标从“快速变厉害”改成“每天能听、能读、能说一点”。',
        emotion: '混乱、整理',
        reading_links: ['https://www.zhihu.com/question/368505894'],
      },
      {
        id: 'english-learning-3',
        title: '第一次听懂一句原声台词',
        description: '他开始每天听 15 分钟英文材料，看一句、跟读一句、复述一句。某天看原声片段时，他没有看字幕就听懂了一句很简单的话。那一刻很小，却让他第一次相信自己真的在进步。',
        emotion: '惊喜、坚持',
      },
      {
        id: 'english-learning-4',
        title: '英语从任务变成生活的一部分',
        description: '三个月后，他还不能流利表达复杂观点，但已经能读懂简单英文文章，也敢在会议里说几句英文。英语不再是压在他身上的考试阴影，而变成一个可以慢慢累积的工具。',
        emotion: '稳定、自信',
      },
    ],
    summary: '这段星尘记录了一个成年人从英语受挫到建立学习节奏的过程。知乎内容帮助他从盲目背词转向系统输入，也让他意识到，学习技能最重要的不是突然爆发，而是每天可持续地前进一点。',
    liu_kanshan_state: '我终于不再害怕从零开始，因为零也是一条路的起点。',
    liu_kanshan_image: '/images/liukanshan/english-learning.png',
  },
  {
    id: 'main-reading-habit',
    title: '从刷短视频到重新养成阅读习惯',
    time_range: '2026-03-02 ~ 2026-05-15',
    tags: ['阅读习惯', '注意力修复', '自我提升', '生活方式'],
    nodes: [
      {
        id: 'reading-habit-1',
        title: '发现自己已经很久读不完一本书',
        description: '她在睡前刷短视频，一刷就是两个小时。某天突然发现，自己已经半年没有完整读完一本书。她开始搜索“如何养成阅读习惯”，想知道自己是不是已经失去了深度阅读的能力。',
        emotion: '空虚、警醒',
        reading_links: [
          'https://www.zhihu.com/en/answer/3255832924',
          'https://www.zhihu.com/en/answer/2423285361',
        ],
      },
      {
        id: 'reading-habit-2',
        title: '从每天读一小时，降到每天五分钟',
        description: '一开始她想每天读一小时，结果三天后就放弃。后来看到“从很小的目标开始”的建议，她把任务改成每天睡前读五分钟。五分钟短到没有压力，却足够让她重新坐到书桌前。',
        emotion: '调整、试探',
        reading_links: [
          'https://www.zhihu.com/en/answer/2049499477',
          'https://www.zhihu.com/en/answer/2364267423',
        ],
      },
      {
        id: 'reading-habit-3',
        title: '第一本书读完后的微小成就感',
        description: '她读完的第一本书并不深奥，只是一本散文集。但合上书的那一刻，她有一种久违的完整感：不是被算法推着看完无数碎片，而是自己主动走完了一段内容。',
        emotion: '安定、回归',
      },
      {
        id: 'reading-habit-4',
        title: '阅读变成情绪整理方式',
        description: '后来她不再追求一年读多少本，而是把阅读当成每天和自己相处的时间。焦虑的时候读几页，睡不着的时候读几页，慢慢把注意力从外界拉回自己身上。',
        emotion: '平静、沉淀',
      },
    ],
    summary: '这段星尘不是关于“高效读书”，而是关于注意力和生活节奏的修复。知乎内容让她明白，习惯不需要从宏大目标开始，真正重要的是让一件好事变得容易发生。',
    liu_kanshan_state: '我不是突然变得自律，只是重新找回了和自己安静相处的能力。',
    liu_kanshan_image: '/images/liukanshan/reading-habit.png',
  },
  {
    id: 'main-cat-life',
    title: '独居养猫后，我学会了照顾另一个生命',
    time_range: '2026-01-25 ~ 2026-04-18',
    tags: ['独居生活', '养猫', '情感陪伴', '责任感'],
    nodes: [
      {
        id: 'cat-life-1',
        title: '独居夜晚里的突然心软',
        description: '搬到新城市后，她每天回家面对空荡荡的房间。某天深夜，她搜索“孤独的时候养宠物有用吗”。她不是单纯想要一个可爱的玩伴，而是想知道，家里是否可以有一个生命等她回来。',
        emotion: '孤独、渴望',
        reading_links: [
          'https://www.zhihu.com/en/answer/937914590',
          'https://www.zhihu.com/en/answer/1765124957',
        ],
      },
      {
        id: 'cat-life-2',
        title: '从“想被陪伴”到“我要负责”',
        description: '她看了很多回答后意识到，宠物不是情绪止痛药。猫会生病，会孤独，会需要长期陪伴和稳定照顾。她开始查猫砂、驱虫、疫苗、独自在家注意事项，第一次把“我想要”变成“我能不能承担”。',
        emotion: '克制、认真',
        reading_links: [
          'https://www.zhihu.com/en/answer/2221199608',
          'https://www.zhihu.com/question/1996623067674275967/answer/1996966159862490254',
        ],
      },
      {
        id: 'cat-life-3',
        title: '第一次因为猫改变作息',
        description: '猫到家的第一个月，她的生活被重新安排：下班先喂食，周末清理猫砂，出差前找朋友上门照看。她也会烦，也会累，但每次开门听到猫跑过来的声音，又觉得这个家终于不只是一个睡觉的地方。',
        emotion: '磨合、责任',
      },
      {
        id: 'cat-life-4',
        title: '陪伴不再只是被治愈',
        description: '后来她发现，养猫并不是单方面被治愈。更多时候，是她在学习稳定、耐心和承担。她不再把孤独全部交给猫解决，而是在照顾它的过程中，也把自己的生活照顾得更像样。',
        emotion: '温柔、成长',
      },
    ],
    summary: '这段星尘从独居孤独开始，经过养宠前的信息搜索、责任评估和真实磨合，逐渐转向情感陪伴与生活秩序的建立。知乎内容提醒她，宠物不是用来填补空洞的物品，而是需要认真对待的生命。',
    liu_kanshan_state: '我原来只是想被陪伴，后来学会了怎样去陪伴。',
    liu_kanshan_image: '/images/liukanshan/cat-life.png',
  },
]

export default mockCards
