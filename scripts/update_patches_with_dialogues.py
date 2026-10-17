# -*- coding: utf-8 -*-
"""
update_patches_with_dialogues.py
Adds cutscene dialogue and in-game profile refinements to translation_patches.json.
"""
import json

def main():
    patches_file = "workspace/translation/translation_patches.json"
    with open(patches_file, "r", encoding="utf-8") as f:
        existing_patches = json.load(f)

    existing_by_key = {(p.get("source", "LOCALDAT"), p["ko_id"]): p for p in existing_patches}
    print(f"Existing patches count: {len(existing_patches)}")

    # Define new dialogue & profile patches
    new_patches = [
        # --- Cutscene Dialogues (6501..6942) ---
        {
            "source": "LOCALDAT",
            "ko_id": 6501,
            "category": "Tier 4 - Dialogue Phrasing",
            "reason": "Polite greeting from HQ operator to Clank",
            "old_ko": '안녕, <COL:02>클랭크<COL:01> 요원. "무한의 눈"은 지켰나요?',
            "new_ko": '<COL:02>클랭크<COL:01> 요원, "무한의 눈"은 무사히 지켰나요?'
        },
        {
            "source": "LOCALDAT",
            "ko_id": 6502,
            "category": "Tier 4 - Dialogue Phrasing",
            "reason": "Accurate Clank response to HQ inquiry",
            "old_ko": "아니요. 그런데 아주 이상한 장면을 목격했어요!",
            "new_ko": "아니요, 지키기는커녕 생각지도 못한 방해자가 나타났어요<ELLIPSIS>"
        },
        {
            "source": "LOCALDAT",
            "ko_id": 6503,
            "category": "Tier 4 - Dialogue Phrasing",
            "reason": "Natural phrasing for incoming news report",
            "old_ko": "잠깐만요. 당신이 있는 장소에서 발신되는 뉴스가 있는데 전송해 줄게요.",
            "new_ko": "죄송해요, 방금 들어온 속보가 있어서 화면으로 전송할게요."
        },
        {
            "source": "LOCALDAT",
            "ko_id": 6506,
            "category": "Tier 4 - Dialogue Phrasing",
            "reason": "Accurate news anchor phrase (caught red-handed / arrested)",
            "old_ko": "놀랍게도, 범죄 현장에는 은하계의 영웅인 <COL:02>라쳇<COL:01>이 있었습니다.",
            "new_ko": "놀랍게도 유명 영웅 <COL:02>라쳇<COL:01>이 현행범으로 체포되었습니다."
        },
        {
            "source": "LOCALDAT",
            "ko_id": 6507,
            "category": "Tier 4 - Dialogue Phrasing",
            "reason": "Fixes mistranslated idiom and matches Ratchet's voice",
            "old_ko": "이건 옳지않아! 이건 분명히 알아두라구. 영웅을 위한 댓가는 정말 아무 것도 없다는 걸!",
            "new_ko": "난 잘못 없어! <ELLIPSIS>다들 도둑질은 남는 장사가 아니라고 하지만, 영웅 짓보단 훨씬 낫다고!"
        },
        {
            "source": "LOCALDAT",
            "ko_id": 6508,
            "category": "Tier 4 - Dialogue Phrasing",
            "reason": "Matches JA comedic contrast: saving galaxy vs living in poverty",
            "old_ko": "난 아직도 다 낡아빠진 조그마한 단칸 방에 살고 있다고...",
            "new_ko": "은하계를 아무리 구해봤자 찢어지게 가난하다고! 지금도 여전히 코딱지만 한 단칸방 신세란 말이야!"
        },
        {
            "source": "LOCALDAT",
            "ko_id": 6509,
            "category": "Tier 4 - Dialogue Phrasing",
            "reason": "Ratchet bragging about stashing the gem and breaking out",
            "old_ko": "하지만 이제 곧 달라질거야! 보석은 아무도 찾지 못하는 곳에 있지. 지금은 잡혀있지만, 날 가둬둘 수 있는 감옥 따위는 아무데도 없어.",
            "new_ko": '하지만 그것도 이제 끝이야<ELLIPSIS> "무한의 눈"은 나 말고는 아무도 못 찾아! 두고 보라고, 어떤 감옥이든 금방 탈출해 줄 테니까!'
        },
        {
            "source": "LOCALDAT",
            "ko_id": 6510,
            "category": "Tier 4 - Dialogue Phrasing",
            "reason": "Fixes broken Korean grammar ('존재가 대단한 안타까운 소식')",
            "old_ko": "은하계 최고 영웅이었던 존재가 타락한 안타까운 소식입니다.",
            "new_ko": "유명 영웅의 체포 소식에 온 은하계가 충격과 혼란에 휩싸여 있습니다."
        },
        {
            "source": "LOCALDAT",
            "ko_id": 6512,
            "category": "Tier 4 - Dialogue Phrasing",
            "reason": "HQ operator sympathetic phrasing",
            "old_ko": "유감이에요. 당신과 <COL:02>라쳇<COL:01>은<ELLIPSIS>",
            "new_ko": "정말 큰일이네요<ELLIPSIS> 그 사람, 당신의 가장 친한 친구잖아요?"
        },
        {
            "source": "LOCALDAT",
            "ko_id": 6513,
            "category": "Tier 4 - Dialogue Phrasing",
            "reason": "Clank polite tone and biometric recognition check",
            "old_ko": "저 자가 내 친구일 리가 없어. 뉴스 영상에 망막 검사를 해봐요.",
            "new_ko": "라쳇이 저런 악당일 리 없어요! 영상으로 생체 인식을 해봐요!"
        },
        {
            "source": "LOCALDAT",
            "ko_id": 6514,
            "category": "Tier 4 - Dialogue Phrasing",
            "reason": "Retina pattern match confirmation",
            "old_ko": "결과는 양성이에요<ELLIPSIS> <COL:02>라쳇<COL:01>이 맞아요.",
            "new_ko": "망막 패턴 일치<ELLIPSIS> 본인이 맞아요."
        },
        {
            "source": "LOCALDAT",
            "ko_id": 6515,
            "category": "Tier 4 - Dialogue Phrasing",
            "reason": "Operator suggestion to investigate museum",
            "old_ko": "<COL:02>클랭크<COL:01>, 시간이 없어요. 박물관으로 다시 가서, 보석의 행방을 찾으세요.",
            "new_ko": "이렇게 된 이상 박물관에 다시 잠입해서 단서를 찾아보는 건 어떨까요?"
        },
        {
            "source": "LOCALDAT",
            "ko_id": 6519,
            "category": "Tier 4 - Dialogue Phrasing",
            "reason": "Operator suspecting deeper hidden circumstances",
            "old_ko": "이 사건이 당신과 개인적으로 관련되어 유감이지만 이 사건은 보다 큰 범죄 계획의 일부에 불과해요.",
            "new_ko": "<COL:02>라쳇<COL:01>이 체포된 데에는 분명 뭔가 말 못 할 사정이 있을 거예요."
        },
        {
            "source": "LOCALDAT",
            "ko_id": 6520,
            "category": "Tier 4 - Dialogue Phrasing",
            "reason": "Calm encouragement to proceed",
            "old_ko": "당신이 꼭 남아서 이 임무를 완수해 주길 바래요.",
            "new_ko": "이럴 때일수록 침착하게 조사해 나가요."
        },
        {
            "source": "LOCALDAT",
            "ko_id": 6521,
            "category": "Tier 4 - Dialogue Phrasing",
            "reason": "Clank polite acknowledgment to operator",
            "old_ko": "알고 있어요. 발견하는 게 있으면 보고하죠.",
            "new_ko": "알겠습니다! 단서를 찾는 대로 연락할게요."
        },
        {
            "source": "LOCALDAT",
            "ko_id": 6522,
            "category": "Tier 4 - Dialogue Phrasing",
            "reason": "Operator polite honorific to Clank",
            "old_ko": "<COL:02>클랭크<COL:01>, 지켜보고 있을 거에요.",
            "new_ko": "<COL:02>클랭크<COL:01> 님, 지켜보고 있을게요."
        },
        {
            "source": "LOCALDAT",
            "ko_id": 6523,
            "category": "Tier 4 - Dialogue Phrasing",
            "reason": "Restores fortune cookie paper joke",
            "old_ko": "고대 격언: 네 일에나 신경써라.",
            "new_ko": "포춘 쿠키 쪽지로군요<ELLIPSIS> '로봇도 걷다 보면 너덜너덜'."
        },
        {
            "source": "LOCALDAT",
            "ko_id": 6524,
            "category": "Tier 4 - Dialogue Phrasing",
            "reason": "Fortune cookie slip with address details",
            "old_ko": "제조업체: 당신의 행운과자 공장, <COL:02>아시아니카<COL:01>",
            "new_ko": "포춘 쿠키 안쪽 쪽지예요. 주소도 적혀 있어요!"
        },
        {
            "source": "LOCALDAT",
            "ko_id": 6525,
            "category": "Tier 4 - Dialogue Phrasing",
            "reason": "Connecting clue to Asyanica planet",
            "old_ko": "보석이 있는 장소를 알아낸 것 같아요.",
            "new_ko": "'<COL:02>아시아니카<COL:01>'라는 장소가 수상하네요."
        },
        {
            "source": "LOCALDAT",
            "ko_id": 6534,
            "category": "Tier 4 - Dialogue Phrasing",
            "reason": "Warden calling Ratchet naive/greenhorn",
            "old_ko": "그래, 여기 온 사람들은 누구나 결백하다고 하지. 조금 충격이긴 하겠지만",
            "new_ko": "어이구, 완전 세상 물정 모르는 풋내기구만 그래. 여긴 그렇게 만만한 감옥이 아니라고!"
        },
        {
            "source": "LOCALDAT",
            "ko_id": 6539,
            "category": "Tier 4 - Dialogue Phrasing",
            "reason": "Warden admitting bribe in bolts",
            "old_ko": "보통은 그렇지만 너 같은 위대한 영웅한테는 보호가 필요없을 것 같군.",
            "new_ko": "원래는 그래야 하지만, 죄수들한테 뇌물로 볼트를 두둑하게 챙겨 받았거든."
        },
        {
            "source": "LOCALDAT",
            "ko_id": 6540,
            "category": "Tier 4 - Dialogue Phrasing",
            "reason": "Warden taunting Ratchet to survive inmate attacks",
            "old_ko": "게다가 널 편히 지내지 못하게 해달라는 부탁과 함께 돈을 좀 받았거든. 그럼 잘 쉬라고.",
            "new_ko": "영웅이라는 양반이 살려달라고 징징댈 건 아니겠지? 어디 한번 잘 버텨보라고."
        },
        {
            "source": "LOCALDAT",
            "ko_id": 6546,
            "category": "Tier 4 - Dialogue Phrasing",
            "reason": "Fixes inverted mistranslation: Number Woo laughs that Clank is vulnerable to electricity",
            "old_ko": "아, <COL:02>클랭크<COL:01> 요원. 자네한테 <COL:02>전기<COL:01>는 별 효과가 없는 모양이야. 하하하.",
            "new_ko": "하하하, <COL:02>클랭크<COL:01> 요원! 네놈은 전기에 아주 쥐약이로구나! 크하하하하!"
        },
        {
            "source": "LOCALDAT",
            "ko_id": 6547,
            "category": "Tier 4 - Dialogue Phrasing",
            "reason": "Number Woo death laser threat",
            "old_ko": "닌자들이 이 레이저를 <COL:02>충전<COL:01>시키고 나면 넌 영원히 파괴될 거다. 각오하시게나!!!",
            "new_ko": "살인 레이저 충전이 끝나면 넌 끝장이다<ELLIPSIS> 영원히 말이지! 각오하거라!"
        },
        {
            "source": "LOCALDAT",
            "ko_id": 6548,
            "category": "Tier 4 - Dialogue Phrasing",
            "reason": "Clank commanding Gadgebots and promising treats",
            "old_ko": "브라보, 헥터, 서펜타인. 행동 개시. 칠면조가 닭장에 갇혀 있다!",
            "new_ko": "브라보! 헥터! 서펜타! 돌격, 돌격! 임무 끝나면 간식 줄게요!"
        },
        {
            "source": "LOCALDAT",
            "ko_id": 6549,
            "category": "Tier 4 - Dialogue Phrasing",
            "reason": "Clank telling Gadgebots to stand by for next mission",
            "old_ko": "넘버 우한테 너희들 안부까지 확실히 전해줄게.",
            "new_ko": "다음 임무에서 부를 때까지 대기하세요!"
        },
        {
            "source": "LOCALDAT",
            "ko_id": 6557,
            "category": "Tier 4 - Dialogue Phrasing",
            "reason": "Fixes typo '할꺼' and matches Clank's polite agent refusal to release Number Woo",
            "old_ko": "그러면 당신이 날 죽이려 할꺼 같아 안 그러기로 했어요.",
            "new_ko": "풀어드리고는 싶지만, 절 바로 없애버리려 하실 것 같아서 안 되겠네요."
        },
        {
            "source": "LOCALDAT",
            "ko_id": 6570,
            "category": "Tier 4 - Dialogue Phrasing",
            "reason": "Barney questioning Quark's pseudo-science",
            "old_ko": "잠깐... 그건 말이 안되는데.",
            "new_ko": "그거, 이해하고 말씀하시는 거예요?"
        },
        {
            "source": "LOCALDAT",
            "ko_id": 6571,
            "category": "Tier 4 - Dialogue Phrasing",
            "reason": "Quark defensive reply",
            "old_ko": "네가 그때 거기에 있었냐?",
            "new_ko": "이해 못 했을 리가 없잖아!"
        },
        {
            "source": "LOCALDAT",
            "ko_id": 6572,
            "category": "Tier 4 - Dialogue Phrasing",
            "reason": "Barney taking notes on Quark's lack of knowledge",
            "old_ko": "아니..요<ELLIPSIS>",
            "new_ko": "이해<ELLIPSIS> 못 함, 메모."
        },
        {
            "source": "LOCALDAT",
            "ko_id": 6573,
            "category": "Tier 4 - Dialogue Phrasing",
            "reason": "Quark bluffing with vague nonsense words",
            "old_ko": "없었으면 말을 하지마. 난 장치를 만진 후에 플랫폼에 올라섰지.",
            "new_ko": "안다니까! 아무튼 그런 느낌으로 어쩌구저쩌구<ELLIPSIS> 뭐시기 효과로!"
        },
        {
            "source": "LOCALDAT",
            "ko_id": 6591,
            "category": "Tier 4 - Dialogue Phrasing",
            "reason": "Restores Clank's iconic deadpan flatter quip",
            "old_ko": "분명히 그런 소문을 들으셨겠죠?",
            "new_ko": "빈말 기능은 내장되어 있지 않습니다."
        },
        {
            "source": "LOCALDAT",
            "ko_id": 6595,
            "category": "Tier 3 - Typo",
            "reason": "Fixes spelling typo '꺽는다는' -> '꺾는다는'",
            "old_ko": "왕년에 관절 좀 꺽는다는 소릴 들었죠.",
            "new_ko": "왕년에 관절 좀 꺾는다는 소릴 들었죠."
        },
        {
            "source": "LOCALDAT",
            "ko_id": 6597,
            "category": "Tier 3 - Typo",
            "reason": "Fixes awkward trailing typo '감동시켰어용.' -> '감동시켰어요!'",
            "old_ko": "놀라워요. 그댄 다른 어떤 로봇들 보다도 날 감동시켰어용.",
            "new_ko": "놀라워요! 그댄 다른 어떤 로봇들보다도 날 감동시켰어요!"
        },
        {
            "source": "LOCALDAT",
            "ko_id": 6614,
            "category": "Tier 4 - Dialogue Phrasing",
            "reason": "Clank stalling guard with shoelace excuse",
            "old_ko": "잠깐만. 신발끈이 풀려서.",
            "new_ko": "잠깐만요. 신발끈이<ELLIPSIS> 풀려서<ELLIPSIS> 에잇!"
        },
        {
            "source": "LOCALDAT",
            "ko_id": 6642,
            "category": "Tier 4 - Dialogue Phrasing",
            "reason": "Guard encouraging short robot to hang in there",
            "old_ko": "잘 가라구.",
            "new_ko": "힘내서 살아라!"
        },
        {
            "source": "LOCALDAT",
            "ko_id": 6648,
            "category": "Tier 4 - Dialogue Phrasing",
            "reason": "Clank warm/casual communication to Ratchet",
            "old_ko": "<COL:02>라쳇<COL:01>. 난 널 감옥에서 빼내려고 해. 슬라임이 거기 있다는 걸 알았고 이게 너한테 메시지를 전할 수 있는 유일한 방법이지.",
            "new_ko": "<COL:02>라쳇<COL:01>! 어떻게든 널 구해내고 싶어! 슬라임이 연락을 중계해 줄 거야."
        },
        {
            "source": "LOCALDAT",
            "ko_id": 6656,
            "category": "Tier 4 - Dialogue Phrasing",
            "reason": "Spacing correction for drama parody line",
            "old_ko": "내안에 볼트 있다.",
            "new_ko": "내 안에 볼트 있다."
        },
        {
            "source": "LOCALDAT",
            "ko_id": 6658,
            "category": "Tier 4 - Dialogue Phrasing",
            "reason": "Removes archaic Joseon '하오체' and restores suave secret agent tone to dealer",
            "old_ko": "고맙소 레이디. 여기 게임 규칙은 뭐요?",
            "new_ko": "고마워요, 레이디. 이 게임은 어떻게 하는 건가요?"
        },
        {
            "source": "LOCALDAT",
            "ko_id": 6659,
            "category": "Tier 4 - Dialogue Phrasing",
            "reason": "Removes archaic Joseon '하오체' and restores suave secret agent tone",
            "old_ko": "음 내 취향과 좀 다르지만 한 번 해보도록 하겠소. 뭘 걸어야하오?",
            "new_ko": "제 취향엔 조금 시시해 보이지만, 어디 한번 해볼까요? 판돈은 어떻게 걸죠?"
        },
        {
            "source": "LOCALDAT",
            "ko_id": 6661,
            "category": "Tier 4 - Dialogue Phrasing",
            "reason": "Removes archaic Joseon '하오체' and restores suave agent bet declaration",
            "old_ko": "내 목장 행성의 권리증을 걸겠소. 대신 내가 이기면 저 상자 안에 든 걸 모두 가지겠소.",
            "new_ko": "제 목장 행성의 소유권을 걸겠습니다. 대신 이기면 저 상자 속 물건은 제 차지가 되는 겁니다."
        },
        {
            "source": "LOCALDAT",
            "ko_id": 6663,
            "category": "Tier 4 - Dialogue Phrasing",
            "reason": "Removes archaic Joseon '하오체' and restores suave agent tone",
            "old_ko": "이제 저 상자를 가지고 가야겠소.",
            "new_ko": "아무래도 상자 속 물건은 제 차지인 것 같군요."
        },
        {
            "source": "LOCALDAT",
            "ko_id": 6665,
            "category": "Tier 4 - Dialogue Phrasing",
            "reason": "Removes archaic Joseon '하오체' and restores agent dialogue to dealer ('Then you have swindled me, Madame!')",
            "old_ko": "그럼 날 물먹인 거란 말이오?",
            "new_ko": "그럼 절 속이신 건가요, 부인?"
        },
        {
            "source": "LOCALDAT",
            "ko_id": 6667,
            "category": "Tier 4 - Dialogue Phrasing",
            "reason": "Removes awkward translation of 'One cannot wager what one does not possess'",
            "old_ko": "가지고 있지 않은 것을 잃을 순 없지.",
            "new_ko": "가지고 있지도 않은 걸 걸어서는 안 되죠."
        },
        {
            "source": "LOCALDAT",
            "ko_id": 6670,
            "category": "Tier 4 - Dialogue Phrasing",
            "reason": "Removes archaic Joseon '하오체' and restores James Bond suave parting line",
            "old_ko": "그건 다음으로 미룹시다. 여기서의 게임은 이미 끝난 것 같소.",
            "new_ko": "그건 다음에 하죠. 매력적인 신사는 늘 바쁜 법이거든요."
        },
        {
            "source": "LOCALDAT",
            "ko_id": 6686,
            "category": "Tier 4 - Dialogue Phrasing",
            "reason": "Clank polite agent rescue intro",
            "old_ko": "전 <COL:02>클랭크<COL:01> 요원이죠. 박사님을 킹핀으로부터 구출하는 거에요.",
            "new_ko": "<COL:02>클랭크<COL:01> 요원입니다! 당신을 구하러 왔어요."
        },
        {
            "source": "LOCALDAT",
            "ko_id": 6691,
            "category": "Tier 4 - Dialogue Phrasing",
            "reason": "Clank polite tone regarding the mint/vault",
            "old_ko": "볼트 공장! 항상 돈이 문제군.",
            "new_ko": "조폐국 말씀인가요! 역시 돈 문제였군요."
        },
        {
            "source": "LOCALDAT",
            "ko_id": 6715,
            "category": "Tier 4 - Dialogue Phrasing",
            "reason": "Clank realizing he was framed by fabricated footage",
            "old_ko": "이건 말도 안돼. 내가 뭘 하고 있는 거지?",
            "new_ko": "이건 가짜 영상이에요! 함정에 빠진 거라고요!"
        },
        {
            "source": "LOCALDAT",
            "ko_id": 6717,
            "category": "Tier 4 - Dialogue Phrasing",
            "reason": "Restores Clank's polite gratitude to Gadgebots ('Thank you, gentlemen. I am in your debt.')",
            "old_ko": "고맙다. 너희들한테 신세를 졌구나.",
            "new_ko": "고마워요, 신사 여러분. 큰 신세를 졌네요!"
        },
        {
            "source": "LOCALDAT",
            "ko_id": 6718,
            "category": "Tier 4 - Dialogue Phrasing",
            "reason": "Natural phrasing for bank heist framing",
            "old_ko": "함정이었어요. 그들이 내가 금고를 터는 것처럼 보이게 만들었어요.",
            "new_ko": "함정이었어요! 금고 털이 누명을 쓰게 생겼어요!"
        },
        {
            "source": "LOCALDAT",
            "ko_id": 6737,
            "category": "Tier 4 - Dialogue Phrasing",
            "reason": "Fixes inverted mistranslation: Klunk praises Clank for seeing through Kingpin costume",
            "old_ko": "잘됐군. 네가 차이점을 구분하지 못한다면 누구도 눈치채지 못하겠지.",
            "new_ko": "훌륭하군! 과연 너라면 꿰뚫어 볼 줄 알았다 게스!"
        },
        {
            "source": "LOCALDAT",
            "ko_id": 6738,
            "category": "Tier 4 - Dialogue Phrasing",
            "reason": "Clank polite tone to Klunk",
            "old_ko": "클렁크! 대체 여기서 뭐하는 거야?",
            "new_ko": "클렁크! 왜 여기에 있는 거죠?"
        },
        {
            "source": "LOCALDAT",
            "ko_id": 6747,
            "category": "Tier 3 - Typo",
            "reason": "Fixes typo '물었봤던' -> '물어봤던'",
            "old_ko": "그게 바로 우주 수녀들이 내게 물었봤던 질문이지.",
            "new_ko": "그게 바로 우주 수녀들이 내게 물어봤던 질문이지."
        },
        {
            "source": "LOCALDAT",
            "ko_id": 6757,
            "category": "Tier 4 - Dialogue Phrasing",
            "reason": "Clank polite tone when tracking his ship",
            "old_ko": "다행히도 이건 아직 작동되는군. 내 우주선의 신호를 잡을 수 있다면 클렁크를 찾을 수 있을 거야.",
            "new_ko": "아직 움직여주면 좋겠는데<ELLIPSIS> 제 우주선을 추적하면 클렁크가 있는 곳도 알 수 있어요."
        },
        {
            "source": "LOCALDAT",
            "ko_id": 6759,
            "category": "Tier 4 - Dialogue Phrasing",
            "reason": "Clarifying that Klunk stole the ship and abandoned it",
            "old_ko": "배후에 누가 있는지 마침내 알아냈어요. 그건 클렁크였어요! 그가 내 우주선을 훔쳐서 여기로 왔어요.",
            "new_ko": "마침내 진짜 흑막을 알아냈어요! 바로 '클렁크'예요! 제 우주선을 훔쳐서 여기 버려두고 갔어요."
        },
        {
            "source": "LOCALDAT",
            "ko_id": 6773,
            "category": "Tier 4 - Dialogue Phrasing",
            "reason": "Warden barking angrily at Ratchet",
            "old_ko": "무슨 짓을 한 거지?",
            "new_ko": "건방 떨지 마라!"
        },
        {
            "source": "LOCALDAT",
            "ko_id": 6811,
            "category": "Tier 4 - Dialogue Phrasing",
            "reason": "Klunk distinctive villain dialect and taunt",
            "old_ko": "이젠 나이가 들어서 굼벵이처럼 느리시구만.",
            "new_ko": "이렇게나 느려터지다니 나이를 헛먹었나 보군 게스?"
        },
        {
            "source": "LOCALDAT",
            "ko_id": 6812,
            "category": "Tier 4 - Dialogue Phrasing",
            "reason": "Clank defiant reply to Klunk",
            "old_ko": "그래도 너 같은 악당을 다룰 만큼은 기운이 넘쳐.",
            "new_ko": "아직 젊음이 넘쳐흐르거든요! 은하계의 쓰레기가 남아있는 한은요!"
        },
        {
            "source": "LOCALDAT",
            "ko_id": 6814,
            "category": "Tier 4 - Dialogue Phrasing",
            "reason": "Fixes Korean particle error and preserves Clank's voice",
            "old_ko": "최소한 옳고 그름이 차이가 있다는 건 알고 있지.",
            "new_ko": "정의와 악의 차이 정도는 구분할 줄 알거든요?"
        },
        {
            "source": "LOCALDAT",
            "ko_id": 6816,
            "category": "Tier 4 - Dialogue Phrasing",
            "reason": "Matches Klunk's philosophical villain claim",
            "old_ko": "올바른 이유를 위해 그릇된 행동을 할 때도 있는 법이라고.",
            "new_ko": "<ELLIPSIS>훨씬 더 불확실하게 돌아가는 법이다 게스!"
        },
        {
            "source": "LOCALDAT",
            "ko_id": 6819,
            "category": "Tier 4 - Dialogue Phrasing",
            "reason": "Klunk mocking Ratchet and Clank partnership",
            "old_ko": "그는 너 보다 멍청하고 약하지만 너는 회전목마에 탄 어린아이처럼 그의 등 뒤에 매달려서 환호성을 지르지.",
            "new_ko": "그런 멍청이가 영웅 행세를 하고<ELLIPSIS> 실력에서 앞서는 네가 부하 노릇이나 하다니 우습지 않나 게스!"
        },
        {
            "source": "LOCALDAT",
            "ko_id": 6820,
            "category": "Tier 4 - Dialogue Phrasing",
            "reason": "Clank's unwavering loyalty to Ratchet",
            "old_ko": "라쳇은 영웅이자 친구로서 충분히 가치를 입증했어.",
            "new_ko": "<COL:02>라쳇<COL:01>은 소중한 친구이자 훌륭한 영웅입니다!"
        },
        {
            "source": "LOCALDAT",
            "ko_id": 6821,
            "category": "Tier 4 - Dialogue Phrasing",
            "reason": "Clank declaring it an honor to adventure with Ratchet",
            "old_ko": "나는 명예롭게도 그의 임무를 도와준 거야.",
            "new_ko": "함께 모험할 수 있어서 오히려 영광이라고요!"
        },
        {
            "source": "LOCALDAT",
            "ko_id": 6822,
            "category": "Tier 4 - Dialogue Phrasing",
            "reason": "Klunk scoffing at self-deception",
            "old_ko": "하! 구역질 날 만큼 위선적이군! 그가 그렇게 위대한 영웅이라면, 어째서",
            "new_ko": "하! 자기기만도 작작 해라 게스! 그렇게 훌륭한 영웅이라면<ELLIPSIS>"
        },
        {
            "source": "LOCALDAT",
            "ko_id": 6823,
            "category": "Tier 4 - Dialogue Phrasing",
            "reason": "Klunk revealing the Mind-Control Helmet scheme",
            "old_ko": "자기 헬멧이 마인드컨트롤 장치와 바뀐것도 모르고 나를 위해 무한의 눈을 훔쳤을까?",
            "new_ko": "내 '세뇌 헬멧'에 조종당하지도 않았을 테고<ELLIPSIS> '무한의 눈'을 훔치지도 않았을 테니 말이다 게스!"
        },
        {
            "source": "LOCALDAT",
            "ko_id": 6824,
            "category": "Tier 4 - Dialogue Phrasing",
            "reason": "Clank realizing Ratchet was mind-controlled",
            "old_ko": "그럴 줄 알았어! 라쳇은 절대로 자기 의지로 그런 짓을 하지 않아!",
            "new_ko": "그랬던 거군요! <COL:02>라쳇<COL:01>은 조종당하고 있었던 거였어요!"
        },
        {
            "source": "LOCALDAT",
            "ko_id": 6825,
            "category": "Tier 4 - Dialogue Phrasing",
            "reason": "Klunk boasting about tricking the organic public",
            "old_ko": "맞아. 하지만 다른 허약한 생물들은 너무도 쉽게 속아버리더군.",
            "new_ko": "그래. 뭐, 생물 찌꺼기 녀석들은 맥없이 홀딱 속아 넘어갔지만 말이다 게스!"
        },
        {
            "source": "LOCALDAT",
            "ko_id": 6839,
            "category": "Tier 4 - Dialogue Phrasing",
            "reason": "Restores punchline joke responding to Klunk's long monologue",
            "old_ko": "생각처럼 간단하게 될까?",
            "new_ko": "전혀 간단하지 않잖아요."
        },
        {
            "source": "LOCALDAT",
            "ko_id": 6883,
            "category": "Tier 4 - Dialogue Phrasing",
            "reason": "Fixes awkward honorific phrasing for agent Clank report to President",
            "old_ko": "또 한 번 <COL:02>클랭크<COL:01>는 요원으로서의 뛰어난 능력을 증명했습니다<ELLIPSIS>게다가 매우 섹시하죠.",
            "new_ko": "또 한 번 <COL:02>클랭크<COL:01> 요원은 뛰어난 능력을 증명했습니다<ELLIPSIS>게다가 아주 매력적이죠."
        },
        {
            "source": "LOCALDAT",
            "ko_id": 6889,
            "category": "Tier 4 - Dialogue Phrasing",
            "reason": "Restores Klunk turned into vacuum cleaner punchline",
            "old_ko": "대통령께서 클렁크의 처분을 우리한테 잘 맡기신 거 같은데. 딱 맞는 장소를 찾은 것 같아.",
            "new_ko": "이 모습이라면 클렁크도 나쁜 짓은 못 하겠네요! 이름하여 '특급 청소기'!"
        },
        {
            "source": "LOCALDAT",
            "ko_id": 6920,
            "category": "Tier 3 - Typo",
            "reason": "Spelling fixes: '말하건데' -> '말하건대', '할꺼' -> '할 것'",
            "old_ko": "이제 말하건데, 내가 받은 돈의 반은 반환해야 할꺼 같아.",
            "new_ko": "이제 말하건대, 내가 받은 돈의 반은 반환해야 할 것 같아."
        },
        {
            "source": "LOCALDAT",
            "ko_id": 6923,
            "category": "Tier 3 - Typo",
            "reason": "Spelling fixes: '뭉겠는데' -> '뭉갰는데', spacing",
            "old_ko": "내가 그 나비를 뭉겠는데 아무일도 없었어. 이상한 일인거 같다고?",
            "new_ko": "내가 그 나비를 뭉갰는데 아무 일도 없었어. 이상한 일인 것 같다고?"
        },
        {
            "source": "LOCALDAT",
            "ko_id": 6926,
            "category": "Tier 3 - Typo",
            "reason": "Spelling fix: '깨달았을꺼야' -> '깨달았을 거야'",
            "old_ko": "상대를 가려서 덤벼야 한다는 걸 깨달았을꺼야. 이건 사실이지.",
            "new_ko": "상대를 가려서 덤벼야 한다는 걸 깨달았을 거야. 이건 사실이지."
        },

        # --- In-game Profiles (7000..7450) ---
        {
            "source": "LOCALDAT",
            "ko_id": 7100,
            "category": "Tier 4 - Dialogue Phrasing",
            "reason": "Fixes mistranslation of rock guitar shredding",
            "old_ko": "닌자의 CPU는 무지막지한 검 공격과 기타의 감미로운 선율만 생각할 수 있어요.",
            "new_ko": "닌자의 CPU는 카타나 검술과 록 기타의 속주에 최적화되어 있어요."
        },
        {
            "source": "LOCALDAT",
            "ko_id": 7185,
            "category": "Tier 3 - Typo",
            "reason": "Fixes typo '중안 보안' -> '중앙 보안 센터에 경보 신호를 보내도록'",
            "old_ko": "단순한 레이저 권총이 아니라 발사하는 순간 중안 보안 장치에 위협이 발생했다고 알려줘요.",
            "new_ko": "단순한 레이저 권총이 아니라 발사하는 순간 중앙 보안 센터에 경보 신호를 보내도록 되어 있어요."
        },
        {
            "source": "LOCALDAT",
            "ko_id": 7200,
            "category": "Tier 3 - Typo",
            "reason": "Fixes phonetic loanword '그린하우스 가스' -> '온실가스'",
            "old_ko": "백열광 대신에 형광등을 사용하면 그린하우스 가스를 일년에 2천만 톤가량 줄일 수 있습니다.",
            "new_ko": "백열등 대신 형광등을 사용하면 온실가스를 일 년에 2천만 톤가량 줄일 수 있습니다."
        },
        {
            "source": "LOCALDAT",
            "ko_id": 7214,
            "category": "Tier 3 - Typo",
            "reason": "Fixes spelling typo '안되서' -> '안 돼서' and clarifies actress-in-training",
            "old_ko": "그녀는 사실 웨이트리스가 아니라 여배우에요. 그 일이 뜻대로 안되서 그렇지<ELLIPSIS>",
            "new_ko": "그녀는 사실 웨이트리스가 아니라 여배우 지망생이에요. 그 일이 뜻대로 안 돼서 그렇지<ELLIPSIS>"
        },
        {
            "source": "LOCALDAT",
            "ko_id": 7240,
            "category": "Tier 3 - Typo",
            "reason": "Fixes typo '소움' -> '소음' and mistranslation",
            "old_ko": "하등한 종족의 여성들은 종종 밝은 빛과 큰 소움에 즐거워 하죠.",
            "new_ko": "변방 행성의 여성 관광객들은 폭발음이나 섬광을 봐도 위험하다고 생각하기는커녕 오히려 즐거워하죠."
        },
        {
            "source": "LOCALDAT",
            "ko_id": 7365,
            "category": "Tier 3 - Typo",
            "reason": "Fixes typos '핀스트라이트' -> '핀스트라이프', '엑세서리' -> '액세서리'",
            "old_ko": "핀스트라이트 수트의 진정한 엑세서리. 라즈푸틴 파이어 에머럴드는 지팡이의 윗 부분에 있습니다.",
            "new_ko": "핀스트라이프 슈트에 어울리는 액세서리는 역시 지팡이겠죠. 상단에는 라스푸틴의 불꽃이라 불리는 보석이 박혀 있습니다."
        },
        {
            "source": "LOCALDAT",
            "ko_id": 7417,
            "category": "Tier 3 - Typo",
            "reason": "Fixes pronoun typo '그거까지' -> '그것까지'",
            "old_ko": "<COL:02>클랭크<COL:01>와 똑같은 <COL:02>제트 부츠<COL:01>도 클렁크에겐 잘 안 어울리네요. '불쾌한 냄새' 스위치를 잘못해서 켜 놓은 것 같긴 하지만 대체 왜 그거까지 같이 붙여서 만들었을까요!",
            "new_ko": "<COL:02>클랭크<COL:01>와 똑같은 <COL:02>제트 부츠<COL:01>도 클렁크에겐 잘 안 어울리네요. '불쾌한 냄새' 스위치를 잘못해서 켜 놓은 것 같긴 하지만 대체 왜 그것까지 같이 붙여서 만들었을까요!"
        },
        {
            "source": "LOCALDAT",
            "ko_id": 7448,
            "category": "Tier 3 - Typo",
            "reason": "Fixes typo '꺼에요' -> '거예요' and removes double space",
            "old_ko": '그 누구도 볼트 보스가 무슨 생각을 하는지 알 수 없어요<ELLIPSIS>  그의 생각을 읽을 수 있다면 아마 "아.. <COL:02>라쳇<COL:01> 녀석을 혼내주지 못했어"라는 걸 읽었을 꺼에요.',
            "new_ko": '그 누구도 볼트 보스가 무슨 생각을 하는지 알 수 없어요<ELLIPSIS> 그의 생각을 읽을 수 있다면 아마 "아.. <COL:02>라쳇<COL:01> 녀석을 혼내주지 못했어"라는 걸 읽었을 거예요.'
        },
        {
            "source": "LOCALDAT",
            "ko_id": 7450,
            "category": "Tier 3 - Typo",
            "reason": "Fixes typo '좋을 꺼에요' -> '좋을 거예요' and matches accurate boss hint",
            "old_ko": "볼트 보스는 하늘로부터 자이언트 볼트를 소환할 수 있습니다. 땅에 닿으면 땅을 파고들기 시작합니다. 폭발할 때는 멀리 떨어져 있는게 좋을 꺼에요. 돈은 전혀 획득할 수 없어요.",
            "new_ko": "볼트 보스는 하늘로부터 자이언트 볼트를 소환할 수 있습니다. 공격용이기 때문에 기다려도 볼트는 얻을 수 없어요. 폭발할 때는 멀리 떨어져 있는 게 좋을 거예요. 바로 도망쳐야 해요."
        },

        # --- Additional HELPLOCALDAT defect ---
        {
            "source": "HELPLOCALDAT",
            "ko_id": -458,
            "category": "Tier 3 - Typo",
            "reason": "Fixes spelling typos '치뤄야' -> '치러야' and '할꺼야' -> '할 거야'",
            "old_ko": "오! 뭔가를 손상시킨 것 같군. 대가를 치뤄야 할꺼야.",
            "new_ko": "오! 뭔가를 파손한 것 같군. 대가를 치러야 할 거야."
        }
    ]

    added_count = 0
    updated_count = 0
    for p in new_patches:
        key = (p.get("source", "LOCALDAT"), p["ko_id"])
        if key in existing_by_key:
            existing_by_key[key].update(p)
            updated_count += 1
        else:
            existing_by_key[key] = p
            added_count += 1

    final_list = list(existing_by_key.values())
    # Sort by source and ko_id
    final_list.sort(key=lambda x: (0 if x.get("source") == "LOCALDAT" else 1, x["ko_id"]))

    with open(patches_file, "w", encoding="utf-8") as f:
        json.dump(final_list, f, ensure_ascii=False, indent=2)

    print(f"Patches updated. Added: {added_count}, Updated existing: {updated_count}, Total patches now: {len(final_list)}")

if __name__ == "__main__":
    main()

