"""
Generate realistic mock social media data for Social Insights Agent.
Run: python generate_mock_data.py
Output: data/mock_data.csv (~620 rows)
"""
import pandas as pd
import random
from datetime import datetime, timedelta
import os

random.seed(42)

# ─── Accounts & Platforms ────────────────────────────────────────────────────
GOOGLE_ACCOUNTS = [
    "googlebrasil", "YouTube Brasil", "Google India", "Android",
    "Made by Google", "GoogleStore", "Pixel", "Google"
]
SOCIAL_NETWORKS = ["Instagram", "TikTok", "YouTube", "Facebook", "X", "Threads", "Reddit"]

# ─── Campaigns → Account mapping ─────────────────────────────────────────────
CAMPAIGNS = {
    "Pixel Camera Q4":        ["Made by Google", "Pixel", "GoogleStore"],
    "Android Safety H2'25":   ["Android", "Google"],
    "Gemini Launch BR":       ["googlebrasil", "Google India"],
    "Android 15 Launch":      ["Android", "googlebrasil"],
    "Pixel 9 Pro Global":     ["Made by Google", "Pixel"],
    "Google One AI Premium":  ["Google", "googlebrasil"],
    "Android Safety BR":      ["googlebrasil", "Android"],
    "Pixel Camera India":     ["Google India", "Pixel"],
    "YouTube Premium BR":     ["YouTube Brasil"],
    "Google Search AI":       ["Google", "googlebrasil", "Google India"],
    "Pixel 9a Launch":        ["Made by Google", "Pixel", "googlebrasil"],
    "Android for Everyone":   ["Android", "Google India"],
}

# ─── Post Captions ────────────────────────────────────────────────────────────
POST_CAPTIONS = {
    "Pixel Camera Q4": [
        "📸 Every moment deserves to be captured perfectly. Meet Pixel 9's revolutionary camera system. #MadeByGoogle #Pixel9",
        "Night, day, or everything in between — the Pixel 9 camera sees it all. Shop now. #Pixel9 #NightSight",
        "The world's most advanced smartphone camera. Now with AI-powered zoom. #MadeByGoogle",
    ],
    "Android Safety H2'25": [
        "Your phone knows when something's wrong. Android Theft Detection — real-time AI that protects your device. #AndroidSafety",
        "Introducing Live Threat Detection: AI-powered security that runs entirely on your device. #Android15",
        "Your data is yours. Private Compute Core keeps AI features local and secure. #AndroidPrivacy",
    ],
    "Gemini Launch BR": [
        "Conheça o Gemini, sua IA do Google. Integrado ao Android, ele aprende com você. #Gemini #GoogleBrasil",
        "Peça ao Gemini para resumir, criar, planejar — tudo direto do seu celular. #Gemini #IA",
        "O futuro da IA chegou ao seu bolso. Gemini no Android 15. #Google #Gemini",
    ],
    "Android 15 Launch": [
        "Android 15 is here. Smarter battery, better privacy, smoother performance. Update now. #Android15",
        "Everything you love about Android, now even better. Android 15 available for Pixel. #Android15",
    ],
    "Pixel 9 Pro Global": [
        "Meet Pixel 9 Pro. The phone that thinks like a photographer. #Pixel9Pro #MadeByGoogle",
        "Pro-level photography. Consumer-level simplicity. Pixel 9 Pro. #Pixel9Pro",
    ],
    "Google One AI Premium": [
        "Google One AI Premium: Gemini Advanced, 2TB storage, and more. Starting at $19.99/month.",
        "Get the full power of Gemini with Google One AI Premium. #GoogleOne #Gemini",
    ],
    "Android Safety BR": [
        "Seu Android agora detecta roubos automaticamente. Conheça o Theft Detection. #AndroidSegurança",
        "Proteção total para seu celular. Novo Android com IA antifurto. #GoogleBrasil #Android",
    ],
    "Pixel Camera India": [
        "Capture the colours of India like never before. Pixel 9 Pro's AI camera. #PixelIndia #MadeByGoogle",
        "Night mode that outshines the competition. Pixel 9 Pro is here. #PixelIndia",
    ],
    "YouTube Premium BR": [
        "YouTube Premium: assista sem anúncios, baixe vídeos e ouça com a tela desligada. #YouTubePremium",
        "Música, podcasts e vídeos — tudo sem interrupções. YouTube Premium. #YouTubeBrasil",
    ],
    "Google Search AI": [
        "AI Overviews: get the information you need, faster. New Google Search. #GoogleSearch",
        "Google Search now with Gemini AI. Ask anything, get answers. #GoogleAI",
        "Novo Google Search com IA. Respostas mais completas, mais rápidas. #GoogleBrasil",
    ],
    "Pixel 9a Launch": [
        "Pixel 9a: flagship camera at a more accessible price. #Pixel9a #MadeByGoogle",
        "Pixel 9a disponível agora. Câmera Pixel, preço mais acessível. #Pixel9a #GoogleBrasil",
    ],
    "Android for Everyone": [
        "Android for Everyone. Powerful AI features available on more devices. #AndroidForAll",
        "Making the best of Android accessible to more people worldwide. #Android #Google",
    ],
}

# ─── Comment Templates ─────────────────────────────────────────────────────────

# Camera quality — English
CAMERA_POS_EN = [
    "The night mode on Pixel 9 is absolutely unreal. Shot this at midnight and it looks like noon 🌙",
    "Switched from iPhone 15 Pro last month and the camera difference is night and day. Google killed it",
    "The astrophotography mode blew my mind. Shot the Milky Way from my backyard with this phone",
    "Pro tip: Magic Eraser is genuinely magic. Removed an entire crowd from my vacation photo seamlessly",
    "Can't believe I'm getting DSLR-quality photos from my phone. The Pixel camera team is incredible",
    "The video stabilization on Pixel 9 is insane. Shot a whole concert and it looks professionally done",
    "Portrait mode with this camera beats my actual DSLR for headshots. No joke at all",
    "The AI photo enhancement features are class-leading. Every shot looks like it was professionally edited",
    "Shot my sister's wedding entirely on Pixel 9 Pro. Everyone thought I hired a photographer 📸",
    "Best investment I've ever made. The camera alone justifies the price for a photographer like me",
    "Low-light performance is incredible. Colors are accurate, noise is minimal. Samsung can't touch this",
    "The Real Tone technology finally captures my skin tone accurately. As a dark-skinned person, this matters",
    "10x zoom quality surprised me completely. Sharp and detailed. Way better than I expected",
    "Best Take saved our family Christmas photo. Got every expression perfect. Love this feature",
    "The computational photography on Pixel is in a league of its own. Other phones can't compete",
]

CAMERA_NEG_EN = [
    "Camera quality has noticeably dropped since the latest update. Low-light shots are grainy now 😞",
    "The zoom quality is disappointing for this price point. iPhone handles 10x zoom much better",
    "Video quality in 4K mode drains battery way too fast. Had to recharge mid-event, very annoying",
    "Front camera is terrible for video calls. The rear camera is amazing but selfie cam disappoints",
    "The AI sharpening is too aggressive. Photos look over-processed, especially portraits",
    "Low-light performance isn't what the ads promise. Very disappointed for the price",
    "Compared to Samsung S24 Ultra the zoom just isn't competitive. Google needs to improve this",
    "My old iPhone 14 takes better videos honestly. Very disappointed with this upgrade",
    "Night Sight takes too long to process. By the time it's done the moment is gone",
    "The ultrawide camera loses too much quality at the edges. Disappointing for landscape shots",
]

CAMERA_NEU_EN = [
    "How do I access the Pro mode settings? Can't find it in the camera app anywhere",
    "Does this have manual focus control? Coming from a Sony I need that specific feature",
    "How does the Pixel 9 camera compare to the Samsung Galaxy S25?",
    "Which mode works best for food photography? Restaurant or manual settings?",
    "Is there a way to save photos in RAW format on this phone?",
    "Anyone use this for real estate photography? Wondering about the wide-angle quality",
    "What's the best way to shoot video at night on Pixel? Any settings recommendations?",
]

# Camera quality — Portuguese
CAMERA_POS_PT = [
    "A câmera do Pixel 9 é simplesmente a melhor que já usei em qualquer celular. Fotos incríveis 🤩",
    "Comprei há 3 semanas e estou impressionado com a qualidade das fotos noturnas. Perfeito!",
    "O modo noturno deixa qualquer câmera concorrente com vergonha. Simplesmente incrível demais",
    "As fotos saem tão boas que minha agência de fotografia ficou curiosa qual câmera eu uso. É o Pixel!",
    "Capturei um nascer do sol ontem de manhã. A câmera captou cada detalhe. Impressionante mesmo",
    "O Magic Eraser me salvou. Removi um estranho de uma foto de família muito importante",
    "Modo retrato do Pixel é melhor que qualquer outra câmera que já tive. Bordas perfeitas",
    "Mudei do iPhone 14 Pro e não me arrependo nada. A câmera é claramente superior no Pixel",
]

CAMERA_NEG_PT = [
    "A câmera frontal decepcionou muito. Por esse preço eu esperava qualidade muito superior mesmo",
    "Desde a última atualização minhas fotos ficaram com muito ruído. Alguém mais passou por isso?",
    "O zoom digital não chega nem perto do Samsung Galaxy S25. Decepcionante para o preço cobrado",
    "Comprei achando que seria melhor que iPhone 15. Na câmera, prefiro o iPhone. Me arrependi",
    "O processamento demora muito. Às vezes perco o momento esperando o Night Sight processar",
]

CAMERA_NEU_PT = [
    "Como ativo o modo astronômico? Tentei várias vezes mas não consigo encontrar a opção",
    "Alguém sabe como salvar em formato RAW nesse celular? Preciso para o trabalho",
    "Como esse Pixel 9 compara com o Samsung S24 Ultra na câmera? Estou indeciso entre os dois",
    "Qual modo é melhor para fotografar comida? Uso muito para o meu perfil de gastronomia",
]

# Camera quality — Spanish
CAMERA_POS_ES = [
    "La cámara del Pixel 9 es espectacular. Las fotos nocturnas son de otro nivel completamente 🌙",
    "Me cambié del iPhone 15 Pro y la diferencia en la cámara es brutal. Google ganó en esto",
    "El modo noche del Pixel deja a todos los competidores muy atrás. Simplemente increíble",
    "Fotografío bodas como hobby y el Pixel 9 Pro es mi cámara de respaldo favorita ahora",
    "La estabilización de video es impresionante. Grabé un concierto completo y quedó perfecto",
]

CAMERA_NEG_ES = [
    "La cámara frontal podría ser mejor para el precio. La trasera es excelente pero la selfie decepciona",
    "En modo zoom el Samsung todavía supera al Pixel claramente. Necesitan mejorar eso urgente",
    "Los videos en 4K consumen batería muy rápido. Necesito cargar el teléfono constantemente",
    "El procesamiento nocturno tarda demasiado. Para cuando termina ya perdí el momento",
]

# Battery — English
BATTERY_POS_EN = [
    "Battery optimization with Android 15 is a game changer. Finally no more dead phone at 3pm",
    "I've been getting 2 full days of battery life on normal usage. Incredible improvement from before",
    "The adaptive battery feature actually learned my usage patterns. Super impressed with this",
    "First phone ever where I don't carry a power bank everywhere. Battery life is genuinely that good",
    "Wireless charging is so fast it charges overnight even at slow speeds. Love this convenience",
]

BATTERY_NEG_EN = [
    "Battery drains super fast when using GPS navigation. Goes from 100% to 20% in just 2 hours",
    "The 5G battery drain is still too high. Wish there was an option to auto-switch to LTE",
    "Battery health dropped to 87% after just 6 months. Not acceptable at this price point",
    "Screen-on time is disappointingly short. My 3-year-old iPhone 13 lasts much longer than this",
    "Overnight charging with adaptive charging still drains to 80% by morning. Something is wrong",
]

BATTERY_NEU_EN = [
    "How long does the battery typically last with heavy use? Thinking of buying this phone",
    "Is fast charging included in the box or do I need to buy it separately?",
    "Anyone know if there's a battery saver mode that doesn't kill performance?",
]

BATTERY_POS_PT = [
    "Bateria do Pixel 9 dura muito mais do que esperava! Uso pesado e chega no fim do dia tranquilo",
    "Com Android 15 a bateria melhorou muito. Antes durava um dia, agora dura dia e meio facilmente",
    "O carregamento adaptativo noturno protege muito a saúde da bateria. Ideia genial do Google",
]

BATTERY_NEG_PT = [
    "A bateria drena muito rápido com GPS ligado. Preciso de carregador no carro sempre agora",
    "Saúde da bateria caiu para 85% em 8 meses. Isso não é aceitável no preço pago por esse celular",
    "Uso moderado e a bateria não passa de 12 horas. Muito abaixo do prometido no marketing",
]

# AI Features — English
AI_POS_EN = [
    "Magic Eraser is literally magic. Removed an entire person from my vacation photo seamlessly",
    "The AI transcription on Google Recorder is best in class. Handles Brazilian Portuguese perfectly",
    "Gemini integration in Android is incredible. It's like having a personal assistant everywhere",
    "The AI-powered call screening saves me hours every week from annoying spam calls",
    "Gemini on Android now answers my complex work questions better than typing on desktop",
    "The on-device AI processing means my data stays private. That's a huge deal for me",
    "Circle to Search is absolutely incredible. Just circle anything and Google knows what it is",
    "Gemini Advanced summarized a 50-page report for me in 30 seconds. Mind blown completely",
    "The AI photo unblur feature recovered photos I thought were lost forever. Insane technology",
]

AI_NEG_EN = [
    "Gemini still can't match ChatGPT for complex reasoning tasks. Google needs to seriously step up",
    "The AI photo editing is too heavy-handed. No way to turn off the auto-processing",
    "Gemini gives incorrect information too often for me to trust it for actual work tasks",
    "The AI features require constant internet connection. Should work offline for privacy",
    "AI Overviews in Google Search are often wrong or misleading. They need more accuracy",
]

AI_POS_PT = [
    "O Gemini no Android está ficando cada vez mais inteligente. Já uso mais do que o ChatGPT",
    "A transcrição de áudio automática é perfeita mesmo em português. Muito impressionado",
    "O Magic Eraser salvou várias fotos minhas. Removo elementos indesejados em segundos",
    "IA do Pixel reconhece textos em qualquer língua. Genial para viagens internacionais",
    "Gemini resumiu meu TCC inteiro em 2 minutos. Impossível fazer isso sem essa tecnologia",
]

AI_NEG_PT = [
    "O Gemini ainda erra muito em português. Às vezes as respostas simplesmente não fazem sentido",
    "Prefiro o ChatGPT para trabalho. O Gemini ainda está muito atrás em raciocínio complexo",
    "A edição de foto com IA fica artificial demais. Preferia ter controle manual das edições",
]

AI_POS_ES = [
    "El borrador mágico es increíble. Eliminé a una persona de una foto de vacaciones sin dejar rastro",
    "Circle to Search me cambió la vida. Círculo alrededor de cualquier cosa y Google lo identifica",
    "Gemini en Android es como tener un asistente personal siempre disponible. Lo recomiendo",
]

AI_NEG_ES = [
    "Gemini todavía no llega al nivel de ChatGPT para tareas complejas. Google necesita mejorar",
    "Las funciones de IA consumen mucha batería en segundo plano. Necesitan optimizarlas",
]

# Security — English
SECURITY_POS_EN = [
    "Theft Detection actually worked when someone tried to snatch my bag! Phone locked instantly and I got it back",
    "The new Android security features are incredibly comprehensive. Finally feel truly safe",
    "Biometric authentication on Pixel is the fastest and most accurate I've ever used",
    "Quarterly security updates give me real peace of mind. Much better than my old Android device",
    "Private Compute Core means AI features work without sharing my data. Love this approach",
    "Find My Device worked perfectly when I lost my phone at the airport. Lifesaver feature",
]

SECURITY_NEG_EN = [
    "How do I activate Theft Detection? I've searched everywhere in settings and cannot find it",
    "The fingerprint scanner sometimes takes 3-4 tries to unlock. Very frustrating in daily use",
    "Security update pushed today broke my mobile banking app. Had to manually roll back",
    "Face unlock still gets fooled by a good photo. Not truly secure for banking apps",
    "Theft Detection feature is great in theory but the setup process is very confusing",
    "Can someone explain exactly how to turn on Theft Detection? The documentation is unclear",
]

SECURITY_POS_PT = [
    "A detecção de roubo funcionou de verdade! Tentaram roubar meu celular e ele travou instantaneamente",
    "Atualizações de segurança mensais me dão muita tranquilidade. Melhor que meu Android antigo",
    "O reconhecimento facial noturno do Pixel é perfeito. Nunca falha mesmo no escuro total",
    "Find My Device me salvou quando perdi o celular no metrô. Encontrei em menos de 10 minutos",
]

SECURITY_NEG_PT = [
    "Como ativo a detecção de roubo? Tentei várias vezes mas não consigo encontrar nas configurações",
    "O leitor de digital às vezes demora muito para reconhecer. Bastante frustrante no dia a dia",
    "A atualização de segurança quebrou meu app bancário. Precisei reverter manualmente para usar",
    "Alguém sabe onde fica a opção de detecção de roubo? Procurei em todo lugar nas configurações",
    "Como configuro a detecção de roubo passo a passo? Não consegui entender as instruções",
]

SECURITY_NEU_PT = [
    "Como funciona a detecção de roubo? Alguém pode explicar como ativar e configurar?",
    "Onde encontro as configurações de segurança avançadas no Android 15?",
]

SECURITY_NEG_ES = [
    "¿Cómo activo la detección de robo? No encuentro la opción en ningún menú de configuración",
    "El escáner de huella a veces no funciona bien con las manos húmedas o frías",
    "Alguien sabe como activar la detección de robo? No encuentro la opción en settings",
]

# iOS Comparison — English
IOS_POS_EN = [
    "Switched from iPhone 15 to Pixel 9 and will NEVER go back. Camera alone is worth it",
    "Android 15 is finally smoother than iOS for daily tasks. Google has come so far",
    "The customization on Android vs iPhone is incomparable. Miss absolutely nothing about iOS",
    "Google apps work so much better on native Android. Makes sense but still impressive",
    "After 8 years on iPhone, made the switch to Pixel. Best decision I've made this year",
]

IOS_NEG_EN = [
    "Sorry but iOS 18 is still smoother in animations than Android 15. Google needs to fix this",
    "iMessage integration issues make it hard to switch from iPhone in a group chat heavy world",
    "App quality on iOS is still generally higher than Android versions of the same apps sadly",
    "Battery analytics in iOS are more detailed and useful than Android's equivalent dashboard",
]

IOS_ES = [
    "Cambié de iPhone a Android y la diferencia en precio/calidad es increíble. No vuelvo al iPhone",
    "iOS sigue siendo más fluido en animaciones pero Android gana en todo lo demás",
    "La integración con servicios de Google en Android no tiene comparación con iOS. Mucho mejor",
    "Después de 5 años en iPhone probé el Pixel y la cámara me convenció completamente",
]

# Pricing — English
PRICING_NEG_EN = [
    "The price is just too high for most people. Google needs a mid-range Pixel that's affordable",
    "$1099 for a phone is insane. Features are great but not worth that price point for most",
    "Google should offer more carrier deals. Unlocked price makes it inaccessible to most people",
]

PRICING_NEG_PT = [
    "Não consigo entender por que o Google não lança o Pixel no Brasil. A câmera é incrível mas o preço é absurdo",
    "R$7000 por um celular é impossível para a maioria dos brasileiros. Precisam de versão acessível",
    "O Pixel não é vendido oficialmente no Brasil e ainda assim cobram preço de importação absurdo",
    "Google, por favor lancen o Pixel no Brasil com preço acessível. Estamos aguardando há anos",
    "Por que pagar tão caro em importação se o Google não quer lançar o Pixel por aqui oficialmente?",
]

PRICING_NEG_ES = [
    "El precio es demasiado alto para el mercado latinoamericano. Necesitan opciones accesibles",
    "En México el Pixel cuesta el doble que en EEUU. Google necesita pensar en mercados emergentes",
    "¿Por qué Google no lanza el Pixel en toda Latinoamérica? La demanda existe. El precio no ayuda",
]

# Regional concerns
REGIONAL_PT = [
    "Quando o Google vai lançar oficialmente o Pixel no Brasil? Estamos cansados de esperar",
    "O atendimento ao cliente do Google no Brasil é péssimo. Precisam melhorar com urgência",
    "O Google Pay ainda não funciona em todos os bancos brasileiros. Precisam ampliar parcerias",
    "Gemini em português ainda está muito abaixo do GPT-4. Quando vai melhorar para o nosso idioma?",
]

REGIONAL_ES = [
    "¿Cuándo llegará el Pixel oficialmente a México? Ya me cansé de esperar respuesta",
    "El soporte de Google en América Latina deja mucho que desear. Necesitan mejorar urgente",
    "Google Pay todavía no funciona con todos los bancos en Colombia. Cuando lo arreglan?",
]

# Spam / noise — realistic social media noise (~20% of dataset)
SPAM = [
    # Engagement bait & self-promotion
    "FOLLOW ME @techreviews_daily FOR DAILY TECH CONTENT 🔥🔥🔥",
    "Subscribe to my YouTube for honest reviews! Link in bio 👇",
    "DM me for collaboration opportunities 📩",
    "Check my profile for a giveaway! 🎁",
    "Drop a comment to win a gift card! 💰",
    "Go follow @gadget_king99 for daily deals!!!",
    "I post tech content every day, follow for more! 🚀",
    # Pure emoji / reaction noise
    "First! 🎉",
    "💯💯💯",
    "👍",
    "❤️❤️❤️",
    "🔥🔥🔥",
    "👏👏👏",
    "😍😍😍",
    "🙌🙌",
    "💪💪💪",
    "🤩🤩",
    # One-word / filler
    "Nice",
    "Same 🙏",
    "Wow 😍",
    "Cool!",
    "Facts",
    "Agreed",
    "Lol",
    "fr fr",
    "no way",
    # Generic positive noise (no actionable content)
    "Great post! Love the content",
    "Love this ❤️",
    "Amazing! 🙌",
    "Can't wait to try this!",
    "I got mine last week!!",
    "This is awesome content, keep it up!",
    "Best brand ever no cap 🔥",
    # Off-topic / unrelated complaints
    "Google Maps is broken again, keeps crashing on my old phone",
    "Why did you remove the Podcasts app?? Bring it back NOW",
    "Gmail is showing ads in my inbox. Absolutely disgusted 😤",
    "My Google account got hacked and support is useless 😡",
    "YouTube keeps recommending the same videos over and over",
    "Google Drive deleted all my files with no warning. Horrible",
    "Por que o YouTube fica travando no meu Android antigo?",
    "Alguém mais com problema no Google Maps? Tá dando erro aqui",
    "Google cancelou meu pedido na Play Store sem motivo algum",
    "¿Por qué YouTube elimina videos sin explicación? Es un abuso",
    "Mi cuenta de Google fue suspendida sin razón. Inaceptable",
    # Spam links / phishing
    "www.techdeals99.xyz - best prices guaranteed",
    "Get free gift cards at bit.ly/freecard123",
    "Earn $500/day working from home: shorturl.at/spam",
    # Political / completely off-topic rants
    "Big tech is controlling us all. Wake up people!!! 👁️",
    "Stop using Google, they spy on everything you do",
    "All these companies are the same. None of them care about us",
    "Technology is ruining society. Put the phone down people",
    # Gibberish / test comments
    "asdfghjkl",
    "test",
    "...",
    "kkkkkkkkk",
    "hahaha",
    "jajajaja",
    "rsrsrsrsrs",
    # Foreign-language noise (no relevance to query topics)
    "كيف يمكنني الحصول على هاتف مجاني؟",
    "这个手机怎么样？值得买吗？",
    "Очень интересно, спасибо за пост!",
]

# ─── Build the full comment pool ─────────────────────────────────────────────
# Each entry: (text, sentiment)
COMMENT_POOL = (
    [(t, "Positive") for t in CAMERA_POS_EN + CAMERA_POS_PT + CAMERA_POS_ES] +
    [(t, "Negative") for t in CAMERA_NEG_EN + CAMERA_NEG_PT + CAMERA_NEG_ES] +
    [(t, "Neutral")  for t in CAMERA_NEU_EN + CAMERA_NEU_PT] +
    [(t, "Positive") for t in BATTERY_POS_EN + BATTERY_POS_PT] +
    [(t, "Negative") for t in BATTERY_NEG_EN + BATTERY_NEG_PT] +
    [(t, "Neutral")  for t in BATTERY_NEU_EN] +
    [(t, "Positive") for t in AI_POS_EN + AI_POS_PT + AI_POS_ES] +
    [(t, "Negative") for t in AI_NEG_EN + AI_NEG_PT + AI_NEG_ES] +
    [(t, "Positive") for t in SECURITY_POS_EN + SECURITY_POS_PT] +
    [(t, "Negative") for t in SECURITY_NEG_EN + SECURITY_NEG_PT + SECURITY_NEG_ES] +
    [(t, "Neutral")  for t in SECURITY_NEU_PT] +
    [(t, "Positive") for t in IOS_POS_EN + IOS_ES[:2]] +
    [(t, "Negative") for t in IOS_NEG_EN + IOS_ES[2:]] +
    [(t, "Negative") for t in PRICING_NEG_EN + PRICING_NEG_PT + PRICING_NEG_ES] +
    [(t, "Neutral")  for t in REGIONAL_PT + REGIONAL_ES] +
    [(t, "Neutral")  for t in SPAM]  # spam is "Neutral" sentiment label
)

# ─── Username generation ──────────────────────────────────────────────────────
FIRST_PARTS = ["tech", "pixel", "android", "google", "mobile", "camera", "photo", "daily",
               "real", "just", "the", "user", "dev", "pro", "ia", "digital", "foto"]
LAST_PARTS  = ["lover", "fan", "geek", "guy", "girl", "nerd", "pro", "insider", "review",
               "brasil", "mx", "india", "news", "life", "hub", "world", "hacks"]

def random_username():
    if random.random() < 0.3:
        # Name-style handle
        names = ["joao_silva", "maria_garcia", "raj_patel", "lucas_souza", "ana_lima",
                 "carlos_mendez", "priya_sharma", "felipe_costa", "sarah_jones",
                 "mateus_rocha", "isabela_faria", "diego_morales", "fatima_hassan",
                 "arjun_kumar", "camila_oliveira", "roberto_campos"]
        return random.choice(names) + str(random.randint(10, 999))
    return random.choice(FIRST_PARTS) + random.choice(LAST_PARTS) + str(random.randint(1, 9999))

# ─── Date helpers ─────────────────────────────────────────────────────────────
START_DATE = datetime(2024, 1, 1)
END_DATE   = datetime(2026, 3, 1)

def random_date(start=START_DATE, end=END_DATE):
    delta = end - start
    return start + timedelta(days=random.randint(0, delta.days))

def random_asset_url():
    uid = ''.join(random.choices("abcdefghijklmnopqrstuvwxyz0123456789", k=24))
    return f"prod8-media-proxy.sprinklr.com/channel/data/media/{uid}"

# ─── Generate rows ────────────────────────────────────────────────────────────
def generate_rows(n=620):
    rows = []
    campaigns = list(CAMPAIGNS.keys())

    for _ in range(n):
        campaign = random.choice(campaigns)
        account  = random.choice(CAMPAIGNS[campaign])
        network  = random.choice(SOCIAL_NETWORKS)
        captions = POST_CAPTIONS.get(campaign, ["Google product announcement post."])
        caption  = random.choice(captions)

        post_date    = random_date()
        comment_date = post_date + timedelta(
            hours=random.randint(0, 72),
            minutes=random.randint(0, 59)
        )

        comment_text, sentiment = random.choice(COMMENT_POOL)

        # Bias likes by sentiment
        if sentiment == "Positive":
            likes = int(random.betavariate(2, 5) * 5000)
        elif sentiment == "Negative":
            likes = int(random.betavariate(1, 8) * 2000)
        else:
            likes = int(random.betavariate(1, 10) * 500)

        rows.append({
            "date":              post_date.strftime("%Y-%m-%d"),
            "google_account":    account,
            "social_network":    network,
            "post_caption":      caption,
            "asset_url":         random_asset_url(),
            "campaign_name":     campaign,
            "comment_text":      comment_text,
            "comment_sentiment": sentiment,
            "comment_likes":     likes,
            "comment_author":    random_username(),
            "comment_date":      comment_date.strftime("%Y-%m-%d %H:%M:%S"),
        })

    return rows

# ─── Main ─────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    os.makedirs("data", exist_ok=True)
    rows = generate_rows(620)
    df = pd.DataFrame(rows)
    output_path = "data/mock_data.csv"
    df.to_csv(output_path, index=False)
    print(f"✅  Generated {len(df)} rows → {output_path}")
    print(f"    Sentiment distribution:\n{df['comment_sentiment'].value_counts().to_string()}")
    print(f"    Platforms:\n{df['social_network'].value_counts().to_string()}")
    print(f"    Campaigns:\n{df['campaign_name'].value_counts().to_string()}")
