import telebot
from telebot import types
import json
import os
import threading
import time
import pytz
from datetime import datetime, timedelta
def load_json(filename):
    """تحميل البيانات من ملف JSON."""
    with open(filename, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}

def save_json(filename, data):
    """حفظ البيانات إلى ملف JSON."""
    with open(filename, "w") as f:
        json.dump(data, f, indent=4)
def load_config(): 
    return load_json("config.json")

# 📌 أضف تعريف الدالة save_config هنا!
def save_config(data): 
    return save_json("config.json", data)        
timezone = pytz.timezone('Africa/Cairo')
# 🔑 المنطقة الزمنية المعتمدة الآن: بغداد
BAGHDAD_TZ = pytz.timezone('Asia/Baghdad')
owner = '@A_E20877' # يوزر المالك
FACTORY_RESET_PASSWORD = "ali"
bot_name = 'بوت توب كاش الاستثماري'   
TOKEN = "8466192636:AAFuFrn95NnRdE3WIPsiAzVt_Wua1-ys8cI" # توكنك
ADMIN_ID = "6454550864" # ايدي الادمن (للوحة التحكم الرئيسية)
ADMIN_ID = 6454550864

ADMIN_IDS = load_config().get('admin_ids', ['6454550864'])
EXEMPT_ID = 6454550864
CHANNEL_ID = "6454550864"  # قناة الاشعارات الدخول
CHANNEL_ID4 = "6454550864"
CHANNEL_ID2 = "6454550864" # قناة العدادات و القروض و التحويل و الوكلاء
CHANNEL_ID3 = "6454550864" #اثباتات السحب والمتجر 
WITHDRAWAL_ADMIN_ID = "6454550864" # آيدي المشرف المسؤول عن طلبات السحب والموافقة عليها (جديد)
bot = telebot.TeleBot(TOKEN)
user_transfer_data = {} 
REQUIRED_CHANNEL_ID = "-1001823792351"
TRANSFER_FEE = 5000 # عمولة التحويل الثابتة
SHOP_ADMIN_ID = "6454550864" #مشرف قسم المتجر
EDIT_FILE = 'edit.json'
coupon_temp_data = {} 
def save_admin_ids(new_admin_list):
    """تحديث وحفظ قائمة ADMIN_IDS في config.json."""
    global ADMIN_IDS # 🚨 هام جداً لتحديث المتغير العام في الذاكرة
    config = load_config()
    config['admin_ids'] = new_admin_list
    save_config(config)
    ADMIN_IDS = new_admin_list # تحديث المتغير في الكود
def is_admin(user_id):
    return str(user_id) in ADMIN_IDS
def load_edit_settings():
    """تحميل بيانات الإعدادات الإضافية من edit.json."""
    if not os.path.exists(EDIT_FILE):
        return {}
    try:
        # قراءة البيانات مع دعم UTF-8
        with open(EDIT_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return {} # إرجاع قاموس فارغ في حال وجود خطأ
def load_agents():
    """تحميل بيانات الوكلاء من agents.json."""
    if not os.path.exists(AGENTS_FILE):
        return {}
    try:
        # قراءة البيانات مع دعم UTF-8 للأحرف العربية
        with open(AGENTS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return {} # إرجاع قاموس فارغ في حال وجود خطأ في الملف

def save_agents(agents_data):
    """حفظ بيانات الوكلاء إلى agents.json."""
    # ensure_ascii=False للحفاظ على الأحرف العربية، و indent=4 للتنسيق
    with open(AGENTS_FILE, 'w', encoding='utf-8') as f:
        json.dump(agents_data, f, indent=4, ensure_ascii=False)
user_states = {} 
def initialize_files():
    """تهيئة الملفات JSON إذا لم تكن موجودة."""
    files = ["users.json", "products.json", "a.json", "edit.json", "config.json", "bot_status.json", "coupons.json", "withdrawals.json"]
    for filename in files:
        if not os.path.exists(filename):
            with open(filename, "w") as f:
                # إعطاء قيمة ابتدائية مناسبة لكل ملف
                if filename == "edit.json":
                    json.dump({"referral_points": 50}, f)
                elif filename == "config.json":
                    json.dump({"auto_send_enabled": True}, f)
                elif filename == "bot_status.json":
                    json.dump({"active": True, "reason": "البوت في وضع التشغيل", "resume_time": ""}, f)
                else:
                    json.dump({}, f)

initialize_files()


# دوال التحميل والحفظ المخصصة
# ... (موقع الدوال في ملفك)

def load_users():
    """تحميل بيانات المستخدمين من ملف users.json وضمان تعيين دور 'admin' لجميع آيديات ADMIN_IDS."""
    
    # 1. تحميل البيانات من الملف
    if not os.path.exists('users.json'):
        # ⚠️ يجب التأكد من تهيئة ملف users.json عند بداية تشغيل البوت
        return {}
    try:
        with open('users.json', 'r', encoding='utf-8') as f:
            users = json.load(f)
    except (IOError, json.JSONDecodeError):
        users = {}
    
    # 2. التحقق من آيديات الأدمن وتعيين الدور لهم
    users_modified = False
    
    # التكرار على كل آيدي موجود في القائمة ADMIN_IDS
    for admin_id_str in ADMIN_IDS:
        # التأكد من أن الآيدي موجود كـ key (على افتراض أن الآيديات في users.json هي سلاسل نصية)
        if admin_id_str in users:
            current_role = users[admin_id_str].get("role", "user")
            
            # إذا كان الدور ليس "owner" أو "admin"، قم بتعيينه كـ "admin"
            if current_role not in ["owner", "admin"]:
                users[admin_id_str]["role"] = "admin"
                users_modified = True
                
        # 💡 ملاحظة: إذا لم يكن الآيدي موجوداً في users، فهذا يعني أن الأدمن لم يبدأ البوت بعد، ولا نحتاج لعمل أي شيء.

    # 3. حفظ التغييرات إذا تم تعديل أي دور
    if users_modified:
        # ⚠️ يجب التأكد من وجود دالة save_users(users)
        save_users(users)

    return users

def save_users(users):
    """حفظ بيانات المستخدمين إلى ملف users.json"""
    try:
        with open('users.json', 'w', encoding='utf-8') as f:
            json.dump(users, f, indent=4, ensure_ascii=False)
    except IOError as e:
        print(f"❌ خطأ في حفظ بيانات المستخدمين: {e}")

# ...
# --------------------------------------------------------------------------
# 📌 دالة التحقق من الاشتراك (يجب أن تكون في أعلى الملف)
# --------------------------------------------------------------------------
def check_subscription(user_id, channel_id):
    """التحقق من اشتراك المستخدم في القناة الإلزامية."""
    try:
        member = bot.get_chat_member(channel_id, user_id)
        # إذا كانت حالة المستخدم "عضو" أو "مدير" أو "منشئ"
        return member.status in ['member', 'administrator', 'creator']
    except telebot.apihelper.ApiTelegramException as e:
        # خطأ في حالة القناة غير صحيحة أو البوت غير مسؤول
        print(f"Error checking subscription for {user_id}: {e}")
        return False

# --------------------------------------------------------------------------
# 📌 دالة إرسال رسالة الاشتراك الإجباري (لتجنب تكرار الكود)
# --------------------------------------------------------------------------
# ⚠️ يجب التأكد من أن المتغير REQUIRED_CHANNEL_ID مُعرَّف كـ global ومتحدث

def send_sub_required_message(chat_id):
    # 1. استخدام الآيدي المحفوظ في المتغير العام
    # ملاحظة: إذا كان الآيدي يبدأ بـ -100 (سوبر جروب/قناة)، يجب استخدام اليوزر نيم أو get_chat لجلب الرابط
    # لكن لتبسيط العملية، سنفترض أننا نريد ربط القناة بالآيدي مباشرة (وهذا لا يعمل غالباً في t.me)
    # الحل الأفضل هو استخدام رابط دعوة دائم إذا كان الآيدي رقمي، أو ربط القناة باسمها المعرف (@username).
    
    # 💡 الحل الأبسط والآمن: إنشاء رابط القناة t.me/c/ID/1 (رابط مشاركة)
    # أو استخدام اسم المستخدم الخاص بالقناة إذا كان معروفا. 
    # سنفترض أن القناة تحتوي على يوزر نيم لتجنب تعقيدات الروابط الرقمية:
    
    try:
        # محاولة جلب معلومات القناة لإنشاء رابط t.me/username
        chat_object = bot.get_chat(REQUIRED_CHANNEL_ID)
        if chat_object.username:
            channel_link = f"https://t.me/{chat_object.username}"
        else:
            # في حال عدم وجود يوزر نيم، نعتمد على الرابط الرقمي (قد لا يعمل)
            # أو رابط مشاركة رسالة داخلية:
            channel_link = f"https://t.me/c/{str(REQUIRED_CHANNEL_ID).replace('-100', '')}/1"
            
    except Exception:
        # في حال فشل جلب المعلومات، نعود إلى استخدام رابط رقمي فقط
        channel_link = f"https://t.me/c/{str(REQUIRED_CHANNEL_ID).replace('-100', '')}/1"
    
    
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(types.InlineKeyboardButton("🔗 اضغط للاشتراك في القناة", url=channel_link))
    markup.add(types.InlineKeyboardButton("✅ تحقق من الاشتراك", callback_data="check_sub_final")) 
    
    bot.send_message(chat_id, 
                     "⚠️ <b>يجب عليك الاشتراك في القناة التالية للاستمرار في استخدام البوت:</b>", 
                     reply_markup=markup, 
                     parse_mode="HTML")

# --------------------------------------------------------------------------
# 📌 فلتر الاشتراك الإجباري العام (الديكوراتور الذي سنستخدمه)
# --------------------------------------------------------------------------
def subscription_required(message):
    user_id = str(message.from_user.id)
    # لا ينطبق الفلتر على الأدمن/المالك
    if user_id == str(ADMIN_ID) or user_id in ADMIN_IDS: # ⚠️ استخدم قائمة الآيديات الإضافية إذا لديك
        return True
        
    if check_subscription(user_id, REQUIRED_CHANNEL_ID):
        return True
    else:
        # إرسال رسالة الإجبار على الاشتراك
        send_sub_required_message(message.chat.id)
        return False # منع تنفيذ المعالج
# --------------------------------------------------------------------------
# 📌 دالة فلتر الاشتراك الإجباري للكولباك (Inline Buttons)
# --------------------------------------------------------------------------
def subscription_required_callback(call):
    user_id = str(call.from_user.id)
    chat_id = call.message.chat.id
    
    # 1. استثناء الأدمن (لن يطبق عليهم الفلتر)
    # ⚠️ تأكد أن ADMIN_ID معرف كـ str أو int حسب استخدامه
    if user_id == str(ADMIN_ID): 
        return True
    
    # 2. استثناء زر التحقق من الاشتراك نفسه لمنع التوقف
    if call.data == "check_sub_final":
        return True
        
    # 3. التحقق من الاشتراك
    if check_subscription(user_id, REQUIRED_CHANNEL_ID):
        return True
    else:
        # 4. إرسال رسالة الإجبار على الاشتراك (إذا كان غير مشترك)
        send_sub_required_message(chat_id)
        
        # 5. إغلاق تنبيه الكولباك
        bot.answer_callback_query(call.id, "⚠️ يرجى الاشتراك في القناة أولاً.", show_alert=True)
        return False    
def load_products(): return load_json("products.json")
def save_products(data): save_json("products.json", data)

def load_a_json(): 
    data = load_json("a.json")
    # التأكد من أن المفاتيح هي سلاسل نصية
    return {str(k): v for k, v in data.items()}

def save_a_json(data): save_json("a.json", data)

def load_edit(): return load_json("edit.json")
def save_edit(data): save_json("edit.json", data)

def load_config(): return load_json("config.json")
def save_config(data): save_json("config.json", data)

def load_bot_status(): return load_json("bot_status.json")
def save_bot_status(data): save_json("bot_status.json", data)

def load_coupons(): return load_json("coupons.json")
def save_coupons(data): save_json("coupons.json", data)

def load_withdrawals(): return load_json("withdrawals.json")
def save_withdrawals(data): save_json("withdrawals.json", data)

# --- منطق العداد التلقائي (الذي يستخدم ملف a.json) ---
def get_rank(points):
    """تحديد الرتبة بناءً على النقاط."""
    if points < 1000: return "مبتدئ"
    elif points < 5000: return "متوسط"
    elif points < 10000: return "متقدم"
    else: return "محترف"

BAGHDAD_TZ = pytz.timezone('Asia/Baghdad') # المنطقة الزمنية لبغداد
ADDITION_INTERVAL = timedelta(hours=24)
# --------------------------------------------------------------------------------

def auto_add_points():
    """إضافة النقاط التلقائية بناءً على التوقيت التالي المحسوب لكل مستخدم."""
    
    while True:
        try:
            config = load_config()
            
            if not config.get("auto_send_enabled", True):
                time.sleep(300) # ينام 5 دقائق فقط إذا كان الإرسال معطلاً
                continue

            a_data = load_a_json()
            users = load_users()
            now = datetime.now(BAGHDAD_TZ)
            updates_made = False
            
            min_sleep_duration = ADDITION_INTERVAL.total_seconds() 
            
            for uid, data in a_data.items():
                
                if isinstance(data, int):
                    pts = data
                    last_added_time = now - ADDITION_INTERVAL
                else:
                    pts = data.get('points_to_add', 0)
                    last_added_str = data.get('last_added_time')
                    try:
                        last_added_time = datetime.fromisoformat(last_added_str).astimezone(BAGHDAD_TZ)
                    except (ValueError, TypeError):
                        last_added_time = now - ADDITION_INTERVAL 

                next_due_time = last_added_time + ADDITION_INTERVAL
                
                if now >= next_due_time and pts > 0 and uid in users:
                    
                    users[uid]["points"] = users[uid].get("points", 0) + pts
                    
                    try:
                         bot.send_message(uid, 
                                          f"تمت إضافة **{pts}** نقطة إلى رصيدك من العداد التلقائي.\nرصيدك الحالي: **{users[uid]['points']}**", 
                                          parse_mode="Markdown")
                    except Exception:
                         pass
                        
                    a_data[uid]['last_added_time'] = next_due_time.isoformat() 
                    updates_made = True
                    
                    next_due_time = next_due_time + ADDITION_INTERVAL


                time_to_wait = next_due_time - now
                
                if time_to_wait.total_seconds() > 0:
                    min_sleep_duration = min(min_sleep_duration, time_to_wait.total_seconds())


            if updates_made:
                save_users(users)
                save_a_json(a_data) 
            final_sleep = min(min_sleep_duration, 1) 
            
            print(f"سوف ينتظر البوت: {final_sleep:.2f} ثانية ({final_sleep / 60:.2f} دقيقة) قبل الفحص التالي.")
            time.sleep(final_sleep)
            

        except Exception as e:
            print(f"خطأ في التحديث التلقائي: {e}")
            time.sleep(60) # الانتظار دقيقة واحدة في حالة وجود خطأ

threading.Thread(target=auto_add_points, daemon=True).start()



@bot.message_handler(func=lambda message: message.text == "📄 جلب الملفات" and message.from_user.id == ADMIN_ID)
def send_all_files(message):
    chat_id = message.chat.id
    
    # قائمة بأسماء الملفات التي تريد إرسالها (يمكنك تعديل هذه القائمة)
    files_to_send = [
        'main.py', 
        'agents.json', 
        'users.json', 
        'products.json', 
        'edit.json',
        'config.json',
        'loan.json',
        'withdrawals.json',
        'a.json'
    ]
    
    # وصف لكل ملف يتم إرساله
    file_descriptions = {
        'main.py': "ملف الكود الرئيسي للبوت الذي يحتوي على جميع الدوال والمعالجات.",
        'agents.json': "ملف قاعدة بيانات الوكلاء. يحتوي على آيدياتهم، أسمائهم، أدوارهم، وأرصدتهم وروابطهم.",
        'users.json': "ملف قاعدة بيانات المستخدمين (الأعضاء) يحتوي على نقاطهم ومعلوماتهم.",
        'products.json': "ملف قاعدة بيانات السلع المتوفرة في المتجر.",
        'edit.json': "الهدية اليومية و رابط الاحالة",
        'config.json': "ملف تشغيل ارسال العدادت",
        'loan.json': "ملف القروض ",
        'withdrawals.json': "ملف عمليات السحب",
        'a.json': "ملف عدادات المستثمرين ملف مهم حقاً"
    }

    files_found = 0
    bot.send_message(chat_id, "⏳ جاري محاولة جلب وإرسال الملفات المطلوبة...")

    for filename in files_to_send:
        if os.path.exists(filename):
            try:
                # محاولة فتح الملف وإرساله
                with open(filename, 'rb') as f:
                    # الحصول على الوصف أو استخدام وصف افتراضي
                    caption = f"📄 اسم الملف: `{filename}`\n\n**الوصف: {file_descriptions.get(filename, 'لا يوجد وصف محدد لهذا الملف.')}"
                    
                    # استخدام send_document لإرسال الملف
                    bot.send_document(
                        chat_id, 
                        f, 
                        caption=caption, 
                        parse_mode="Markdown"
                    )
                    files_found += 1
            except Exception as e:
                # إبلاغ الأدمن إذا فشل إرسال ملف معين
                bot.send_message(chat_id, f"❌ **خطأ: فشل إرسال ملف {filename}. السبب: {e}", parse_mode="Markdown")
        
    
    if files_found > 0:
        bot.send_message(chat_id, f"✅ تم إرسال {files_found} ملف/ملفات بنجاح.", parse_mode="Markdown")
    else:
        bot.send_message(chat_id, "⚠️ تنبيه: لم يتم العثور على أي من ملفات الكود أو قواعد البيانات في مسار تشغيل البوت.")
import sys 
# 🚨 هام: ضع هذا السطر لحل مشكلة الترميز بعد import sys
sys.stdout.reconfigure(encoding='utf-8') 
# ... باقي استيراداتك مثل telebot, threading, time, datetime, pytz ...

# --- 1. الثوابت وإدارة الملفات الجديدة (ضعها مع الثوابت الأخرى) ---
BAGHDAD_TZ = pytz.timezone('Asia/Baghdad') 

LOAN_TIERS = {
    # المفتاح:   الرصيد المطلوب (العداد),   مبلغ القرض (النقاط),   التسمية
    "L80K":   {"required": 1000, "loan_amount": 80000, "label": "80,000 نقطة"},
    "L120K":  {"required": 1500, "loan_amount": 120000, "label": "120,000 نقطة"},
    "L200K":  {"required": 2500, "loan_amount": 200000, "label": "200,000 نقطة"},
    "L400K":  {"required": 5000, "loan_amount": 400000, "label": "400,000 نقطة"},
    "L800K":  {"required": 10000, "loan_amount": 800000, "label": "800,000 نقطة"},
    "L2M":    {"required": 25000, "loan_amount": 2000000, "label": "2,000,000 نقطة"},
    "L4M":    {"required": 50000, "loan_amount": 4000000, "label": "4,000,000 نقطة"},
}
SUPPORT_LINK = "https://t.me/topcash121" # رابط الدعم الفني الذي طلبته
def load_a(): 
    # يُفترض وجود دالة load_json
    data = load_json("a.json")
    return {str(k): v for k, v in data.items()}

def save_a(data): 
    # يُفترض وجود دالة save_json
    save_json("a.json", data)

def load_loans(): 
    data = load_json("loan.json")
    return {str(k): v for k, v in data.items()}

def save_loans(data): 
    save_json("loan.json", data)
def get_current_counter_value(user_id):
    """جلب قيمة العداد الصحيحة من a.json بغض النظر عن تنسيقها."""
    a_data = load_a() 
    counter_entry = a_data.get(user_id)

    if isinstance(counter_entry, dict) and 'points_to_add' in counter_entry:
        return counter_entry['points_to_add']
    elif isinstance(counter_entry, int):
        return counter_entry
    else:
        return 0

@bot.callback_query_handler(func=lambda call: call.data == "loans_menu" and subscription_required_callback(call))
def loans_menu_callback(call):
    user_id = str(call.from_user.id)

    # تخطي الايقاف للادمن
    if not is_bot_active(call.message) and not is_admin(user_id):
        return bot.answer_callback_query(call.id, "❌ البوت متوقف مؤقتاً.")
        
    # هنا، إذا وصل الكود إلى هذا السطر، فإما أن البوت يعمل أو أن المستخدم هو الأدمن.

    current_counter = get_current_counter_value(user_id)
    
    loans = load_loans()
    users = load_users() 
    
    active_or_pending_loans = [loan for loan in loans.get(user_id, []) if loan['status'] in ['active', 'pending']]
    
    markup = types.InlineKeyboardMarkup(row_width=1)

    
    # ... بقية منطق الدالة ...
    
    # 🚨 تم التعديل إلى HTML (<b>)
    text = (
        "🏦 <b>قسم القروض والنقاط</b> 🏦\n\n"
        f"عدادك الحالي (a.json): <b>{current_counter:,} نقطة</b>\n"
        f"رصيدك الحالي (النقاط): <b>{users.get(user_id, {}).get('points', 0):,} نقطة</b>\n\n"
    )

    if active_or_pending_loans:
        loan_status = active_or_pending_loans[0]['status']
        loan_amount = active_or_pending_loans[0]['amount']
        
        if loan_status == 'active':
            due_date_str = active_or_pending_loans[0]['due_date']
            text += (f"⚠️ <b>لديك قرض نشط حالياً</b> بقيمة {loan_amount:,} نقطة.\n"
                     f"تاريخ الاستحقاق: {due_date_str}.\n\n"
                     f"لا يمكنك طلب قرض جديد حتى يتم تسديد القرض الحالي.")
        elif loan_status == 'pending':
            text += (f"⏳ <b>لديك طلب قرض قيد المراجعة</b> بقيمة {loan_amount:,} نقطة.\n\n"
                     f"الرجاء الانتظار حتى تتم الموافقة عليه من قبل الإدارة.")
            
        markup.add(types.InlineKeyboardButton("⬅️ رجوع للقائمة الرئيسية", callback_data="back_to_main_menu"))

    else:
        text += ("اختر القرض المناسب لك. يجب أن يكون عدادك الحالي <b>أعلى أو يساوي</b> العداد المطلوب. فترة التسديد: <b>30 يوماً</b>.")
        for key, loan_info in LOAN_TIERS.items():
            required = loan_info['required']
            if current_counter >= required:
                button_text = f"✅ قرض {loan_info['label']} (يتطلب عداد {required:,})"
                callback_data = f"confirm_loan:{key}" 
            else:
                button_text = f"❌ قرض {loan_info['label']} (يتطلب عداد {required:,})"
                callback_data = "no_action" 
            markup.add(types.InlineKeyboardButton(button_text, callback_data=callback_data))

        markup.add(types.InlineKeyboardButton("⬅️ رجوع للقائمة الرئيسية", callback_data="back_to_main_menu"))
    
    try:
        bot.edit_message_text(chat_id=call.message.chat.id, 
                              message_id=call.message.message_id,
                              text=text, 
                              reply_markup=markup,
                              parse_mode='HTML') # 🚨 تم التعديل إلى HTML
    except Exception as e:
        if "message is not modified" not in str(e):
             bot.send_message(call.message.chat.id, text, reply_markup=markup, parse_mode='HTML') # 🚨 تم التعديل إلى HTML

    bot.answer_callback_query(call.id)


@bot.callback_query_handler(func=lambda call: call.data.startswith("confirm_loan:"))
def confirm_loan_callback(call):
    user_id = str(call.from_user.id)
    _, loan_key = call.data.split(":")
    loan_info = LOAN_TIERS.get(loan_key)
    if not loan_info:
        return bot.answer_callback_query(call.id, "❌ خطأ في بيانات القرض.")

    required = loan_info['required']
    loan_amount = loan_info['loan_amount']
    loan_label = loan_info['label']

    current_counter = get_current_counter_value(user_id)
    
    if current_counter < required:
        bot.answer_callback_query(call.id, "❌ العداد غير كافٍ للحصول على هذا القرض.")
        return loans_menu_callback(call)

    # 🚨 تم التعديل إلى HTML (<b>)
    text = (
        f"🚨 <b>تأكيد طلب قرض: {loan_label}</b> 🚨\n\n"
        f"<b>المبلغ الذي سيضاف إلى رصيدك (نقاط):</b> <b>{loan_amount:,} نقطة</b>\n"
        f"<b>العداد المطلوب (a.json):</b> {required:,} نقطة\n"
        f"<b>فترة التسديد:</b> 30 يوماً. (في حال الموافقة)\n\n" 
        "<b>ملاحظة هامة:</b> في تاريخ الاستحقاق، سيتم خصم <b>نفس مبلغ القرض</b> من نقاطك. إذا كانت نقاطك غير كافية، سيتم <b>حظر حسابك بشكل رسمي (banned: true)</b>.\n\n"
        "<b>بعد الضغط على زر الموافقة، سيتم إرسال طلبك للإدارة للمراجعة والموافقة اليدوية.</b>"
    )
    
    markup = types.InlineKeyboardMarkup()
    markup.row(
        types.InlineKeyboardButton(f"✅ نعم، أرسل طلب {loan_label}", callback_data=f"take_loan:{loan_key}"),
        types.InlineKeyboardButton("❌ إلغاء والعودة", callback_data="loans_menu")
    )
    
    try:
        bot.edit_message_text(chat_id=call.message.chat.id, 
                              message_id=call.message.message_id,
                              text=text, 
                              reply_markup=markup,
                              parse_mode='HTML') # 🚨 تم التعديل إلى HTML
    except Exception:
        bot.send_message(call.message.chat.id, text, reply_markup=markup, parse_mode='HTML') # 🚨 تم التعديل إلى HTML
        
    bot.answer_callback_query(call.id) 
    
    
@bot.callback_query_handler(func=lambda call: call.data.startswith("take_loan:"))
def take_loan_callback(call):
    """تسجيل طلب القرض بـ حالة 'pending' وإشعار الأدمن."""
    user_id = str(call.from_user.id)
    _, loan_key = call.data.split(":")
    loan_info = LOAN_TIERS.get(loan_key)
    
    if not loan_info:
        return bot.answer_callback_query(call.id, "❌ خطأ في بيانات القرض.")

    required = loan_info['required']
    loan_amount = loan_info['loan_amount']
    
    users = load_users()
    loans = load_loans()
    u = users.get(user_id, {})
    
    current_counter = get_current_counter_value(user_id)
    
    if current_counter < required:
        return bot.answer_callback_query(call.id, "❌ العداد غير كافٍ للحصول على هذا القرض.")
        
    active_or_pending_loans = [loan for loan in loans.get(user_id, []) if loan['status'] in ['active', 'pending']]
    
    if active_or_pending_loans:
        return bot.answer_callback_query(call.id, "❌ لديك قرض نشط أو قيد الانتظار مسبقاً. يرجى التسديد/الانتظار قبل طلب جديد.")

    issue_date = datetime.now(BAGHDAD_TZ)
    issue_date_str = issue_date.strftime('%Y-%m-%d %H:%M:%S%z') 
    
    loan_record = {
        "id": str(int(time.time() * 1000)),
        "user_id": user_id,
        "amount": loan_amount,
        "required_counter": required, 
        "issue_date": issue_date_str,
        "due_date": "", 
        "status": "pending", 
        "reminders_sent": 0 
    }
    
    if user_id not in loans:
        loans[user_id] = []
        
    loans[user_id].append(loan_record)
    save_loans(loans)

    msg_to_user = (
        f"✅ <b>تم استلام طلب قرضك بنجاح!</b>\n\n"
        f"<b>المبلغ المطلوب:</b> <b>{loan_amount:,} نقطة</b>\n"
        f"سيتم مراجعة الطلب من قبل الإدارة. يرجى الانتظار لحين الموافقة."
    )
    
    try:
        full_edit_text = f"🏦 <b>قسم القروض والنقاط</b> 🏦\n\n{msg_to_user}"
        bot.edit_message_text(full_edit_text, 
                          call.message.chat.id, call.message.message_id, parse_mode='HTML', # 🚨 تم التعديل إلى HTML
                          reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("⬅️ العودة للقائمة", callback_data="back_to_main_menu")))
    except Exception:
        bot.send_message(call.message.chat.id, msg_to_user, parse_mode='HTML') # 🚨 تم التعديل إلى HTML
        
    bot.answer_callback_query(call.id, "✅ تم إرسال الطلب للإدارة.")
    
    user_name = u.get('name', 'مستخدم')
    username = u.get('username', 'لا يوجد')
    
    markup_admin = types.InlineKeyboardMarkup()
    markup_admin.row(
        types.InlineKeyboardButton("✅ موافقة", callback_data=f"approve_loan:{user_id}:{loan_record['id']}:{loan_key}"),
        types.InlineKeyboardButton("❌ رفض", callback_data=f"reject_loan:{user_id}:{loan_record['id']}")
    )
    
    admin_msg = (
        f"🔔 <b>طلب قرض جديد بانتظار الموافقة!</b>\n\n"
        f"<b>المقترض:</b> {user_name} (@{username})\n"
        f"<b>آيدي المقترض:</b> <code>{user_id}</code>\n"
        f"<b>مبلغ القرض:</b> {loan_amount:,} نقطة\n"
        f"<b>العداد الحالي (a.json):</b> {current_counter:,} نقطة\n"
    )
    bot.send_message(WITHDRAWAL_ADMIN_ID, admin_msg, parse_mode="HTML", reply_markup=markup_admin)
# 5. دوال موافقة ورفض الأدمن

@bot.callback_query_handler(func=lambda call: call.data.startswith("approve_loan:"))
def approve_loan_callback(call):
    """تنفيذ منح القرض بعد موافقة الأدمن."""
    admin_id = str(call.from_user.id)
    if admin_id != WITHDRAWAL_ADMIN_ID:
        return bot.answer_callback_query(call.id, "❌ لست المالك لتنفيذ هذا الإجراء.")
        
    _, user_id, loan_id, loan_key = call.data.split(":")
    loan_info = LOAN_TIERS.get(loan_key)
    
    if not loan_info:
        return bot.answer_callback_query(call.id, "❌ خطأ في بيانات القرض.")
        
    loan_amount = loan_info['loan_amount']
    
    loans = load_loans()
    users = load_users()
    u = users.get(user_id, {})
    
    loan_to_approve = next((loan for loan in loans.get(user_id, []) if loan['id'] == loan_id and loan['status'] == 'pending'), None)
    
    if not loan_to_approve:
        bot.edit_message_text("❌ لم يتم العثور على طلب القرض أو تمت الموافقة عليه/رفضه مسبقاً.", call.message.chat.id, call.message.message_id)
        return bot.answer_callback_query(call.id, "❌ لم يتم العثور على الطلب.")

    users[user_id] = users.get(user_id, {})
    users[user_id]['points'] = users[user_id].get('points', 0) + loan_amount
    save_users(users)
    
    issue_date = datetime.now(BAGHDAD_TZ)
    due_date = issue_date + timedelta(days=30) 
    
    loan_to_approve['status'] = 'active'
    loan_to_approve['issue_date'] = issue_date.strftime('%Y-%m-%d %H:%M:%S%z') 
    loan_to_approve['due_date'] = due_date.strftime('%Y-%m-%d %H:%M:%S%z')
    
    save_loans(loans)
    
    bot.edit_message_text(
        f"✅ تم منح القرض بنجاح:\n\nالمقترض: <code>{user_id}</code>\nالمبلغ: {loan_amount:,} نقطة\nتاريخ الاستحقاق: {due_date.strftime('%Y-%m-%d | %H:%M:%S')}", 
        call.message.chat.id, call.message.message_id, parse_mode="HTML"
    )

    msg_to_user = (
        f"🎉 <b>تمت الموافقة على طلب قرضك!</b> 🎉\n\n"
        f"<b>المبلغ الممنوح:</b> <b>{loan_amount:,} نقطة</b>\n"
        f"<b>رصيدك الجديد:</b> <b>{users[user_id]['points']:,} نقطة</b>\n"
        f"<b>تاريخ الاستحقاق (التسديد):</b> {due_date.strftime('%Y-%m-%d | %H:%M:%S')}\n\n"
        "⚠️ سيتم خصم المبلغ تلقائياً في تاريخ الاستحقاق (بعد 30 يوماً). في حال عدم كفاية الرصيد، سيتم حظر حسابك."
    )
    try:
        bot.send_message(user_id, msg_to_user, parse_mode='HTML') # 🚨 تم التعديل إلى HTML
    except Exception: pass
    
    user_name = u.get('name', 'مستخدم')
    username = u.get('username', 'لا يوجد')
    channel_msg = (
        f"💸 <b>عملية قرض ممنوح (موافقة إدارية):</b>\n\n"
        f"<b>المقترض:</b> {user_name} (@{username})\n"
        f"<b>آيدي المقترض:</b> <code>{user_id}</code>\n"
        f"<b>مبلغ القرض:</b> {loan_amount:,} نقطة\n"
    )
    bot.send_message(CHANNEL_ID2, channel_msg, parse_mode="HTML") 
    
    bot.answer_callback_query(call.id, "✅ تم منح القرض.")


@bot.callback_query_handler(func=lambda call: call.data.startswith("reject_loan:"))
def reject_loan_callback(call):
    """تغيير حالة طلب القرض إلى 'rejected'."""
    admin_id = str(call.from_user.id)
    if admin_id != WITHDRAWAL_ADMIN_ID:
        return bot.answer_callback_query(call.id, "❌ لست المالك لتنفيذ هذا الإجراء.")
        
    _, user_id, loan_id = call.data.split(":")
    
    loans = load_loans()
    
    loan_to_reject = next((loan for loan in loans.get(user_id, []) if loan['id'] == loan_id and loan['status'] == 'pending'), None)
    
    if not loan_to_reject:
        bot.edit_message_text("❌ لم يتم العثور على طلب القرض أو تمت معالجته مسبقاً.", call.message.chat.id, call.message.message_id)
        return bot.answer_callback_query(call.id, "❌ لم يتم العثور على الطلب.")

    loan_to_reject['status'] = 'rejected'
    save_loans(loans)
    
    bot.edit_message_text(
        f"❌ تم رفض طلب القرض بنجاح:\n\nالمقترض: <code>{user_id}</code>\nالمبلغ: {loan_to_reject['amount']:,} نقطة.", 
        call.message.chat.id, call.message.message_id, parse_mode="HTML"
    )

    msg_to_user = (
        f"❌ <b>تم رفض طلب قرضك.</b>\n\n"
        f"<b>المبلغ المطلوب:</b> <b>{loan_to_reject['amount']:,} نقطة</b>\n"
        f"يرجى التواصل مع الدعم الفني للاستفسار."
    )
    try:
        markup_support = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("💬 الدعم الفني", url=SUPPORT_LINK)) 
        bot.send_message(user_id, msg_to_user, parse_mode='HTML', reply_markup=markup_support) # 🚨 تم التعديل إلى HTML
    except Exception: pass
    
    bot.answer_callback_query(call.id, "❌ تم رفض القرض.")

def loan_repayment_checker():
    """التحقق من مواعيد استحقاق القروض (الخصم أو الحظر) وإرسال التذكيرات."""
    while True:
        try:
            loans = load_loans()
            users = load_users()
            now = datetime.now(BAGHDAD_TZ).replace(microsecond=0)
            
            loans_modified = False
            users_modified = False
            new_loans_data = {} 
            
            for user_id, user_loans in loans.items():
                updated_user_loans = []
                
                for loan in user_loans:
                    
                    if loan['status'] == 'active':
                        due_date_str = loan['due_date']
                        
                        due_date = datetime.strptime(due_date_str, '%Y-%m-%d %H:%M:%S%z') 
                        
                        loan_amount = loan['amount']
                        time_to_due = due_date - now
                        
                        # 1. إرسال التذكير (Modified to HTML)
                        if timedelta(hours=1) < time_to_due <= timedelta(days=1, minutes=5) and loan.get('reminders_sent', 0) == 0:
                            try:
                                bot.send_message(user_id, 
                                                f"⚠️ <b>تذكير: موعد تسديد القرض يقترب!</b> ⚠️\n\n"
                                                f"يستحق سداد قرضك البالغ <b>{loan_amount:,} نقطة</b> خلال أقل من 24 ساعة.\n"
                                                "يرجى التأكد من أن رصيدك كافٍ لتجنب الحظر.", 
                                                parse_mode='HTML') # 🚨 تم التعديل إلى HTML
                                loan['reminders_sent'] = 1
                                loans_modified = True
                            except Exception: pass
                        
                        # 2. معالجة الاستحقاق (تاريخ الاستحقاق أو تجاوزه)
                        if now >= due_date:
                            
                            if user_id in users:
                                user_points = users[user_id].get('points', 0)
                                user_data = users[user_id]
                                user_name = user_data.get('name', 'مستخدم')
                                username = user_data.get('username', 'لا يوجد')
                                
                                # أ. حالة النقاط كافية: الخصم والتسديد (Modified to HTML)
                                if user_points >= loan_amount:
                                    users[user_id]['points'] -= loan_amount
                                    loan['status'] = 'paid'
                                    users_modified = True
                                    loans_modified = True
                                    
                                    # إشعار للمستخدم
                                    try:
                                        bot.send_message(user_id, 
                                                         f"✅ <b>تم تسديد القرض بنجاح!</b> ✅\n\nتم خصم <b>{loan_amount:,} نقطة</b> تلقائياً.\nرصيدك الحالي: <b>{users[user_id]['points']:,} نقطة</b>.", 
                                                         parse_mode='HTML') # 🚨 تم التعديل إلى HTML
                                    except Exception: pass
                                        
                                    # إشعار للقناة - (Uses HTML)
                                    channel_msg = (
                                        f"💰 <b>تم تسديد قرض:</b>\n\n<b>المستخدم:</b> {user_name} (@{username})\n<b>آيدي:</b> <code>{user_id}</code>\n<b>المبلغ المسدد:</b> {loan_amount:,} نقطة"
                                    )
                                    bot.send_message(CHANNEL_ID2, channel_msg, parse_mode="HTML")
                                    
                                # ب. حالة النقاط غير كافية: الحظر (Modified to HTML)
                                else:
                                    loan['status'] = 'defaulted'
                                    loans_modified = True
                                    
                                    users[user_id]['banned'] = True 
                                    users_modified = True
                                    
                                    # إشعار للمستخدم
                                    ban_message = (
                                        f"🚫 <b>تم حظر حسابك!</b> 🚫\n\n<b>السبب:</b> عدم تسديد القرض المستحق بقيمة <b>{loan_amount:,} نقطة</b>.\n"
                                        f"رصيدك الحالي: {user_points:,} نقطة (غير كافٍ).\n"
                                        f"لرفع الحظر تواصل مع <b>الدعم الفني</b>."
                                    )
                                    markup_ban = types.InlineKeyboardMarkup()
                                    markup_ban.add(types.InlineKeyboardButton("💬 الدعم الفني", url=SUPPORT_LINK))
                                    
                                    try:
                                        bot.send_message(user_id, ban_message, parse_mode='HTML', reply_markup=markup_ban) # 🚨 تم التعديل إلى HTML
                                    except Exception: pass
                                        
                                    # إشعار للقناة - (Uses HTML)
                                    channel_msg = (
                                        f"🚨 <b>حظر بسبب عدم التسديد!</b> 🚨\n\n<b>المستخدم:</b> {user_name} (@{username})\n<b>آيدي:</b> <code>{user_id}</code>\n<b>مبلغ القرض:</b> {loan_amount:,} نقطة"
                                    )
                                    bot.send_message(CHANNEL_ID2, channel_msg, parse_mode="HTML")
                        
                    updated_user_loans.append(loan)

                new_loans_data[user_id] = updated_user_loans
                
            if loans_modified:
                save_loans(new_loans_data)
                
            if users_modified:
                save_users(users)
                
        except Exception as e:
            # هذا السطر مهم للإبقاء عليه لمعرفة أي خطأ غير متوقع
            print(f"خطأ غير متوقع في التحقق من القروض: {e}")

        # فترة التحديث: 3 ثواني
        time.sleep(3)



# --- 4. سطر تشغيل الدالة (يجب أن يكون في نهاية الملف) ---

# 🚨 هام: هذا السطر لتشغيل الفحص الخلفي
# threading.Thread(target=loan_repayment_checker, daemon=True).start()          
##       
def get_badge(user_data):
    """تحديد الشارة بناءً على الإحصائيات."""
    if user_data.get('referrals', 0) >= 50: return "أسطورة الدعوات"
    elif user_data.get('purchases', 0) >= 10: return "مسوّق ذهبي"
    elif user_data.get('points', 0) >= 500: return "صاحب نقاط"
    else: return "مستخدم عادي"

def update_user_rank(user_id):
    """دالة وهمية يمكن استخدامها لتحديث حالة المستخدم إذا لزم الأمر."""
    pass
    

def is_bot_active(context):
    """
    التحقق من حالة إيقاف/تشغيل البوت، مع استثناء الأدمن (ADMINo_ID) والآيدي الإضافي.
    """
    
    # 1. تحديد الآيدي الإضافي المطلوب تخطيه (يجب أن يكون رقمًا صحيحًا)
    
    
    # 2. محاولة استخراج آيدي المستخدم (كعدد صحيح)
    try:
        # استخراج آيدي المستخدم من أي سياق (رسالة أو ضغطة زر)
        if hasattr(context, 'from_user'):
            user_id_int = context.from_user.id
        elif hasattr(context, 'message') and hasattr(context.message, 'from_user'):
            user_id_int = context.message.from_user.id
        else:
            return True 
    except Exception:
        return True

    # 🚀 3. السماح للأدمن والآيدي المُعفى بالمرور دائمًا
    # يجب استخدام  الرقمي للمقارنة
    if user_id_int == ADMIN_IDS or user_id_int == EXEMPT_ID: 
        return True
        
    # 4. المنطق الأصلي للتحقق من حالة البوت لغير الأدمن
    status = load_bot_status()
    if not status.get("active", True):
        # تحديد chat_id لإرسال رسالة التوقف
        chat_id = context.chat.id if hasattr(context, 'chat') else context.message.chat.id
        
        bot.send_message(
            chat_id,
            f"❌ البوت متوقف مؤقتاً.\nالسبب: {status.get('reason', 'غير معروف')}\nيعود للعمل في: {status.get('resume_time', 'غير معروف')}"
        )
        return False
        
    return True
# --- الأزرار الشفافة الجديدة (Main Menu) ---
def get_main_menu_markup(user_id):
    """إنشاء أزرار المنيو الرئيسية الشفافة."""
    main_menu_markup = types.InlineKeyboardMarkup(row_width=2)
    users = load_users()
    u = users.get(str(user_id), {})
    
    # تحديد نص زر الهدية اليومية
    gift_text = "🎁 الهدية اليومية"
    if u.get("last_claim"):
        try:
            last_claim_time = datetime.strptime(u["last_claim"], "%Y-%m-%d %H:%M:%S")
            time_diff = datetime.now() - last_claim_time
            if time_diff < timedelta(days=1):
                time_remaining = timedelta(days=1) - time_diff
                hours_left, remainder = divmod(time_remaining.seconds, 3600)
                minutes_left, _ = divmod(remainder, 60)
                gift_text = f"🎁 متبقي: {hours_left} س {minutes_left} د"
        except Exception:
            pass

    main_menu_markup.add(
        types.InlineKeyboardButton("شراء عداد", callback_data="show_products_menu"),
        types.InlineKeyboardButton("مشترياتي", callback_data="show_purchases_inline"),
        types.InlineKeyboardButton("اهداء عداد", callback_data="gift_counter")
    )
    main_menu_markup.add(
    )
    main_menu_markup.add(
        types.InlineKeyboardButton("🛒 المتجر الالكتروني", callback_data="shop_menu"),
        types.InlineKeyboardButton("اعرض سلعتك", callback_data="offer")
    )
    main_menu_markup.add(
        types.InlineKeyboardButton(gift_text, callback_data="claim_daily_gift_inline"),
        types.InlineKeyboardButton("تجربة الكوبون", callback_data="ask_for_coupon_inline"),

        
    )
    main_menu_markup.add(
        types.InlineKeyboardButton("⬅️ تحويل نقاط ➡️", callback_data="transfer_points_inline"),
        types.InlineKeyboardButton("الوكلاء", callback_data="show_agents_list"),
        types.InlineKeyboardButton("💵 القروض 💵", callback_data="loans_menu") 
    )         
    main_menu_markup.add(
        types.InlineKeyboardButton("💰 سحب أرباحي", callback_data="withdrawal_menu"),
        types.InlineKeyboardButton("الاثباتات", url="https://t.me/Topcash124")
    )        

    main_menu_markup.add(
        types.InlineKeyboardButton("الاحكام و السياسات", callback_data="about_us_inline"),
        types.InlineKeyboardButton("الضمانات", callback_data="guarantees")
    )
    main_menu_markup.add(
        types.InlineKeyboardButton("💬 الدعم الفني", url="https://t.me/Topcash121"),
        types.InlineKeyboardButton("📢 القناة", url="https://t.me/topcash2005")
    )
   
    return main_menu_markup

WITHDRAWAL_METHODS = {
    #mastercaed
    "mastercard_10": {"label": "ماستركارد 10$", "amount": 10, "cost": 50000, "fields": ["card_long", "card_short"]},
    "mastercard_25": {"label": "ماستركارد 25$", "amount": 25, "cost": 125000, "fields": ["card_long", "card_short"]},
    "mastercard_50": {"label": "ماستركارد 50$", "amount": 50, "cost": 250000, "fields": ["card_long", "card_short"]},
    "mastercard_100": {"label": "ماستركارد 100$", "amount": 100, "cost": 500000, "fields": ["card_long", "card_short"]},
    "mastercard_150": {"label": "ماستركارد 150$", "amount": 150, "cost": 750000, "fields": ["card_long", "card_short"]},
    #zaincash
    "zaincash_10": {"label": "زين كاش 10$", "amount": 10, "cost": 55000, "fields": ["phone"]},
    "zaincash_25": {"label": "زين كاش 25$", "amount": 25, "cost": 137000, "fields": ["phone"]},
    "zaincash_50": {"label": "زين كاش 50$", "amount": 50, "cost": 275000, "fields": ["phone"]},
    "zaincash_100": {"label": "زين كاش 100$", "amount": 100, "cost": 550000, "fields": ["phone"]},
    "zaincash_150": {"label": "زين كاش 150$", "amount": 150, "cost": 825000, "fields": ["phone"]},
    #ather
    "ether_balance_5": {"label": "رصيد اثير 5$", "amount": 5, "cost": 23000, "fields": ["phone"]},
    "ether_balance_10": {"label": "رصيد اثير 10$", "amount": 10, "cost": 45000, "fields": ["phone"]},
    "ether_balance_15": {"label": "رصيد اثير 15$", "amount": 15, "cost": 67000, "fields": ["phone"]},
    #asia
    "asia_balance_5": {"label": "رصيد اسيا 5$", "amount": 5, "cost": 24000, "fields": ["phone"]},
    "asia_balance_10": {"label": "رصيد اسيا 10$", "amount": 10, "cost": 46000, "fields": ["phone"]},
    "asia_balance_15": {"label": "رصيد اسيا 15$", "amount": 15, "cost": 67500, "fields": ["phone"]},
    #USDT
    "usdt_okx_10": {"label": "USDT 10$ (OKX - TRC20)", "amount": 10, "cost": 60000, "fields": ["okx_id", "trc20_address"]},
    "usdt_okx_25": {"label": "USDT 25$ (OKX - TRC20)", "amount": 25, "cost": 135000, "fields": ["okx_id", "trc20_address"]},
    "usdt_okx_50": {"label": "USDT 50$ (OKX - TRC20)", "amount": 50, "cost": 260000, "fields": ["okx_id", "trc20_address"]},
    
}

# مسارات نصوص الحقول (للسؤال)
FIELD_PROMPTS = {
    "card_long": "الرجاء إرسال **الماستر كارد الطويل** (رقم البطاقة الكامل):",
    "card_short": "الرجاء إرسال **الماستر كارد القصير **:",
    "phone": "الرجاء إرسال **رقم الهاتف** المرتبط بطريقة السحب (مثال: 964771XXXXXXX):",
    "okx_id": "الرجاء إرسال **آيدي حسابك في منصة OKX**:",
    "trc20_address": "الرجاء إرسال **عنوان محفظة TRC20** لاستلام USDT:",
}
user_purchase_data = {}         # لحفظ بيانات المستخدم أثناء تجميع الحقول
pending_purchase_requests = {}  # لطلبات الشراء المعلقة بانتظار موافقة المشرف
user_rejection_data = {}        # لحفظ بيانات الرفض المؤقتة للمشرف
STORE_PRODUCTS = {
    # خدمات تلجرام - تلجرام مميز
    "premium_3m": {
        "label": "اشتراك تلجرام مميز (3 أشهر)", "cost": 80000, "category": "telegram",
        "fields": ["telegram_username"], "admin_id": SHOP_ADMIN_ID 
    },
    "premium_6m": {
        "label": "اشتراك تلجرام مميز (6 أشهر)", "cost": 106000, "category": "telegram",
        "fields": ["telegram_username"], "admin_id": SHOP_ADMIN_ID 
    },
    "premium_12m": {
        "label": "اشتراك تلجرام مميز (سنة كاملة)", "cost": 187000, "category": "telegram",
        "fields": ["telegram_username"], "admin_id": SHOP_ADMIN_ID 
    },
    
    # خدمات تلجرام - نجوم تلجرام (المتطلب: يوزر أو رابط منشور)
    "stars_100": {
        "label": "نجوم تلجرام (100 نجمة)", "cost": 13000, "category": "telegram",
        "fields": ["telegram_user_or_link"], "admin_id": SHOP_ADMIN_ID
    },
    "stars_500": {
        "label": "نجوم تلجرام (500 نجمة)", "cost": 64000, "category": "telegram",
        "fields": ["telegram_user_or_link"], "admin_id": SHOP_ADMIN_ID
    },
    "stars_1000": {
        "label": "نجوم تلجرام (1000 نقطة)", "cost": 127000, "category": "telegram",
        "fields": ["telegram_user_or_link"], "admin_id": SHOP_ADMIN_ID
    },
    
    # شحن ألعاب - شدات ببجي (المتطلب: آيدي واسم اللعبة)
    "pubg_120uc": {
        "label": "شدات ببجي (120 شدة)", "cost": 17000, "category": "games",
        "fields": ["game_id", "game_name"], "admin_id": SHOP_ADMIN_ID
    },
    "pubg_180uc": {
        "label": "شدات ببجي (180 شدة)", "cost": 25000, "category": "games",
        "fields": ["game_id", "game_name"], "admin_id": SHOP_ADMIN_ID
    },
    "pubg_336uc": {
        "label": "شدات ببجي (336 شدة)", "cost": 40000, "category": "games",
        "fields": ["game_id", "game_name"], "admin_id": SHOP_ADMIN_ID
    },
    "pubg_688uc": {
        "label": "شدات ببجي (688 شدة)", "cost": 62000, "category": "games",
        "fields": ["game_id", "game_name"], "admin_id": SHOP_ADMIN_ID
    },
    "pubg_1170uc": {
        "label": "شدات ببجي (1170 شدة)", "cost": 110000, "category": "games",
        "fields": ["game_id", "game_name"], "admin_id": SHOP_ADMIN_ID
    },
}
##
# دوال إهداء عداد بصيغة رقمية في a.json (ID: number)
# تم إزالة التاريخ والوقت تمامًا من جميع الرسائل
# 🚨 يجب أن يكون ADMIN_ID = 6454550864 كرقم في بداية ملفك
# 🚨 يجب أن تكون user_states = {} معرفة كقاموس عالمي
# 🚨 يجب أن تكون دالتا load_agents() و save_agents(agents) معرفتين

# ----------------------------------------------------
# 1. مشغل بدء عملية إدارة الوكلاء (الزر النصي)
# ----------------------------------------------------
# 💡 التصحيح المقترح: يجب استخدام الدالة is_admin هنا
@bot.message_handler(func=lambda message: message.text in ["➕ إضافة وكيل", "➖ إزالة وكيل"] and is_admin(message.from_user.id))
def agent_management_reply_buttons(message):
    # ... بقية الكود
    chat_id = message.chat.id
    
    if message.text == '➕ إضافة وكيل':
        # بدء عملية الإضافة
        user_states[chat_id] = {'state': 'waiting_for_agent_id', 'data': {}}
        bot.send_message(chat_id, "✅ **بدء إضافة وكيل**\n\nالرجاء إرسال **آيدي** الوكيل الجديد (مثل 1234567890).")
    
    elif message.text == '➖ إزالة وكيل':
        # بدء عملية الإزالة
        try:
            agents = load_agents()
        except NameError:
            return bot.send_message(chat_id, "❌ خطأ: دالة load_agents غير معرفة.")
            
        if not agents:
            bot.send_message(chat_id, "❌ لا يوجد وكلاء لإزالتهم حاليًا.")
            return

        # عرض قائمة الوكلاء الحاليين
        agent_list = "\n".join([f"• {data.get('name', 'غير معروف')} (ID: `{agent_id}`)" for agent_id, data in agents.items()])
        
        user_states[chat_id] = {'state': 'waiting_for_agent_id_to_remove'}
        bot.send_message(chat_id, 
            text=f"🗑️ **بدء إزالة وكيل**\n\nالرجاء إرسال **آيدي** الوكيل المراد حذفه.\n\n**الوكلاء الحاليون:**\n{agent_list}\n\n**تحذير:** لا يمكن التراجع عن هذه العملية.",
            parse_mode="Markdown"
        )

# ----------------------------------------------------
# 2. مشغل الإجراءات المتعددة الخطوات (يستجيب للرسائل اللاحقة)
# ----------------------------------------------------
# 💡 التصحيح المقترح: يجب استخدام is_admin هنا
@bot.message_handler(func=lambda message: message.chat.id in user_states and is_admin(message.from_user.id))
def agent_management_message_handler(message):
# ...
    chat_id = message.chat.id
    user_state = user_states.get(chat_id, {})
    
    # --- عملية إضافة وكيل (متعددة الخطوات) ---
    if user_state.get('state') == 'waiting_for_agent_id':
        try:
            agent_id = str(int(message.text.strip()))
            agents = load_agents()
            
            if agent_id in agents:
                bot.send_message(chat_id, f"❌ **خطأ:** الوكيل بالآيدي `{agent_id}` موجود بالفعل باسم: {agents[agent_id]['name']}. تم إلغاء العملية.")
                del user_states[chat_id]
                return
            
            user_state['data']['id'] = agent_id
            user_state['state'] = 'waiting_for_agent_name'
            bot.send_message(chat_id, "☑️ تم استلام الآيدي.\nالآن، الرجاء إرسال **اسم** الوكيل (مثل وكيل مبيعات احمد).")
            
        except ValueError:
            bot.send_message(chat_id, "❌ **خطأ:** الآيدي يجب أن يكون رقماً صحيحاً. حاول مرة أخرى.")
            
    elif user_state.get('state') == 'waiting_for_agent_name':
        agent_name = message.text.strip()
        if not agent_name:
            bot.send_message(chat_id, "❌ **خطأ:** لا يمكن أن يكون الاسم فارغاً. حاول مرة أخرى.")
            return

        user_state['data']['name'] = agent_name
        user_state['state'] = 'waiting_for_agent_role'
        user_state['data']['balance'] = 0 # الرصيد الافتراضي
        
        bot.send_message(chat_id, "☑️ تم استلام الاسم.\nالآن، الرجاء إرسال **دور** الوكيل (مثل agent, shop_admin, المدير).")

    elif user_state.get('state') == 'waiting_for_agent_role':
        agent_role = message.text.strip()
        if not agent_role:
            bot.send_message(chat_id, "❌ **خطأ:** لا يمكن أن يكون الدور فارغاً. حاول مرة أخرى.")
            return

        user_state['data']['role'] = agent_role
        user_state['state'] = 'waiting_for_agent_account_link'
        bot.send_message(chat_id, "☑️ تم استلام الدور.\nالآن، الرجاء إرسال **رابط حساب** الوكيل الخاص به (مثلاً: https://t.me/username).")

    elif user_state.get('state') == 'waiting_for_agent_account_link':
        account_link = message.text.strip()
        if not account_link:
            bot.send_message(chat_id, "❌ **خطأ:** لا يمكن أن يكون رابط الحساب فارغاً. حاول مرة أخرى.")
            return

        user_state['data']['account_link'] = account_link
        user_state['state'] = 'waiting_for_agent_channel_link'
        bot.send_message(chat_id, "☑️ تم استلام رابط الحساب.\n\nأخيراً، الرجاء إرسال **رابط قناة** الوكيل (إذا لم يكن لديه قناة، أرسل `لا يوجد`).")


    elif user_state.get('state') == 'waiting_for_agent_channel_link':
        channel_link = message.text.strip()
        
        # معالجة إدخال "لا يوجد"
        if channel_link in ['لا يوجد', '']:
             channel_link_to_save = 'N/A'
        else:
             channel_link_to_save = channel_link
        
        # تجميع البيانات وحفظها
        new_agent_id = user_state['data']['id']
        new_agent_data = {
            'name': user_state['data']['name'],
            'balance': user_state['data']['balance'],
            'role': user_state['data']['role'],
            'account_link': user_state['data']['account_link'], 
            'channel_link': channel_link_to_save
        }
        
        agents = load_agents()
        agents[new_agent_id] = new_agent_data
        save_agents(agents) # ⚠️ يجب تعريف دالة save_agents
        
        confirmation_msg = (
            "✅ <b>تمت إضافة الوكيل بنجاح!</b>\n\n"
            f"<b>الآيدي:</b> <code>{new_agent_id}</code>\n"
            f"<b>الاسم:</b> {new_agent_data['name']}\n"
            f"<b>الدور:</b> {new_agent_data['role']}\n"
            f"<b>رابط الحساب:</b> <code>{new_agent_data['account_link']}</code>\n"
            f"<b>رابط القناة:</b> <code>{new_agent_data['channel_link']}</code>\n"
            f"<b>الرصيد الافتراضي:</b> <code>{new_agent_data['balance']}</code>"
        )
        bot.send_message(chat_id, confirmation_msg, parse_mode="HTML")
        del user_states[chat_id] # مسح الحالة والانتهاء من العملية
        
    # --- عملية إزالة وكيل ---
    elif user_state.get('state') == 'waiting_for_agent_id_to_remove':
        try:
            agent_id_to_remove = str(int(message.text.strip()))
            agents = load_agents()
            
            if agent_id_to_remove not in agents:
                bot.send_message(chat_id, f"❌ **خطأ:** الوكيل بالآيدي `{agent_id_to_remove}` غير موجود في الملف. حاول مرة أخرى.")
                return

            removed_agent_name = agents[agent_id_to_remove]['name']

            # إزالة الوكيل والحفظ في ملف agents.json
            del agents[agent_id_to_remove]
            save_agents(agents)
            
            bot.send_message(chat_id, 
                             f"✅ **تمت إزالة الوكيل بنجاح!**\n\n"
                             f"تم حذف الوكيل: **{removed_agent_name}** بالآيدي `{agent_id_to_remove}`.")
            del user_states[chat_id] # مسح الحالة والانتهاء من العملية

        except ValueError:
            bot.send_message(chat_id, "❌ **خطأ:** الآيدي يجب أن يكون رقماً صحيحاً. حاول مرة أخرى.")


# ----------------------------------------------------
# 3. مشغل الإلغاء عبر زر Inline (بدون تغيير)
# ----------------------------------------------------
@bot.callback_query_handler(func=lambda call: call.data in ['admin_add_agent', 'admin_remove_agent'])
def agent_management_callbacks(call):
    # 🛑 تم تصحيح هذا المشغل أيضاً لضمان المقارنة الصحيحة
    if call.from_user.id != ADMIN_IDS:
        bot.answer_callback_query(call.id, "❌ أنت لست المسؤول.")
        return

    chat_id = call.message.chat.id
    
    if call.data == 'admin_add_agent':
        # بدء عملية الإضافة
        user_states[chat_id] = {'state': 'waiting_for_agent_id', 'data': {}}
        bot.edit_message_text(
            chat_id=chat_id, 
            message_id=call.message.message_id, 
            text="✅ **بدء إضافة وكيل**\n\nالرجاء إرسال **آيدي** الوكيل الجديد (مثل 1234567890).",
            reply_markup=None 
        )
    
    elif call.data == 'admin_remove_agent':
        # بدء عملية الإزالة
        try:
            agents = load_agents()
        except NameError:
            return bot.answer_callback_query(call.id, "❌ خطأ: دالة load_agents غير معرفة.")
            
        if not agents:
            bot.answer_callback_query(call.id, "❌ لا يوجد وكلاء لإزالتهم حاليًا.")
            return

        # عرض قائمة الوكلاء الحاليين لمساعدة الأدمن
        agent_list = "\n".join([f"• {data.get('name', 'غير معروف')} (ID: `{agent_id}`)" for agent_id, data in agents.items()])
        
        user_states[chat_id] = {'state': 'waiting_for_agent_id_to_remove'}
        bot.edit_message_text(
            chat_id=chat_id, 
            message_id=call.message.message_id, 
            text=f"🗑️ **بدء إزالة وكيل**\n\nالرجاء إرسال **آيدي** الوكيل المراد حذفه.\n\n**الوكلاء الحاليون:**\n{agent_list}\n\n**تحذير:** لا يمكن التراجع عن هذه العملية.",
            parse_mode="Markdown",
            reply_markup=None
        )
import json
import os
from datetime import datetime, timezone 
# يجب التأكد من تعريف telebot, types, is_admin, is_bot_active, get_main_reply_keyboard, CHANNEL_ID2 في ملفك.

GIFT_FEE_PERCENTAGE = 0.20  # 20% عمولة
MIN_GIFT_AMOUNT = 100       # الحد الأدنى المحدد: 100
user_gift_data = {}         # لتخزين بيانات عملية الإهداء الجارية

# ----------------------------------------------------
# دوال قراءة وكتابة ملف a.json
# ----------------------------------------------------

def load_data_a():
    """تحميل كامل بيانات a.json."""
    if not os.path.exists('a.json'):
        return {}
    try:
        with open('a.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading a.json: {e}")
        return {}

def save_data_a(data):
    """حفظ كامل بيانات a.json."""
    try:
        with open('a.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False) 
    except Exception as e:
        print(f"Error saving a.json: {e}")

def get_user_balance_a(user_id):
    """الحصول على رصيد 'عدادك' من حقل points_to_add مع التحقق الآمن."""
    data = load_data_a()
    user_data = data.get(str(user_id))
    
    if isinstance(user_data, dict):
        try:
            return int(user_data.get('points_to_add', 0))
        except (ValueError, TypeError):
            return 0
    return 0

# ----------------------------------------------------
# دالة بدء عملية الإهداء (Callback Query) - تحقق الـ 100
# ----------------------------------------------------

@bot.callback_query_handler(func=lambda call: call.data == 'gift_counter' and subscription_required_callback(call))
def handle_gift_counter_inline_start(call):
    bot.answer_callback_query(call.id)
    sender_id = str(call.message.chat.id)

    if not is_admin(call.from_user.id) and not is_bot_active(call.message):
        return bot.answer_callback_query(call.id, "❌ البوت متوقف مؤقتاً.")

    current_balance = get_user_balance_a(sender_id)

    # 🛑 هذا هو الشرط الذي يمنع المستخدم من الإهداء إذا كان رصيده أقل من 100
    if not is_admin(sender_id) and current_balance < MIN_GIFT_AMOUNT:
        bot.send_message(call.message.chat.id, 
                         f"❌ لا يمكنك الإرسال إذا كان عدادك أقل من {MIN_GIFT_AMOUNT} (عدادك الحالي: {current_balance}).")
        return # إلغاء العملية
    
    # إذا كان الرصيد 100 فما فوق، يتم الاستمرار.
    user_gift_data[sender_id] = {'target_id': None}
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton('إلغاء الإهداء'))

    bot.send_message(call.message.chat.id,
                     f"📊 عدادك الان: {current_balance}\n✅ أرسل آيدي الشخص الذي تريد إهداءه العداد.",
                     reply_markup=markup)
    bot.register_next_step_handler(call.message, process_target_id_gift)


# ----------------------------------------------------
# دالة استقبال آيدي المستلم
# ----------------------------------------------------

def process_target_id_gift(message):
    sender_id = str(message.chat.id)

    if message.text == 'إلغاء الإهداء':
        user_gift_data.pop(sender_id, None)
        try:
            bot.send_message(message.chat.id, '✅ تم إلغاء عملية الإهداء.', reply_markup=get_main_reply_keyboard())
        except NameError:
            bot.send_message(message.chat.id, '✅ تم إلغاء عملية الإهداء.', reply_markup=types.ReplyKeyboardRemove())
        return

    target_id = message.text.strip()
    if not target_id.isdigit() or target_id == sender_id:
        bot.send_message(message.chat.id, '❌ الآيدي غير صالح. أرسل آيدي صحيح لمستخدم آخر.')
        bot.register_next_step_handler(message, process_target_id_gift)
        return
    
    user_gift_data[sender_id]['target_id'] = target_id
    bot.send_message(message.chat.id, f"✅ تم تحديد المستلم (آيدي: {target_id}).\nأرسل كمية العدادات التي تريد إهداءها (الحد الأدنى {MIN_GIFT_AMOUNT}).", reply_markup=types.ReplyKeyboardRemove())
    bot.register_next_step_handler(message, process_amount_gift)


# ----------------------------------------------------
# دالة استقبال كمية الإهداء وتنفيذ العملية
# ----------------------------------------------------

def process_amount_gift(message):
    sender_id = str(message.chat.id)

    if message.text == 'إلغاء الإهداء':
        user_gift_data.pop(sender_id, None)
        try:
            bot.send_message(message.chat.id, '✅ تم إلغاء عملية الإهداء.', reply_markup=get_main_reply_keyboard())
        except NameError:
            bot.send_message(message.chat.id, '✅ تم إلغاء عملية الإهداء.', reply_markup=types.ReplyKeyboardRemove())
        return

    try:
        amount = int(message.text.strip())
    except Exception:
        bot.send_message(message.chat.id, '❌ يجب إدخال رقم صحيح.')
        bot.register_next_step_handler(message, process_amount_gift)
        return

    data_a = load_data_a()
    sender_balance = get_user_balance_a(sender_id) 
    target_id = user_gift_data.get(sender_id, {}).get('target_id')

    if not target_id:
        bot.send_message(message.chat.id, '❌ لم يتم تحديد المستلم. ابدأ العملية من جديد.')
        user_gift_data.pop(sender_id, None)
        return

    fee = int(amount * GIFT_FEE_PERCENTAGE)
    total = amount + fee

    # التحقق من الحد الأدنى والرصيد (لغير الأدمن)
    if not is_admin(sender_id):
        if amount < MIN_GIFT_AMOUNT:
            bot.send_message(message.chat.id, f"❌ الحد الأدنى للإهداء هو {MIN_GIFT_AMOUNT} عداد.")
            bot.register_next_step_handler(message, process_amount_gift)
            return
        if total > sender_balance:
            bot.send_message(message.chat.id, f"❌ رصيدك غير كافٍ. تحتاج إلى {total} عداد (المبلغ + عمولة {int(GIFT_FEE_PERCENTAGE*100)}%).")
            user_gift_data.pop(sender_id, None)
            return
    
    # حساب الأرصدة الجديدة
    sender_old = sender_balance
    target_old = get_user_balance_a(target_id)
    
    # استثناء الأدمن من الخصم (كما طلبت سابقاً)
    sender_new = sender_balance - total if not is_admin(sender_id) else sender_balance
    
    target_new = target_old + amount
    
    # 🛑 إعداد الوقت الحالي
    current_time_iso = datetime.now(timezone.utc).astimezone().isoformat()
    
    # حماية البيانات والتصحيح التلقائي
    str_sender_id = str(sender_id)
    str_target_id = str(target_id)

    # 1. تحديث رصيد المُهدي (Sender)
    if not isinstance(data_a.get(str_sender_id), dict):
        data_a[str_sender_id] = {}
        
    data_a[str_sender_id]['points_to_add'] = sender_new
    data_a[str_sender_id]['last_added_time'] = current_time_iso

    # 2. تحديث رصيد المستلم (Target)
    if not isinstance(data_a.get(str_target_id), dict):
        data_a[str_target_id] = {}
        
    data_a[str_target_id]['points_to_add'] = target_new
    data_a[str_target_id]['last_added_time'] = current_time_iso
    
    # حفظ البيانات
    save_data_a(data_a)

    sender_name = message.from_user.first_name or 'مستخدم'
    sender_username = message.from_user.username or 'غير متوفر'

    # إرسال رسائل النجاح
    try:
        reply_m = get_main_reply_keyboard()
    except NameError:
        reply_m = types.ReplyKeyboardRemove()
        
    bot.send_message(message.chat.id,
                     f"🎉 تم الإهداء بنجاح!\n\n💸 المبلغ المُرسل: {amount}\n💰 العمولة: {fee}\n💳 عدادك السابق: {sender_old}\n💵 عدادك الجديد: {sender_new}",
                     reply_markup=reply_m)

    # رسالة للمستلم وإشعارات القناة (بدون تغيير)
    try:
        bot.send_message(int(target_id),
                         f"🎁 تم إهداؤك {amount} عداد من {sender_name} (آيدي: {sender_id})!\n\n💰 عدادك السابق: {target_old}\n➕ المبلغ المضاف: {amount}\n💸 عمولة المرسل: {fee}\n💳 عدادك الجديد: {target_new}")
    except Exception:
        pass

    try:
        bot.send_message(CHANNEL_ID2,
                         f"🎁 عملية إهداء عداد:\n👤 المُهدي: {sender_name} (@{sender_username}) [آيدي: {sender_id}]\n🎯 المستلم: [آيدي: {target_id}]\n💸 الكمية: {amount}\n💰 العمولة: {fee}\n💳 عداد المستلم قبل: {target_old}\n💳 بعد: {target_new}", parse_mode='HTML')
    except Exception:
        pass

    user_gift_data.pop(sender_id, None)

##
@bot.callback_query_handler(func=lambda call: call.data == "offer" and subscription_required_callback(call))
def send_offer_item_info(call):
    """معالجة ضغطة زر 'اعرض سلعتك' لإظهار النص والروابط."""

    # ✅ تحقق من حالة البوت — يسمح للأدمن دائمًا
    try:
        user_id = call.from_user.id
        
        if user_id not in ADMIN_ID:
            import json, os
            if os.path.exists("bot_status.json"):
                with open("bot_status.json", "r", encoding="utf-8") as f:
                    status = json.load(f)
                if not status.get("active", True):
                    reason = status.get("reason", "تم إيقاف البوت مؤقتاً")
                    resume_time = status.get("resume_time", "غير محدد")
                    bot.answer_callback_query(call.id, f"❌ البوت متوقف مؤقتاً.\nالسبب: {reason}\nيعود للعمل في: {resume_time}", show_alert=True)
                    return
    except Exception as e:
        print(f"[offer handler check error] {e}")

    # النص الذي سيظهر للمستخدم
    message_text = (
        "🛍️ **اعرض سلعتك الآن بكل حرية!**\n\n"
        "مقابل **500 توب فقط**، احصل على فرصة عرض سلعتك لمدة **24 ساعة كاملة** داخل المنصة ✨\n"
        "بشكل مميز، بدون أي قيود أو شروط — **اجعل الجميع يشاهد منتجك الآن** 🚀"
    )

    # إنشاء الأزرار
    markup = types.InlineKeyboardMarkup()
    channel_link = types.InlineKeyboardButton("📤  القناة", url="https://t.me/Topcash128")
    btn_link = types.InlineKeyboardButton("تواصل معنا 👤", url="https://t.me/hzhzhz8")
    btn_back = types.InlineKeyboardButton("◀ رجوع", callback_data="back_to_main_menu")
    markup.add(channel_link, btn_link)
    markup.add(btn_back)

    try:
        # تعديل رسالة المنيو الحالية بالنص الجديد والأزرار
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=message_text,
            reply_markup=markup,
            parse_mode='Markdown'
        )
    except Exception:
        # في حال فشل التعديل، نرسل رسالة جديدة
        bot.send_message(
            call.message.chat.id,
            text=message_text,
            reply_markup=markup,
            parse_mode='Markdown'
        )

    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda call: call.data == "guarantees")
def guarantees_callback_handler(call):
    """معالجة ضغط زر الضمانات."""
    try:
        send_guarantees_message(call.message.chat.id, call.message.message_id)
        bot.answer_callback_query(call.id)
    except Exception as e:
        print(f"Error handling guarantees: {e}")
def get_guarantees_markup():
    """إنشاء لوحة مفاتيح وزر الرجوع لرسالة الضمانات."""
    markup = types.InlineKeyboardMarkup()
    # يتم افتراض أن زر الضمانات موجود في القائمة الرئيسية (main_menu)، 
    # إذا كانت القائمة السابقة مختلفة، يرجى تغيير callback_data إلى ما يناسبك.
    markup.add(types.InlineKeyboardButton("➡️ رجوع", callback_data="back_to_main_menu")) 
    return markup

def send_guarantees_message(chat_id, message_id):
    """إرسال رسالة شروط وأحكام الضمانات."""
    
    # النص التفصيلي كما طلبته
    guarantees_text = (
        "📑 **شروط وأحكام عقد الاستثمار المضمون – مختصر**\n\n"
        "1️⃣ **مدة العقد:** الاستثمار لمدة سنة واحدة فقط.\n\n"
        "2️⃣ **الضمان:** الإدارة تلتزم بضمان قانوني وإلكتروني لمدة سنة عبر المالك مباشرة.\n\n"
        "3️⃣ **التحويلات المالية:** لا تتجاوز قيمة التحويلات 💸 **10,000 نقطة** خلال فترة العقد، ويجوز زيادتها فقط بموافقة خطية مسبقة من إدارة البوت.\n\n"
        "4️⃣ **نشاط الحساب:** يجب أن يكون الحساب 📲 نشط خلال آخر 45 يوم من توقيع العقد.\n\n"
        "5️⃣ **الأرباح:** تصرف شهريًا 💵 بالدينار أو الدولار 💲 أو تحفظ بالبوت.\n\n"
        "6️⃣ **الالتزامات:** المستثمر لا يطالب بأرباح إضافية خارج العقد، والإدارة غير مسؤولة ⚠️ عن خسائر بسبب مخالفته.\n\n"
        "7️⃣ **المخاطر:** الأرباح غير ثابتة 📉 وتعتمد على نشاط الحساب، مع **ضمان أصل رأس المال فقط**.\n\n"
        "8️⃣ **فسخ العقد:** يمكن لأي طرف فسخ العقد بشرط إشعار مسبق ⏳ قبل 30 يوم.\n\n"
        "9️⃣ **القوانين:** العقد يخضع ⚖️ للقوانين المحلية النافذة.\n\n"
        "🔟 **فائدة الضمان:**\n"
        "في حال حدوث ظروف طارئة 🚨 أو توقف المشروع لأي سبب (مثل مشاكل السيولة 💧، إيقاف النشاط من قبل الجهات الرسمية 🏛️، أو أي عارض خارج عن إرادة الإدارة)، فإن الاستثمار بالضمان يضمن للمستثمر ✅ حقه الاستثماري السنوي وفق الشروط والأحكام المذكورة أعلاه، دون أن يمتد إلى التزامات إضافية خارج إطار العقد.\n\n\n"
        "🔹 **ملاحظة:** هذا العداد يختلف عن العداد العادي. عند شرائك لأول مرة يجب إبلاغ الوكيل بأنك تريد استثمار بالضمان، ليتم تفعيل العداد وتسجيلك في الضمان."
    )
    
    bot.edit_message_text(
        chat_id=chat_id, 
        message_id=message_id, 
        text=guarantees_text, 
        reply_markup=get_guarantees_markup(),
        parse_mode="Markdown"
    )        
@bot.callback_query_handler(func=lambda call: call.data == 'show_agents_list' and subscription_required_callback(call))
def show_agents_list(call):
    user_id = str(call.from_user.id)

    # تخطي الايقاف للادمن
    if not is_bot_active(call.message) and not is_admin(user_id):
        return bot.answer_callback_query(call.id, "❌ البوت متوقف مؤقتاً.")

    agents = load_agents()
    
    if not agents:
        bot.answer_callback_query(call.id, "❌ لا يوجد وكلاء متاحون حالياً.")
        return

    agents_list_markup = types.InlineKeyboardMarkup()

    # إنشاء زر لكل وكيل
    for agent_id, agent_data in agents.items():
        button_text = f"👤 {agent_data['name']} ({agent_data['role']})"
        callback_data = f"agent_details_{agent_id}" 
        agents_list_markup.add(
            types.InlineKeyboardButton(button_text, callback_data=callback_data)
        )
        
    # زر للعودة إلى القائمة الرئيسية
    agents_list_markup.add(
        types.InlineKeyboardButton("🔙 رجوع للقائمة الرئيسية", callback_data="back_to_main_menu")
    )

    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text="👥 **اختر الوكيل الذي تود التواصل معه:**",
        reply_markup=agents_list_markup,
        parse_mode="Markdown"
    )

    
@bot.callback_query_handler(func=lambda call: call.data.startswith('agent_details_'))
def show_agent_details(call):
    # استخلاص آيدي الوكيل من بيانات الزر (مثال: agent_details_1234567890)
    agent_id = call.data.split('_')[2]
    agents = load_agents()
    
    if agent_id in agents:
        agent = agents[agent_id]
        
        # التأكد من وجود الروابط
        account_link = agent.get('account_link', 'https://t.me/NOT_AVAILABLE')
        channel_link = agent.get('channel_link', 'https://t.me/NOT_AVAILABLE')
        
        message_text = (
            f"**معلومات الوكيل: {agent['name']}**\n\n"
            f"**الدور:** {agent['role']}\n"
        )
        
        # إنشاء أزرار روابط مباشرة
        details_markup = types.InlineKeyboardMarkup(row_width=1)
        
        # إضافة زر رابط الحساب
        details_markup.add(
            types.InlineKeyboardButton("📞 التواصل مع الوكيل (حسابه)", url=account_link)
        )
        
        # إضافة زر رابط القناة
        details_markup.add(
            types.InlineKeyboardButton("📺 قناة الوكيل", url=channel_link)
        )
        
        # زر للعودة لقائمة الوكلاء
        details_markup.add(
            types.InlineKeyboardButton("🔙 رجوع لقائمة الوكلاء", callback_data="show_agents_list")
        )
        
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=message_text,
            reply_markup=details_markup,
            parse_mode="Markdown"
        )
    else:
        bot.answer_callback_query(call.id, "❌ لم يتم العثور على معلومات هذا الوكيل.")    
##
@bot.message_handler(func=lambda message: message.text == "انشاء كوبون" and message.chat.id == ADMIN_ID)
def start_create_coupon(message):
    """بدء عملية إنشاء الكوبون وطلب الرمز."""
    global coupon_temp_data
    if message.chat.id in coupon_temp_data:
        del coupon_temp_data[message.chat.id]
        
    msg = bot.send_message(message.chat.id, "⬇️ **لإنشاء كوبون جديد (الخطوة 1/4):**\nالرجاء إرسال **رمز الكوبون** (مثال: SALE2024).", parse_mode="Markdown")
    bot.register_next_step_handler(msg, get_coupon_code)

def get_coupon_code(message):
    """الخطوة 2/4: استلام رمز الكوبون وطلب عدد النقاط."""
    global coupon_temp_data
    admin_id = message.chat.id
    code = message.text.strip()
        
    try:
        if code in load_coupons(): 
            msg = bot.send_message(admin_id, "❌ هذا الرمز موجود بالفعل. الرجاء إرسال **رمز كوبون** جديد.")
            bot.register_next_step_handler(msg, get_coupon_code)
            return
    except NameError:
         return bot.send_message(admin_id, "❌ خطأ داخلي: دالة load_coupons غير موجودة.")
        
    coupon_temp_data[admin_id] = {'code': code}
    
    msg = bot.send_message(admin_id, f"✅ تم حفظ الرمز: **{code}**.\n\n**الخطوة 2/4:** كم هي **عدد النقاط** التي يمنحها الكوبون؟", parse_mode="Markdown")
    bot.register_next_step_handler(msg, get_coupon_points)

def get_coupon_points(message):
    """الخطوة 3/4: استلام عدد النقاط وطلب الحد الأقصى للاستخدام."""
    global coupon_temp_data
    admin_id = message.chat.id
    
    if admin_id not in coupon_temp_data:
        bot.send_message(admin_id, "❌ خطأ في العملية. الرجاء البدء من جديد.")
        return
        
    try:
        points = int(message.text.strip())
        if points <= 0: raise ValueError
    except ValueError:
        msg = bot.send_message(admin_id, "❌ عدد النقاط يجب أن يكون رقماً صحيحاً وموجباً. حاول مرة أخرى.")
        bot.register_next_step_handler(msg, get_coupon_points)
        return
        
    coupon_temp_data[admin_id]['points'] = points
    
    msg = bot.send_message(admin_id, f"✅ تم حفظ النقاط: {points}.\n\n**الخطوة 3/4:** كم هو **الحد الأقصى لعدد المستخدمين** الذين يمكنهم استخدام الكوبون؟", parse_mode="Markdown")
    bot.register_next_step_handler(msg, get_coupon_max_uses)

def get_coupon_max_uses(message):
    """الخطوة 4/4: استلام الحد الأقصى للاستخدام وطلب مدة الانتهاء."""
    global coupon_temp_data
    admin_id = message.chat.id
    
    if admin_id not in coupon_temp_data:
        bot.send_message(admin_id, "❌ خطأ في العملية. الرجاء البدء من جديد.")
        return

    try:
        max_uses = int(message.text.strip())
        if max_uses <= 0: raise ValueError
    except ValueError:
        msg = bot.send_message(admin_id, "❌ الحد الأقصى يجب أن يكون رقماً صحيحاً وموجباً. حاول مرة أخرى.")
        bot.register_next_step_handler(msg, get_coupon_max_uses)
        return
        
    coupon_temp_data[admin_id]['max_uses'] = max_uses
    
    msg = bot.send_message(admin_id, f"✅ تم حفظ الحد الأقصى: {max_uses}.\n\n**الخطوة الأخيرة:** كم هي **مدة صلاحية الكوبون**؟\n(مثال: **7d** لـ 7 أيام، أو **48h** لـ 48 ساعة).\nإذا لم ترد تعيين مدة، أرسل 0.", parse_mode="Markdown")
    bot.register_next_step_handler(msg, get_coupon_expiry)

def get_coupon_expiry(message):
    """معالجة مدة الانتهاء وإتمام إنشاء الكوبون."""
    global coupon_temp_data
    admin_id = message.chat.id
    
    if admin_id not in coupon_temp_data:
        bot.send_message(admin_id, "❌ خطأ في العملية. الرجاء البدء من جديد.")
        return

    expiry_input = message.text.strip().lower()
    expires_at = None
    
    try:
        if expiry_input == '0':
            expires_at = "لا يوجد"
        else:
            unit = expiry_input[-1] 
            value = int(expiry_input[:-1]) 
            
            if unit == 'd':
                delta = timedelta(days=value)
            elif unit == 'h':
                delta = timedelta(hours=value)
            else:
                raise ValueError("الوحدة غير صالحة.")

            now = datetime.now(timezone.utc)
            expiry_datetime = now + delta
            expires_at = expiry_datetime.strftime("%Y-%m-%d %H:%M:%S UTC")

    except ValueError as ve:
        msg = bot.send_message(admin_id, f"❌ صيغة المدة غير صحيحة ({str(ve)}). يجب أن تكون: [رقم]d أو [رقم]h. حاول مرة أخرى.", parse_mode="Markdown")
        bot.register_next_step_handler(msg, get_coupon_expiry)
        return
    except Exception as e:
        msg = bot.send_message(admin_id, f"❌ حدث خطأ غير متوقع في معالجة المدة ({str(e)}). حاول مرة أخرى.")
        bot.register_next_step_handler(msg, get_coupon_expiry)
        return

    finalize_coupon(admin_id, expires_at)

def finalize_coupon(admin_id, expires_at):
    """حفظ الكوبون في ملف الكوبونات وإضافة زر النشر."""
    global coupon_temp_data
    
    if admin_id not in coupon_temp_data:
        bot.send_message(admin_id, "❌ خطأ داخلي: بيانات العملية غير متوفرة لإتمام الحفظ.")
        return
        
    data = coupon_temp_data[admin_id]
    code = data['code']
    
    try:
        coupons = load_coupons()
    except NameError:
        return bot.send_message(admin_id, "❌ خطأ: دالة load_coupons غير موجودة.")
        
    coupons[code] = {
        "points": data['points'],
        "max_uses": data['max_uses'],
        "expires_at": expires_at,
        "used_by": []
    }
    
    try:
        save_coupons(coupons)
    except NameError:
        return bot.send_message(admin_id, "❌ خطأ: دالة save_coupons غير موجودة. لم يتم حفظ الكوبون.")
    
    coupon_message_html = f"""
    🎁 <b>كوبون جديد متاح الآن!</b> 🎁
    
    💰 <b>النقاط:</b> <code>{data['points']:,}</code> نقطة
    🏷️ <b>الرمز:</b> <code>{code}</code>
    
    🔄 <b>الحد الأقصى للاستخدام:</b> {data['max_uses']} مرات
    🗓️ <b>تاريخ الانتهاء:</b> {expires_at}
    
    """
    
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("📢 نشر الكوبون في القناة", callback_data=f"publish_coupon_{code}")
    )
    
    bot.send_message(admin_id, 
                     f"✅ **تم إنشاء الكوبون بنجاح**.\n\n"
                     f"**الرمز:** `{code}`\n"
                     f"**النقاط:** {data['points']}\n"
                     f"**الحد الأقصى للاستخدام:** {data['max_uses']} مرات\n"
                     f"**تاريخ الانتهاء:** {expires_at}",
                     reply_markup=markup,
                     parse_mode="Markdown")
                     
    coupon_temp_data[admin_id]['publish_message'] = coupon_message_html
@bot.callback_query_handler(func=lambda call: call.data.startswith('publish_coupon_'))
def publish_coupon_handler(call):
    admin_id = call.from_user.id
    
    if admin_id != ADMIN_ID:
        bot.answer_callback_query(call.id, "❌ هذا الزر مخصص للأدمن فقط.", show_alert=True)
        return

    code = call.data.split('_')[2]
    
    if admin_id not in coupon_temp_data or coupon_temp_data[admin_id].get('code') != code:
        bot.edit_message_text("❌ انتهت صلاحية النشر أو حدث خطأ.", call.message.chat.id, call.message.message_id)
        bot.answer_callback_query(call.id, "فشل النشر.")
        return

    coupon_msg_to_publish = coupon_temp_data[admin_id]['publish_message']
    
    try:
        bot.send_message(CHANNEL_ID4, coupon_msg_to_publish, parse_mode='HTML') 
        
        bot.edit_message_text(f"✅ تم نشر الكوبون <b>{code}</b> بنجاح في القناة.", 
                              call.message.chat.id, 
                              call.message.message_id, 
                              parse_mode='HTML')
        bot.answer_callback_query(call.id, "تم النشر بنجاح.")
        
    except Exception as e:
        bot.edit_message_text(f"❌ فشل النشر في القناة. تأكد من أن البوت مسؤول في القناة وأن <code>CHANNEL_ID4</code> صحيح.\nالخطأ: {str(e)}", 
                              call.message.chat.id, 
                              call.message.message_id, 
                              parse_mode='HTML')
        bot.answer_callback_query(call.id, "فشل النشر!", show_alert=True)
        
    finally:
        if admin_id in coupon_temp_data:
            del coupon_temp_data[admin_id]
# ***************************************************************
# --- معالج الرجوع للقائمة الرئيسية (إرسال /start جديد) ---
@bot.callback_query_handler(func=lambda call: call.data == "back_to_main_menu")
def back_to_main_menu_handler(call):
    # 1. إظهار إشعار سريع للمستخدم
    bot.answer_callback_query(call.id, "رجوع للقائمة الرئيسية...")
    
    # 2. حذف الرسالة التي تحتوي على الزر الحالي
    try:
        bot.delete_message(call.message.chat.id, call.message.message_id)
    except Exception as e:
        # إذا فشل الحذف، نتجاهل الخطأ ونستمر بالإرسال
        pass 

    # 3. محاكاة أمر /start باستخدام دالة start الأصلية
    
    # إنشاء كائن رسالة مؤقت (Temporary Message Object)
    class TempMessage:
        def __init__(self, chat_id, from_user):
            self.chat = types.Chat(chat_id, 'private')
            self.from_user = from_user
            self.text = '/start' # النص الذي سيتم قراءته في دالة start

    temp_message = TempMessage(call.message.chat.id, call.from_user)
    
    # استدعاء دالة start الأصلية الخاصة بك
    start(temp_message)
# روابط المتاجر الخارجية (تبقى كما هي)
STORE_LINKS = {
    "alsiraj": {"label": "مكتبة السراج", "url": "https://t.me/S_OOOCI"},
    "alqimma": {"label": "متجر القمة", "url": "https://t.me/u_tto"},
    "bano": {"label": "متجر بانو", "url": "https://t.me/cozmatik10"},
    "zahraa": {"label": "مركز الزهراء للهواتف النقالة", "url": "https://t.me/Topcash110"},
    "wldan": {"label": "مكتبة ولدان القرطاسية", "url": "https://t.me/Topcash112"}
}

# تحديث الحقول المطلوبة (يُضاف إلى قاموس FIELD_PROMPTS)
FIELD_PROMPTSS = { # استبدل القاموس القديم بهذا أو قم بتحديثه
    "telegram_username": "الرجاء إرسال **يوزر حسابك في تلجرام (@username)** لشراء الخدمة:",
    "telegram_user_or_link": "الرجاء إرسال **يوزر حسابك (@username) أو رابط المنشور** لشراء الخدمة:",
    "game_id": "الرجاء إرسال **آيدي حسابك في اللعبة (Player ID)** لشحن الشدات:",
    "game_name": "الرجاء إرسال **اسم حسابك في اللعبة (In-Game Name)**:",
    # ... (قد يحتوي على حقول أخرى مثل "amount" أو "payment_method")
}
# --- 1. قائمة المتجر الرئيسية (المتجر الالكتروني) ---
@bot.callback_query_handler(func=lambda call: call.data == "shop_menu" and subscription_required_callback(call))
def shop_menu_callback(call):
    sender_id = str(call.from_user.id)

    # تخطي الايقاف للادمن
    if not is_bot_active(call.message) and not is_admin(sender_id):
        return bot.answer_callback_query(call.id, "❌ البوت متوقف مؤقتاً.")
    
    markup = types.InlineKeyboardMarkup(row_width=1)
    
    markup.add(types.InlineKeyboardButton("خدمات تلجرام", callback_data="shop_category:telegram"))
    markup.add(types.InlineKeyboardButton("شحن العاب", callback_data="shop_category:games"))
    markup.add(types.InlineKeyboardButton("المتاجر (روابط خارجية)", callback_data="shop_stores"))
    
    markup.add(types.InlineKeyboardButton("⬅️ رجوع للقائمة الرئيسية", callback_data="back_to_main_menu"))
    
    bot.edit_message_text(chat_id=call.message.chat.id, 
                          message_id=call.message.message_id,
                          text="🛒 **المتجر الإلكتروني**\n\nاختر فئة المنتجات:", 
                          reply_markup=markup,
                          parse_mode='Markdown')
    bot.answer_callback_query(call.id)



# --- 2. قوائم الفئات (خدمات تلجرام، شحن العاب) ---
@bot.callback_query_handler(func=lambda call: call.data.startswith("shop_category:"))
def shop_category_callback(call):
    category = call.data.split(":")[1]
    user_id = str(call.from_user.id)
    users = load_users()
    u = users.get(user_id, {})
    
    markup = types.InlineKeyboardMarkup(row_width=1)
    
    for key, item in STORE_PRODUCTS.items():
        if item["category"] == category:
            # هنا يتم تمرير SHOP_ADMIN_ID دائمًا
            callback_data = f"buy_item:{key}:{item['cost']}:{item['admin_id']}"
            markup.add(types.InlineKeyboardButton(f"{item['label']} بسعر {item['cost']} نقطة", callback_data=callback_data))

    markup.add(types.InlineKeyboardButton("⬅️ رجوع لقائمة المتجر", callback_data="shop_menu"))
    
    category_name = "خدمات تلجرام" if category == "telegram" else "شحن الألعاب"
    
    bot.edit_message_text(chat_id=call.message.chat.id, 
                          message_id=call.message.message_id,
                          text=f"رصيدك الحالي: {u.get('points', 0)} نقطة.\n\nاختر من قائمة **{category_name}**:", 
                          reply_markup=markup,
                          parse_mode='Markdown')
    bot.answer_callback_query(call.id)

# --- 3. قائمة المتاجر الخارجية (روابط) ---
@bot.callback_query_handler(func=lambda call: call.data == "shop_stores")
def shop_stores_callback(call):
    markup = types.InlineKeyboardMarkup(row_width=1)
    
    for store_key, store_info in STORE_LINKS.items():
        markup.add(types.InlineKeyboardButton(store_info["label"], url=store_info["url"]))

    markup.add(types.InlineKeyboardButton("⬅️ رجوع لقائمة المتجر", callback_data="shop_menu"))
    
    bot.edit_message_text(chat_id=call.message.chat.id, 
                          message_id=call.message.message_id,
                          text="🛍️ **المتاجر**\n\nاضغط على الزر للانتقال إلى المتجر الخارجي:", 
                          reply_markup=markup,
                          parse_mode='Markdown')
    bot.answer_callback_query(call.id)
# --- 4. بدء عملية الشراء (التحقق من الرصيد) ---
@bot.callback_query_handler(func=lambda call: call.data.startswith("buy_item:"))
def start_purchase_process(call):
    user_id = str(call.from_user.id)
    users = load_users()
    u = users.get(user_id, {})
    global user_purchase_data
    
    try:
        _, item_key, cost_str, admin_target = call.data.split(":")
        cost = int(cost_str)
    except ValueError:
        return bot.answer_callback_query(call.id, "❌ خطأ في تحليل بيانات الشراء.")

    if item_key not in STORE_PRODUCTS:
        return bot.answer_callback_query(call.id, "❌ المنتج غير متوفر حالياً.")
    
    item = STORE_PRODUCTS[item_key]

    if u.get("points", 0) < cost:
        return bot.answer_callback_query(call.id, f"❌ رصيدك ({u.get('points',0)} نقطة) غير كافٍ لشراء {item['label']} ({cost} نقطة).")
    
    # تم توحيد الآيدي إلى SHOP_ADMIN_ID
    actual_admin_id = SHOP_ADMIN_ID 

    user_purchase_data[user_id] = {
        "item_key": item_key,
        "item_label": item["label"],
        "cost": cost,
        "fields_required": item["fields"],
        "fields_collected": {},
        "current_field_index": 0,
        "admin_id": actual_admin_id
    }
    
    bot.answer_callback_query(call.id, f"بدء شراء {item['label']}.")
    
    first_field = item["fields"][0]
    prompt = FIELD_PROMPTSS.get(first_field, "أدخل البيانات المطلوبة:")
    msg = bot.send_message(call.message.chat.id, prompt, parse_mode="Markdown")
    
    bot.register_next_step_handler(msg, collect_purchase_field)

# --- 5. دالة تجميع الحقول بالتتابع ---
def collect_purchase_field(message):
    user_id = str(message.from_user.id)
    global user_purchase_data
    
    if user_id not in user_purchase_data:
        bot.send_message(message.chat.id, "❌ انتهت صلاحية الطلب أو لم يبدأ بشكل صحيح. ابدأ من قائمة المتجر.")
        return
        
    tp = user_purchase_data[user_id]
    idx = tp.get("current_field_index", 0)
    fields = tp.get("fields_required", [])
    
    if idx < len(fields):
        field_name = fields[idx]
        tp['fields_collected'][field_name] = message.text.strip()
        tp['current_field_index'] = idx + 1
        
    if tp['current_field_index'] < len(fields):
        next_field = fields[tp['current_field_index']]
        prompt = FIELD_PROMPTSS.get(next_field, "أدخل البيانات المطلوبة:")
        msg = bot.send_message(message.chat.id, prompt, parse_mode="Markdown")
        bot.register_next_step_handler(msg, collect_purchase_field)
        return
        
    item_label = tp.get("item_label", "منتج")
    cost = tp.get("cost", 0)
    collected = tp.get("fields_collected", {})
    
    fields_summary = ""
    for k, v in collected.items():
        field_prompt = FIELD_PROMPTSS.get(k, k).split(':')[0] 
        fields_summary += f"\n• {field_prompt}: **{v}**"
        
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(types.InlineKeyboardButton("✅ تأكيد وإرسال الطلب", callback_data="confirm_final_purchase"),
               types.InlineKeyboardButton("❌ إلغاء", callback_data="cancel_purchase_confirm"))
               
    bot.send_message(message.chat.id,
                     f"**تأكيد طلب الشراء**\n\nالمنتج: {item_label}\nالنقاط المطلوب خصمها: {cost}\nالتفاصيل:{fields_summary}\n\nاضغط ✅ للتأكيد، وسيتم **إرسال الطلب للمشرف** بانتظار موافقته.",
                     parse_mode="Markdown", reply_markup=markup)

# --- 6. الإلغاء ---
@bot.callback_query_handler(func=lambda call: call.data == "cancel_purchase_confirm")
def cancel_purchase_confirm_callback(call):
    user_id = str(call.from_user.id)
    global user_purchase_data
    
    if user_id in user_purchase_data:
        del user_purchase_data[user_id]
        
    bot.edit_message_text("❌ تم إلغاء عملية الشراء. لم يتم خصم أي نقاط.", call.message.chat.id, call.message.message_id)
    bot.answer_callback_query(call.id, "تم إلغاء الطلب.")

# --- 7. التأكيد النهائي (إرسال الطلب للمشرف) ---
@bot.callback_query_handler(func=lambda call: call.data == "confirm_final_purchase")
def submit_purchase_request(call):
    user_id = str(call.from_user.id)
    global user_purchase_data
    global pending_purchase_requests
    users = load_users()
    
    if user_id not in user_purchase_data:
        return bot.answer_callback_query(call.id, "❌ انتهت صلاحية الطلب. ابدأ من جديد.")
        
    u = users.get(user_id, {})
    tp = user_purchase_data[user_id]
    cost = tp.get("cost", 0)
    
    if u.get("points", 0) < cost:
        del user_purchase_data[user_id]
        return bot.answer_callback_query(call.id, "❌ رصيدك غير كافٍ. تم إلغاء الطلب.")

    request_id = str(int(time.time() * 1000)) 
    
    request_data = {
        "user_id": user_id,
        "item_label": tp["item_label"],
        "cost": cost,
        "details": tp["fields_collected"],
        "admin_id": SHOP_ADMIN_ID,
        "request_time": datetime.now().strftime('%Y-%m-%d | %H:%M:%S') 
    }
    pending_purchase_requests[request_id] = request_data
    
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, 
                          text=f"✅ **تم إرسال طلبك بنجاح!**\n\nتم إرسال طلب شراء **{tp['item_label']}** بقيمة **{cost}** نقطة.\nسيتم مراجعته والموافقة عليه من قبل المشرف قريباً.\nرقم الطلب: <code>{request_id}</code>.", 
                          parse_mode="HTML")
    bot.answer_callback_query(call.id, "تم إرسال الطلب بانتظار الموافقة.")
    
    admin_id_target = SHOP_ADMIN_ID
    collected_details = tp["fields_collected"]
    
    details_text = ""
    for k, v in collected_details.items():
        field_prompt = FIELD_PROMPTSS.get(k, k).split(':')[0].replace('الرجاء إرسال ', '') 
        details_text += f"\n• {field_prompt}: **{v}**"
        
    admin_msg = (
        f"💰 **طلب شراء جديد من المتجر الإلكتروني (بانتظار الموافقة)** 💰\n\n"
        f"**رقم الطلب:** <code>{request_id}</code>\n"
        f"**المنتج:** {tp['item_label']}\n"
        f"**النقاط المطلوبة:** {cost}\n"
        f"**المشتري:** <code>{user_id}</code> - {u.get('name', 'مستخدم')} (@{u.get('username', 'لا يوجد')})\n"
        f"**التفاصيل المطلوبة:{details_text}"
    )

    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("✅ موافقة وخصم النقاط", callback_data=f"purchase_approve:{request_id}"),
        types.InlineKeyboardButton("❌ رفض الطلب (مع السبب)", callback_data=f"purchase_reject_ask:{request_id}")
    )
    
    try:
        bot.send_message(admin_id_target, admin_msg, parse_mode="HTML", reply_markup=markup)
    except Exception as e:
        bot.send_message(ADMIN_ID, f"⚠️ فشل إرسال إشعار الشراء ({tp['item_label']}) إلى المشرف: {admin_id_target}. (الخطأ: {e})", parse_mode="HTML")
        
    del user_purchase_data[user_id]


# --- 8. معالجات المشرف لطلبات الشراء (محدثة) ---
@bot.callback_query_handler(func=lambda call: call.data.startswith("purchase_approve:") or call.data.startswith("purchase_reject_ask:"))
def purchase_admin_handler(call):
    admin_id = str(call.from_user.id)
    
    # التحقق من أن المستخدم ضاغط الزر هو المشرف المسموح له (ADMIN_ID هو المشرف العام و SHOP_ADMIN_ID هو مشرف المتجر)
    allowed_admins = [str(ADMIN_ID), str(SHOP_ADMIN_ID)]
    if admin_id not in allowed_admins: 
        return bot.answer_callback_query(call.id, "❌ ليس لديك صلاحية للقيام بهذا الإجراء.")
        
    global pending_purchase_requests
    global user_rejection_data
    
    action, request_id = call.data.split(":")
    
    if request_id not in pending_purchase_requests:
        return bot.edit_message_text("❌ انتهت صلاحية هذا الطلب أو تم التعامل معه مسبقاً.", call.message.chat.id, call.message.message_id)

    request_data = pending_purchase_requests[request_id]
    user_id = request_data["user_id"]
    cost = request_data["cost"]
    item_label = request_data["item_label"]
    admin_name = call.from_user.first_name
    users = load_users()
    u = users.get(user_id, {})

    if action == "purchase_approve":
        if u.get("points", 0) < cost:
            bot.send_message(call.message.chat.id, f"⚠️ لا يمكن الموافقة. رصيد المستخدم <code>{user_id}</code> غير كافٍ ({u.get('points', 0)} نقطة).", parse_mode="HTML")
            bot.edit_message_text(call.message.text + f"\n\n**⚠️ فشل الخصم:** رصيد غير كافٍ.", call.message.chat.id, call.message.message_id, parse_mode="HTML")
            del pending_purchase_requests[request_id]
            return
            
        # 1. خصم النقاط
        users[user_id]['points'] -= cost
        users[user_id]['purchases'] = users[user_id].get('purchases', 0) + 1 
        save_users(users)
        
        # 2. إشعار المستخدم بالموافقة
        try:
            bot.send_message(user_id, f"✅ **تمت الموافقة على طلب الشراء!**\n\nوافق المشرف **{admin_name}** على طلبك لشراء **{item_label}**.\nتم خصم **{cost}** نقطة من رصيدك.\nرصيدك الحالي: {users[user_id]['points']} نقطة.\nسيتم تزويدك بالخدمة/الشحن قريباً.", parse_mode="Markdown")
        except:
             pass 

        # 3. نشر العملية في القناة المخصصة للمتجر
        try:
            bot.send_message(CHANNEL_ID3, 
                             f"🥳 **عملية شراء جديدة ناجحة!**\n\n**المنتج:** {item_label}\n**النقاط المخصومة:** {cost}\n**المشتري:** <code>{user_id}</code>\n\n**بواسطة المشرف:** {admin_name}", 
                             parse_mode="HTML")
        except Exception as e:
            bot.send_message(ADMIN_ID, f"⚠️ فشل نشر عملية الشراء في قناة المتجر. (الخطأ: {e})", parse_mode="HTML")

        # 4. تحديث رسالة المشرف
        bot.edit_message_text(call.message.text + f"\n\n**✅ تمت الموافقة والخصم**\nتم الخصم بنجاح من رصيد المستخدم.\nالمشرف: {admin_name}", call.message.chat.id, call.message.message_id, parse_mode="HTML")

        # 5. مسح الطلب المعلق
        del pending_purchase_requests[request_id]
        
    elif action == "purchase_reject_ask":
        # 1. طلب السبب من المشرف
        user_rejection_data[admin_id] = {"request_id": request_id, "message_id": call.message.message_id}
        
        # إنشاء زر إلغاء عملية الرفض
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("إلغاء عملية الرفض", callback_data="cancel_admin_action"))
        
        # سنعدل الرسالة الأصلية لطلب السبب لتجنب فقدان السياق
        bot.edit_message_text(call.message.text + "\n\n**❌ الرجاء إرسال سبب رفض طلب الشراء للمستخدم في رسالة منفصلة:**", call.message.chat.id, call.message.message_id, reply_markup=markup, parse_mode="HTML")
        
        # وننتظر الخطوة التالية
        bot.register_next_step_handler(call.message, process_purchase_rejection)
        bot.answer_callback_query(call.id, "الرجاء إدخال السبب في رسالة جديدة.")
        return # لا نمسح الطلب المعلق هنا

    bot.answer_callback_query(call.id, f"تم التعامل مع الطلب بنجاح ({'موافقة' if action == 'purchase_approve' else 'رفض'}).")

# --- 9. معالجة سبب الرفض (جديد) ---
def process_purchase_rejection(message):
    admin_id = str(message.from_user.id)
    global user_rejection_data
    global pending_purchase_requests
    
    if admin_id not in user_rejection_data:
        bot.send_message(message.chat.id, "❌ انتهت صلاحية إدخال سبب الرفض أو لم تبدأ عملية الرفض.")
        return

    data = user_rejection_data[admin_id]
    request_id = data["request_id"]
    original_message_id = data["message_id"]

    if request_id not in pending_purchase_requests:
        bot.send_message(message.chat.id, "❌ الطلب الأصلي غير موجود أو تمت معالجته بالفعل.")
        del user_rejection_data[admin_id]
        return
        
    request_data = pending_purchase_requests[request_id]
    user_id = request_data["user_id"]
    item_label = request_data["item_label"]
    admin_name = message.from_user.first_name
    rejection_reason = message.text.strip()

    # 1. إشعار المستخدم بالرفض وسبب الرفض
    try:
        bot.send_message(user_id, 
                         f"❌ **تم رفض طلب الشراء!**\n\nنأسف، رفض المشرف **{admin_name}** طلبك لشراء **{item_label}**.\n**سبب الرفض:** {rejection_reason}\n\nلم يتم خصم أي نقاط من رصيدك.", 
                         parse_mode="Markdown")
    except:
         bot.send_message(admin_id, f"⚠️ فشل إرسال إشعار الرفض للمستخدم <code>{user_id}</code>.", parse_mode="HTML")
         
    # 2. تحديث رسالة المشرف الأصلية (بإضافة حالة الرفض والسبب)
    try:
        bot.edit_message_text(f"**❌ تم الرفض**\n**المنتج:** {item_label}\n**للمستخدم:** <code>{user_id}</code>\n**المشرف:** {admin_name}\n**السبب المُرسَل:** {rejection_reason}", 
                              message.chat.id, original_message_id, parse_mode="HTML", reply_markup=None)
    except:
         bot.send_message(admin_id, f"⚠️ فشل تحديث رسالة المشرف الأصلية رقم {original_message_id}.", parse_mode="HTML")

    bot.send_message(admin_id, f"✅ تم إرسال سبب الرفض للمستخدم <code>{user_id}</code>.", parse_mode="HTML")
    
    # 3. مسح الطلب المعلق وبيانات الرفض
    del pending_purchase_requests[request_id]
    del user_rejection_data[admin_id]
    
# --- 10. إلغاء عملية إدخال السبب ---
@bot.callback_query_handler(func=lambda call: call.data == "cancel_admin_action")
def cancel_admin_action_callback(call):
    admin_id = str(call.from_user.id)
    global user_rejection_data
    
    if admin_id in user_rejection_data:
        # نستعيد الرسالة الأصلية قبل طلب السبب
        original_message_id = user_rejection_data[admin_id]["message_id"]
        
        # إعادة الرسالة الأصلية إلى حالتها قبل طلب السبب (مع أزرار الموافقة/الرفض)
        request_id = user_rejection_data[admin_id]["request_id"]
        
        markup = types.InlineKeyboardMarkup(row_width=2)
        markup.add(
            types.InlineKeyboardButton("✅ موافقة وخصم النقاط", callback_data=f"purchase_approve:{request_id}"),
            types.InlineKeyboardButton("❌ رفض الطلب (مع السبب)", callback_data=f"purchase_reject_ask:{request_id}")
        )
        
        # تحديث الرسالة الأصلية وإزالة طلب السبب
        try:
             # نفترض أن النص الأصلي ما زال متاحاً في الرسالة قبل التعديل لطلب السبب
             bot.edit_message_text(call.message.text.replace("\n\n**❌ الرجاء إرسال سبب رفض طلب الشراء للمستخدم في رسالة منفصلة:**", ""), 
                                   call.message.chat.id, original_message_id, reply_markup=markup, parse_mode="HTML")
        except:
             # إذا فشل التحديث (ربما تم تعديل النص الأصلي بالكامل)، نرسل رسالة جديدة
             bot.send_message(call.message.chat.id, "✅ تم إلغاء عملية الرفض. يرجى البحث عن الرسالة الأصلية.", reply_markup=markup)
             
        del user_rejection_data[admin_id]
        bot.answer_callback_query(call.id, "تم الإلغاء بنجاح.")
    else:
        bot.answer_callback_query(call.id, "لا توجد عملية رفض قيد التنفيذ للإلغاء.")

####
# ملاحظة: يجب أن تكون user_transfer_data معرفة كـ global dict في بداية ملفك (موجودة في ملفاتك المرفقة).
@bot.callback_query_handler(func=lambda call: call.data == "cancel_transfer")
def cancel_transfer_process(call):
    user_id = str(call.from_user.id)
    
    # 1. إزالة البيانات المؤقتة لضمان إنهاء العملية
    if user_id in user_transfer_data:
        del user_transfer_data[user_id]
        
    # 2. تعديل الرسالة لإبلاغ المستخدم بالإلغاء
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text="❌ **تم إلغاء عملية تحويل النقاط.**\n\n يمكنك بدء عملية جديدة من القائمة الرئيسية.",
        parse_mode='Markdown'
    )
    # 3. إزالة المعالج التالي المسجل (مهم جداً لإنهاء العملية)
    bot.clear_step_handler_by_chat_id(call.message.chat.id)
    bot.answer_callback_query(call.id, "تم إلغاء العملية.")
@bot.callback_query_handler(func=lambda call: call.data == "transfer_points_inline" and subscription_required_callback(call))
def start_transfer_points(call):
    user_id = str(call.from_user.id)

    # تخطي الايقاف للادمن
    if not is_bot_active(call.message) and not is_admin(user_id):
        return bot.answer_callback_query(call.id, "❌ البوت متوقف مؤقتاً.")
    
    # 1. إنشاء زر الإلغاء (Inline Keyboard)
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("❌ إلغاء العملية والرجوع", callback_data="cancel_transfer"))
    
    # 2. إرسال رسالة طلب المبلغ وبدء تسلسل المحادثة
    msg = bot.send_message(
        call.message.chat.id, 
        "🏦 **بدء عملية تحويل النقاط:**\n\n"
        "يرجى إرسال **المبلغ** الذي تود تحويله (أرقام صحيحة).\n"
        f"**ملاحظة:** يتم استقطاع عمولة ثابتة قدرها **{TRANSFER_FEE}** نقطة من رصيدك عند إتمام التحويل.",
        parse_mode='Markdown',
        reply_markup=markup
    )
    
    # تعيين الدالة التالية للمعالجة وتخزين المبلغ
    bot.register_next_step_handler(msg, process_transfer_amount)
    
    # الإجابة على الاستعلام CallbackQuery
    bot.answer_callback_query(call.id)

# ----------------------------------------------------
# 2. معالج استلام المبلغ (تم تحسين التحقق)
# ----------------------------------------------------
def process_transfer_amount(message):
    user_id = str(message.chat.id)
    global user_transfer_data 
    users = load_users()
    
    # التحقق من أن المبلغ رقم صحيح وموجب
    try:
        amount = int(message.text.strip())
        if amount <= 0:
            bot.send_message(user_id, "❌ **خطأ:** يرجى إدخال مبلغ موجب.")
            return # إنهاء العملية
    except ValueError:
        msg = bot.send_message(user_id, "❌ **خطأ:** يرجى إدخال مبلغ صحيح (أرقام فقط).")
        bot.register_next_step_handler(msg, process_transfer_amount)
        return

    # التحقق من أن الرصيد كافٍ (المبلغ + العمولة)
    required_points = amount + TRANSFER_FEE
    current_points = users.get(user_id, {}).get('points', 0)
    
    if current_points < required_points:
        bot.send_message(user_id, 
                         f"❌ **فشل التحويل:** رصيدك الحالي هو **{current_points}** نقطة.\n"
                         f"المجموع المطلوب للتحويل: **{required_points}** نقطة (شامل العمولة). الرصيد غير كافٍ.")
        return # إنهاء العملية

    # حفظ المبلغ وبدء طلب الآيدي
    user_transfer_data[user_id] = {'amount': amount}
    msg = bot.send_message(user_id, 
                           "✅ المبلغ مقبول. يرجى الآن إرسال **آيدي المستخدم** (ID) الذي تريد التحويل إليه. (أرقام فقط)")
    bot.register_next_step_handler(msg, process_target_id)

# ----------------------------------------------------
# 3. معالج استلام الآيدي وتأكيد التحويل (تم تحسين التحقق)
# ----------------------------------------------------
def process_target_id(message):
    sender_id = str(message.chat.id)
    
    # تحقق من أن المستخدم بدأ التسلسل
    if sender_id not in user_transfer_data:
        bot.send_message(sender_id, "❌ **خطأ:** يرجى إعادة بدء عملية التحويل من القائمة الرئيسية.")
        return

    target_id = message.text.strip()
    
    # التحقق من أن الآيدي رقم صحيح
    if not target_id.isdigit():
        msg = bot.send_message(sender_id, "❌ **خطأ:** يجب أن يكون آيدي المستلم أرقاماً فقط.")
        bot.register_next_step_handler(msg, process_target_id)
        return
        
    # منع التحويل للنفس
    if target_id == sender_id:
        bot.send_message(sender_id, "❌ **خطأ:** لا يمكنك التحويل إلى حسابك الشخصي.")
        # مسح البيانات المؤقتة لإنهاء العملية
        if sender_id in user_transfer_data: del user_transfer_data[sender_id]
        return
        
    users = load_users()
    
    # التحقق من وجود المستلم
    if target_id not in users:
        bot.send_message(sender_id, f"❌ **فشل:** لم يتم العثور على مستخدم بالآيدي **{target_id}** في قاعدة البيانات.")
        # مسح البيانات المؤقتة لإنهاء العملية
        if sender_id in user_transfer_data: del user_transfer_data[sender_id]
        return

    # بيانات التحويل
    amount = user_transfer_data[sender_id]['amount']
    target_user = users[target_id]
    
    # بناء رسالة التأكيد
    confirm_text = (
        "🔍 **تأكيد التحويل:**\n\n"
        f"**المبلغ المُحول:** {amount} نقطة\n"
        f"**عمولة التحويل:** {TRANSFER_FEE} نقطة\n"
        f"**المستقطع من حسابك:** {amount + TRANSFER_FEE} نقطة\n\n"
        f"**معلومات المستلم:**\n"
        f"  - **الاسم:** {target_user.get('name', 'غير متوفر')}\n"
        f"  - **الآيدي:** `{target_id}`\n"
        f"  - **نقاطه الحالية:** {target_user.get('points', 0)} نقطة\n\n"
        "**هل أنت متأكد من إتمام العملية؟**"
    )

    # إنشاء زر التأكيد والإلغاء
    markup = types.InlineKeyboardMarkup()
    # تم ترميز الآيدي والمبلغ في الـ callback_data
    confirm_btn = types.InlineKeyboardButton("✅ تأكيد التحويل", 
                                             callback_data=f"confirm_transfer_{target_id}_{amount}")
    cancel_btn = types.InlineKeyboardButton("❌ إلغاء", callback_data="cancel_transfer")
    markup.add(confirm_btn, cancel_btn)
    
    # إرسال رسالة التأكيد
    bot.send_message(sender_id, confirm_text, reply_markup=markup, parse_mode='Markdown')

# ----------------------------------------------------
# 4. معالج التأكيد النهائي وتنفيذ التحويل (تم تعزيز التحقق)
# ----------------------------------------------------
@bot.callback_query_handler(func=lambda call: call.data.startswith('confirm_transfer_'))
def finalize_transfer(call):
    
    sender_id = str(call.message.chat.id)
    
    # تحليل بيانات الـ callback
    try:
        # البيانات تأتي بالصيغة: confirm_transfer_TARGETID_AMOUNT
        _, _, target_id, amount_str = call.data.split('_')
        amount = int(amount_str)
    except ValueError:
        bot.answer_callback_query(call.id, "خطأ في تحليل بيانات التحويل. يرجى المحاولة مرة أخرى.")
        return
        
    try:
        users = load_users() # ⚠️ تأكد من تعريف دالة load_users()
    except NameError:
        bot.answer_callback_query(call.id, "خطأ داخلي: قاعدة البيانات غير متوفرة.")
        return
    
    # التحقق من أن المستلم موجود قبل الخصم
    if target_id not in users:
        bot.send_message(call.message.chat.id, 
                             "❌ **فشل التحويل:** لم يتم العثور على المستلم في قاعدة البيانات.",
                             parse_mode='Markdown')
        bot.answer_callback_query(call.id, "فشل: المستلم غير موجود.")
        return
    
    # تحقق أخير من الرصيد قبل الخصم (تحقق حاسم)
    required_points = amount + TRANSFER_FEE # ⚠️ تأكد من تعريف TRANSFER_FEE
    current_points = users.get(sender_id, {}).get('points', 0)

    if current_points < required_points:
        bot.send_message(call.message.chat.id, 
                             "❌ **فشل التحويل:** رصيدك أصبح غير كافٍ لإتمام العملية بعد التحقق الأخير.",
                             parse_mode='Markdown')
        bot.answer_callback_query(call.id, "فشل: الرصيد غير كافٍ.")
        return
        
    # --- تنفيذ التحويل ---
    
    # 1. خصم النقاط والعمولة من المُحوِل
    users[sender_id]['points'] -= required_points
    
    # 2. إضافة النقاط للمستلم
    users[target_id]['points'] += amount
    save_users(users) # ⚠️ تأكد من تعريف دالة save_users()
    
    # 3. إرسال إشعار للمستلم
    sender_name = users[sender_id].get('name', f"المستخدم {sender_id}")
    try:
        bot.send_message(
            target_id, 
            f"🎉 **لقد استلمت تحويلاً!**\n\n"
            f"  - **الكمية:** **{amount:,}** نقطة.\n"
            f"  - **من:** **{sender_name}**.\n"
            f"  - **رصيدك الجديد:** **{users[target_id]['points']:,}** نقطة.",
            parse_mode='Markdown'
        )
    except Exception as e:
        print(f"فشل إرسال إشعار للمستلم {target_id}: {e}")
        
    # 4. إرسال إشعار إتمام للمُحوِل
    bot.send_message(
        call.message.chat.id, 
        f"✅ **تم التحويل بنجاح!**\n\n"
        f"  - **المبلغ المُحول:** **{amount:,}** نقطة.\n"
        f"  - **العمولة المستقطعة:** **{TRANSFER_FEE}** نقطة.\n"
        f"  - **رصيدك الجديد:** **{users[sender_id]['points']:,}** نقطة.",
        parse_mode='Markdown'
    )
    
    # 5. محاولة حذف رسالة التأكيد القديمة لتنظيف الدردشة
    try:
        bot.delete_message(call.message.chat.id, call.message.message_id)
    except Exception as e:
        print(f"فشل حذف رسالة التأكيد: {e}")

    # 6. حفظ سجل التحويل في القناة (CHANNEL_ID2)
    # 🛑 التصحيح الفني لمشكلة المنطقة الزمنية (سنستخدم UTC كافتراضي)
    try:
        # إذا كان لديك متغير "timezone" معرفاً ككائن (مثل pytz.timezone('...')) فسيستخدمه
        current_time_str = datetime.now(timezone).strftime('%Y-%m-%d | %H:%M:%S')
    except Exception:
        # إذا كان هناك خطأ في تهيئة "timezone"، نستخدم التوقيت العالمي (UTC)
        current_time_str = datetime.now(timezone.utc).strftime('%Y-%m-%d | %H:%M:%S')

    # 🛑 التنسيق الجديد باستخدام HTML (لتحسين شكل السجل)
    log_message = (
        "<b>💵 سجل تحويل نقاط جديد 💵</b>\n"
        "┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄\n"
        f"<b>تاريخ التحويل:</b> {current_time_str}\n"
        f"<b>الكمية المُحولة:</b> <b>{amount:,}</b> نقطة\n"
        f"<b>العمولة المستقطعة:</b> <b>{TRANSFER_FEE}</b> نقطة\n"
        "┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄\n"
        f"<b>الآيدي المُحوِل:</b> <code>{sender_id}</code> | [{users[sender_id].get('name', 'غير متوفر')}]\n"
        f"<b>الآيدي المستلم:</b> <code>{target_id}</code> | [{users[target_id].get('name', 'غير متوفر')}]"
    )
    bot.send_message(CHANNEL_ID2, log_message, parse_mode='HTML') # ⚠️ تأكد من تعريف CHANNEL_ID2
    
    # 7. مسح البيانات المؤقتة
    global user_transfer_data
    if sender_id in user_transfer_data:
        del user_transfer_data[sender_id]
        
    bot.answer_callback_query(call.id, "تم إتمام التحويل!")

# ----------------------------------------------------
# 8. معالج الإلغاء
# ----------------------------------------------------
@bot.callback_query_handler(func=lambda call: call.data == "cancel_transfer")
def cancel_transfer(call):
    sender_id = str(call.message.chat.id)
    
    global user_transfer_data
    # مسح البيانات المؤقتة
    if sender_id in user_transfer_data:
        del user_transfer_data[sender_id]
        
    # إرسال رسالة الإلغاء
    bot.send_message(call.message.chat.id, 
                          "🚫 **تم إلغاء عملية التحويل.** يمكنك البدء من جديد متى شئت.",
                          parse_mode='Markdown')
                          
    # محاولة حذف رسالة التأكيد القديمة لتنظيف الدردشة
    try:
        bot.delete_message(call.message.chat.id, call.message.message_id)
    except Exception as e:
        print(f"فشل حذف رسالة الإلغاء: {e}")
        
    bot.answer_callback_query(call.id, "تم الإلغاء.")

# ---Handlers: عرض قائمة السحب والاختيار---
@bot.callback_query_handler(func=lambda call: call.data == "withdrawal_menu" and subscription_required_callback(call))
def withdrawal_menu_callback(call):
    user_id = str(call.from_user.id)

    # تخطي الايقاف للادمن
    if not is_bot_active(call.message) and not is_admin(user_id):
        return bot.answer_callback_query(call.id, "❌ البوت متوقف مؤقتاً.")
    
    users = load_users()
    u = users.get(user_id, {})
    if u.get("banned", False):
        return bot.answer_callback_query(call.id, "❌ لقد تم حظرك من استخدام هذا البوت.")
    
    markup = types.InlineKeyboardMarkup(row_width=1)
    
    # عرض طرق السحب (مجموعات)
    markup.add(types.InlineKeyboardButton("💳 ماستر كارد", callback_data="wd_group_mastercard"))
    markup.add(types.InlineKeyboardButton("📱 زين كاش", callback_data="wd_group_zain"))
    markup.add(types.InlineKeyboardButton("⛓️ رصيد اثير", callback_data="wd_group_ether"))
    markup.add(types.InlineKeyboardButton("₮ USDT (OKX - TRC20)", callback_data="wd_group_usdt"))
    markup.add(types.InlineKeyboardButton("🌏 رصيد اسيا", callback_data="wd_group_asia"))
    markup.add(types.InlineKeyboardButton("⬅️ رجوع للقائمة الرئيسية", callback_data="back_to_main_menu"))
    
    bot.edit_message_text(
        chat_id=call.message.chat.id, 
        message_id=call.message.message_id,
        text="اختر طريقة السحب التي تفضلها:", 
        reply_markup=markup
    )
    bot.answer_callback_query(call.id)


# لكل مجموعة نعرض الفئات المتاحة منها
@bot.callback_query_handler(func=lambda call: call.data.startswith("wd_group_"))
def wd_group_choose(call):
    group = call.data.replace("wd_group_", "")
    user_id = str(call.from_user.id)
    users = load_users()
    u = users.get(user_id, {})
    markup = types.InlineKeyboardMarkup(row_width=1)

    # بناء قائمة الفئات ذات الصلة بالمجموعة
    if group == "mastercard":
        keys = ["mastercard_10", "mastercard_25", "mastercard_50", "mastercard_100", "mastercard_150"]
    elif group == "zain":
        keys = ["zaincash_10", "zaincash_25", "zaincash_50", "zaincash_100", "zaincash_150"]
    elif group == "ether":
        keys = ["ether_balance_5", "ether_balance_10", "ether_balance_15"]
    elif group == "usdt":
        keys = ["usdt_okx_10", "usdt_okx_25", "usdt_okx_50"]
    elif group == "asia":
        keys = ["asia_balance_5", "asia_balance_10", "asia_balance_15"]
    else:
        keys = []

    for k in keys:
        item = WITHDRAWAL_METHODS[k]
        markup.add(types.InlineKeyboardButton(f"سحب {item['amount']}$ بسعر {item['cost']} نقطة ", callback_data=f"start_withdraw:{k}"))

    markup.add(types.InlineKeyboardButton("⬅️ رجوع لقائمة السحب", callback_data="withdrawal_menu"))
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                          text=f"رصيدك الحالي: {u.get('points', 0)} نقطة.\n\nاختر فئة السحب:", reply_markup=markup)
    bot.answer_callback_query(call.id)

# بدء عملية السحب: نتحقق من الرصيد ونحفظ temp_withdrawal مع قائمة الحقول
@bot.callback_query_handler(func=lambda call: call.data.startswith("start_withdraw:"))
def start_withdrawal_process(call):
    user_id = str(call.from_user.id)
    users = load_users()
    u = users.get(user_id, {})
    option_key = call.data.split(":")[1]
    if option_key not in WITHDRAWAL_METHODS:
        return bot.answer_callback_query(call.id, "❌ خيار سحب غير صحيح.")
    option = WITHDRAWAL_METHODS[option_key]
    if u.get("points", 0) < option["cost"]:
        return bot.answer_callback_query(call.id, f"❌ رصيدك ({u.get('points',0)} نقطة) غير كافٍ لسحب {option['amount']}$ ({option['cost']} نقطة).")
    # أنشئ temp_withdrawal مع الحقول المطلوبة وتابع الخطوة الأولى
    u['temp_withdrawal'] = {
        "method_key": option_key,
        "method_label": option["label"],
        "cost": option["cost"],
        "fields_required": option["fields"],
        "fields_collected": {},
        "current_field_index": 0
    }
    save_users(users)
    bot.answer_callback_query(call.id, f"بدء سحب {option['amount']}$ — {option['label']}.")
    # اسأل أول حقل
    first_field = option["fields"][0]
    prompt = FIELD_PROMPTS.get(first_field, "أدخل البيانات المطلوبة:")
    msg = bot.send_message(call.message.chat.id, prompt, parse_mode="Markdown")
    bot.register_next_step_handler(msg, collect_withdraw_field)

# دالة عامة تجمع الحقول بالتتابع لأي طريقة سحب
def collect_withdraw_field(message):
    user_id = str(message.from_user.id)
    users = load_users()
    if user_id not in users:
        bot.send_message(message.chat.id, "❌ حدث خطأ: المستخدم غير مسجل. ابدأ من جديد.")
        return
    u = users[user_id]
    if 'temp_withdrawal' not in u:
        bot.send_message(message.chat.id, "❌ انتهت صلاحية الطلب أو لم يبدأ بشكل صحيح. ابدأ من قائمة السحب.")
        return
    tw = u['temp_withdrawal']
    idx = tw.get("current_field_index", 0)
    fields = tw.get("fields_required", [])
    # خزّن الإجابة للحقل الحالي
    if idx < len(fields):
        field_name = fields[idx]
        tw['fields_collected'][field_name] = message.text.strip()
        tw['current_field_index'] = idx + 1
        save_users(users)
    # إذا لا يزال هناك حقول متبقية فاسأل التالية
    if tw['current_field_index'] < len(fields):
        next_field = fields[tw['current_field_index']]
        prompt = FIELD_PROMPTS.get(next_field, "أدخل البيانات المطلوبة:")
        msg = bot.send_message(message.chat.id, prompt, parse_mode="Markdown")
        bot.register_next_step_handler(msg, collect_withdraw_field)
        return
    # جميع الحقول تم جمعها -> عرض صفحة التأكيد مع زري تأكيد/إلغاء
    option_label = tw.get("method_label", "طريقة سحب")
    cost = tw.get("cost", 0)
    collected = tw.get("fields_collected", {})
    # بناء نص ملخص الحقول المجمعة
    fields_summary = ""
    for k, v in collected.items():
        fields_summary += f"\n• {k}: `{v}`"
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(types.InlineKeyboardButton("✅ تأكيد الإرسال", callback_data="confirm_final_withdrawal"),
               types.InlineKeyboardButton("❌ إلغاء", callback_data="cancel_withdrawal_confirm"))
    bot.send_message(message.chat.id,
                     f"**تأكيد طلب السحب**\n\nطريقة: {option_label}\nالنقاط المطلوب خصمها: {cost}\nالتفاصيل:{fields_summary}\n\nاضغط ✅ للتأكيد وسيتم خصم النقاط فورًا وإرسال الطلب للمشرف.",
                     parse_mode="Markdown", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "cancel_withdrawal_confirm")
def cancel_withdrawal_confirm_callback(call):
    user_id = str(call.from_user.id)
    users = load_users()
    if 'temp_withdrawal' in users.get(user_id, {}):
        del users[user_id]['temp_withdrawal']
        save_users(users)
    bot.edit_message_text("❌ تم إلغاء عملية السحب. لم يتم خصم أي نقاط.", call.message.chat.id, call.message.message_id)
    bot.answer_callback_query(call.id, "تم إلغاء الطلب.")

# عند الضغط على تأكيد -> نخصم النقاط فورًا، نخزن الطلب ونرسل للمشرف مع أزرار موافقة/رفض
@bot.callback_query_handler(func=lambda call: call.data == "confirm_final_withdrawal")
def final_withdrawal_submission(call):
    user_id = str(call.from_user.id)
    users = load_users()
    if user_id not in users:
        return bot.answer_callback_query(call.id, "❌ خطأ: المستخدم غير موجود.")
    u = users[user_id]
    if 'temp_withdrawal' not in u:
        return bot.answer_callback_query(call.id, "❌ انتهت صلاحية الطلب. ابدأ من جديد.")
    tw = u['temp_withdrawal']
    cost = tw.get("cost", 0)
    if u.get("points", 0) < cost:
        del u['temp_withdrawal']
        save_users(users)
        return bot.answer_callback_query(call.id, "❌ رصيدك غير كافٍ. تم إلغاء الطلب.")
    # خصم النقاط فورًا (حجز)
    users[user_id]['points'] -= cost
    save_users(users)
    # تسجيل الطلب
    withdrawals = load_withdrawals()
    withdrawal_id = f"W{int(time.time())}{user_id[-4:]}"
    request_data = {
        "id": withdrawal_id,
        "user_id": user_id,
        "username": u.get("username", "لا يوجد"),
        "name": u.get("name", "مستخدم"),
        "method_key": tw.get("method_key"),
        "method_label": tw.get("method_label"),
        "details": tw.get("fields_collected", {}),
        "cost": cost,
        "status": "Pending",
        "deducted": True,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    withdrawals[withdrawal_id] = request_data
    save_withdrawals(withdrawals)
    # إعلام المستخدم بنجاح الحجز
    try:
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text=f"✅ تم خصم {cost} نقطة من رصيدك كحجز لطلب السحب رقم `{withdrawal_id}`.\nسيتم مراجعة الطلب من قبل المشرف.\nرصيدك الحالي: {users[user_id]['points']} نقطة.",
                              parse_mode="Markdown")
    except Exception:
        pass
    bot.answer_callback_query(call.id, "تم خصم النقاط وإرسال الطلب للمشرف.")
    # احذف temp_withdrawal من المستخدم
    del users[user_id]['temp_withdrawal']
    save_users(users)
    # إرسال إشعار للمشرف مع أزرار موافقة/رفض
    admin_markup = types.InlineKeyboardMarkup(row_width=2)
    admin_markup.add(types.InlineKeyboardButton("✅ موافقة", callback_data=f"approve_wd:{withdrawal_id}"),
                     types.InlineKeyboardButton("❌ إلغاء", callback_data=f"reject_wd:{withdrawal_id}"))
    # بناء رسالة تفصيلية للمشرف (نعرض الحقول بطريقة مقروءة)
    details = request_data["details"]
    details_text = ""
    for k, v in details.items():
        details_text += f"\n• {k}: {v}"
    admin_msg = (f"🔔 طلب سحب جديد 🔔\n\nرقم الطلب: `{withdrawal_id}`\nالتاريخ: {request_data['timestamp']}\n\n"
                 f"مستخدم: <code>{user_id}</code> - {request_data['name']} (@{request_data['username']})\n"
                 f"طريقة: {request_data['method_label']}\nالنقاط المحجوزة: {cost}\nالتفاصيل:{details_text}")
    try:
        bot.send_message(WITHDRAWAL_ADMIN_ID, admin_msg, parse_mode="HTML", reply_markup=admin_markup)
    except telebot.apihelper.ApiTelegramException:
        bot.send_message(ADMIN_ID, f"⚠️ فشل إرسال طلب السحب رقم {withdrawal_id} إلى المشرف {WITHDRAWAL_ADMIN_ID}.")

# معالجة موافقة/رفض المشرف (كما في النسخة السابقة)
@bot.callback_query_handler(func=lambda call: call.data.startswith("approve_wd:") or call.data.startswith("reject_wd:"))
def handle_admin_withdrawal_action(call):
    admin_id = str(call.from_user.id)
    if admin_id != WITHDRAWAL_ADMIN_ID and admin_id != ADMIN_ID:
        return bot.answer_callback_query(call.id, "❌ ليس لديك صلاحية الموافقة/الإلغاء على السحوبات.")
    action, withdrawal_id = call.data.split(":")
    withdrawals = load_withdrawals()
    if withdrawal_id not in withdrawals:
        return bot.edit_message_text("❌ لم يتم العثور على هذا الطلب أو تم التعامل معه مسبقاً.", call.message.chat.id, call.message.message_id)
    request_data = withdrawals[withdrawal_id]
    user_id = request_data["user_id"]
    users = load_users()
    # منع إعادة التعامل مع نفس الطلب
    if request_data.get("status") != "Pending":
        return bot.answer_callback_query(call.id, f"⚠️ هذا الطلب تم التعامل معه بالفعل ({request_data.get('status')}).")
    if action == "approve_wd":
        # إذا كانت النقاط محجوزة (deducted=True) فلا نخصم مرة أخرى، فقط نغيّر الحالة إلى Approved
        request_data["status"] = "Approved"
        request_data["response_date"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        withdrawals[withdrawal_id] = request_data
        save_withdrawals(withdrawals)
 # ********** إضافة إشعار القناة هنا **********
        user_info = users.get(user_id, {})
        
        channel_msg = (
            f"💰 **تم قبول طلب سحب جديد!**\n\n"
            f"✨ **الحالة:** ✅ **تمت الموافقة**\n"
            f"👤 **المستخدم:** {user_info.get('name', 'غير معروف')} (@{user_info.get('username', 'لا يوجد')})\n"
            f"💳 **آيدي المستخدم:** <code>{user_id}</code>\n"
            f"💸 **المبلغ المطلوب:** {request_data.get('amount_label', 'غير محدد')}\n"
            f"💰 **تكلفة النقاط (المخصومة):** {request_data['cost']} نقطة\n"
            f"⚙️ **طريقة السحب:** {request_data['method_label']}\n"
        )
        try:
            # افتراض أن CHANNEL_ID2 هو القناة المناسبة للمعاملات المالية
            bot.send_message(CHANNEL_ID3, channel_msg, parse_mode="HTML")
        except Exception as e:
            print(f"Failed to send approval message to channel: {e}")
        # **********************************************
        
        # إشعار المستخدم
        try:
            bot.send_message(user_id, f"✅ تم قبول طلب السحب `{withdrawal_id}` وسيتم تنفيذ التحويل.\nالمبلغ: {request_data['method_label']}\nتم حجز: {request_data['cost']} نقطة.\nرصيدك الحالي: {users.get(user_id,{}).get('points',0)} نقطة.")
        except Exception:
            pass
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f"✅ تم الموافقة على طلب {withdrawal_id}.")
        bot.answer_callback_query(call.id, "تمت الموافقة.")
    elif action == "reject_wd":
        # نطلب من المشرف سبب الرفض — وسيتم استرجاع النقاط إذا كانت قد خصمت
        msg = bot.send_message(call.message.chat.id, f"أرسل **سبب إلغاء** طلب السحب رقم `{withdrawal_id}`. (سيتم استرجاع النقاط تلقائياً للمستخدم إن كانت قد خصمت).", parse_mode="Markdown")
        bot.register_next_step_handler(msg, finalize_rejection, withdrawal_id, call.message.message_id, call.message.chat.id)
        bot.answer_callback_query(call.id, "أرسل سبب الإلغاء.")

def finalize_rejection(message, withdrawal_id, original_msg_id, original_chat_id):
    rejection_reason = message.text.strip()
    withdrawals = load_withdrawals()
    users = load_users()
    if withdrawal_id not in withdrawals:
        bot.send_message(original_chat_id, "❌ لم يتم العثور على هذا الطلب أو تم التعامل معه مسبقاً.")
        return
    request_data = withdrawals[withdrawal_id]
    user_id = request_data["user_id"]
    cost = request_data["cost"]
    # تحديث حالة الطلب
    request_data["status"] = "Rejected"
    request_data["rejection_reason"] = rejection_reason
    request_data["response_date"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # استرجاع النقاط إذا كانت قد خصمت
    if request_data.get("deducted", False) and user_id in users:
        users[user_id]["points"] += cost
        save_users(users)
        try:
            bot.send_message(user_id, f"❌ تم إلغاء طلب السحب `{withdrawal_id}`.\nالسبب: {rejection_reason}\nتم استرجاع {cost} نقطة إلى رصيدك.\nرصيدك الحالي: {users[user_id]['points']} نقطة.")
        except Exception:
            pass
        # تحديث رسالة المشرف الأصلية
        bot.edit_message_text(chat_id=original_chat_id, message_id=original_msg_id,
                              text=f"❌ تم إلغاء طلب السحب رقم `{withdrawal_id}`.\nتم استرجاع {cost} نقطة للمستخدم.\nالسبب: {rejection_reason}")
    else:
        bot.edit_message_text(chat_id=original_chat_id, message_id=original_msg_id,
                              text=f"❌ تم إلغاء طلب السحب رقم `{withdrawal_id}`.\nالسبب: {rejection_reason} (لم تُخصم نقاط).")
    withdrawals[withdrawal_id] = request_data
    save_withdrawals(withdrawals)

# --- تكملة الدوال الأساسية ---

def load_a_json_data():
    file_path = 'a.json'
    # التحقق من وجود الملف أولاً
    if not os.path.exists(file_path):
        return {}
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError:
        print(f"Error decoding JSON from {file_path}")
        return {}
    except Exception as e:
        print(f"An error occurred while loading {file_path}: {e}")
        return {}


@bot.message_handler(commands=['start'])
def start(message):
    user_id = str(message.from_user.id)
    users = load_users()
    
    try:
        a_data = load_a_json_data() 
    except NameError:
        a_data = load_a_json() 

    # 1. فحص الحظر أولاً
    if users.get(user_id, {}).get("banned", False):
        bot.send_message(message.chat.id, "❌ لقد تم حظرك من استخدام هذا البوت.")
        return

    is_adminn = (user_id == str(ADMIN_ID))
    args = message.text.split()
    ref = args[1] if len(args) > 1 and args[1].isdigit() and args[1] != user_id else None

    # 2. 🔑 التسجيل الأولي وحفظ المُحيل (يحدث هنا قبل التحقق من الاشتراك)
    if user_id not in users:
        # تسجيل مستخدم جديد
        users[user_id] = {
            "name": message.from_user.first_name or "مستخدم",
            "username": message.from_user.username or "لا يوجد",
            "points": 0,
            "purchases": 0,
            "referrals": 0,
            "banned": False,
            "role": "admin" if is_adminn else "user",
            "last_claim": None,
            "daily_gifts": 0,
            "purchases_list": [],
            "referrer_id": ref, # 🔑 حفظ المُحيل بشكل دائم
            "referral_points_granted": False # 🔑 علامة لمنع تكرار منح النقاط
        }
        
        if is_admin:
            bot.send_message(message.chat.id, "🎉 تهانينا! تم التعرف عليك كأدمن البوت.", parse_mode="Markdown")

        # 🛑 لا يتم تنفيذ execute_referral هنا، نؤجلها إلى بعد الاشتراك أو في نهاية الدالة
        save_users(users)
        
        # إشعار دخول مستخدم جديد
        name = users[user_id]['name']
        username = users[user_id]['username']
        time_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        notif_msg = (
            f"🔔 <b>مستخدم جديد دخل البوت:</b>\n\n"
            f"<b>الاسم:</b> {name}\n"
            f"<b>المعرف:</b> @{username}\n"
            f"<b>الآيدي:</b> <code>{user_id}</code>\n"
            f"<b>التاريخ والوقت:</b> {time_now}"
        )
        try:
            bot.send_message(CHANNEL_ID, notif_msg, parse_mode="HTML") 
        except telebot.apihelper.ApiTelegramException as e:
            print(f"خطأ في إرسال إشعار القناة: {e}")

    # 3. 🔑 التحقق من الاشتراك الإجباري
    # ⚠️ يجب التأكد من أن المتغير REQUIRED_CHANNEL_ID مُعرَّف كـ global ومُحمّل من config.json

# ... (هذا الكود يتم وضعه داخل دالة معالجة الرسائل الرئيسية التي تفحص الاشتراك)

    if not is_admin(user_id):
        if not check_subscription(user_id, REQUIRED_CHANNEL_ID):
            
            # 📌 إنشاء الرابط الديناميكي للقناة هنا
            try:
                # محاولة جلب معلومات القناة لإنشاء رابط t.me/username
                chat_object = bot.get_chat(REQUIRED_CHANNEL_ID)
                if chat_object.username:
                    channel_link = f"https://t.me/{chat_object.username}"
                else:
                    # في حال عدم وجود يوزر نيم، نستخدم رابط مشاركة رقمي
                    # يتم حذف -100 من الآيدي الرقمي للقناة
                    channel_link = f"https://t.me/c/{str(REQUIRED_CHANNEL_ID).replace('-100', '')}/1"
                    
            except Exception:
                # في حال فشل جلب المعلومات (البوت ليس مشرفاً)، نستخدم رابط رقمي احتياطي
                channel_link = f"https://t.me/c/{str(REQUIRED_CHANNEL_ID).replace('-100', '')}/1"


            markup = types.InlineKeyboardMarkup(row_width=1)
            markup.add(types.InlineKeyboardButton("🔗 اضغط للاشتراك في القناة", url=channel_link)) # ⬅️ تم تحديث channel_link
            
            # تم تبسيط الـ callback إلى "check_sub_final"
            markup.add(types.InlineKeyboardButton("✅ تحقق من الاشتراك", callback_data="check_sub_final")) 
            
            bot.send_message(message.chat.id, 
                             "⚠️ <b>يجب عليك الاشتراك في القناة التالية للاستمرار في استخدام البوت:</b>", 
                             reply_markup=markup, parse_mode="HTML")
            return # 🛑 الخروج هنا لانتظار التحقق

        if not is_bot_active(message):
            return
# ...
    # 4. تنفيذ الإحالة للمستخدم الذي قام بالتسجيل حديثاً واشترك الآن (أو عاد بعد الاشتراك)
    u = users[user_id]
    
    if u.get('referrer_id') and not u.get('referral_points_granted', False):
        ref_id = u['referrer_id']
        if ref_id in users:
             # تنفيذ الإحالة ومنح النقاط للمُحيل
            execute_referral(user_id, ref_id, users)
             # وضع علامة على أن النقاط مُنحت لمنع التكرار
            users[user_id]["referral_points_granted"] = True
            save_users(users) # يجب الحفظ بعد التعديل

    # 5. عرض القائمة الرئيسية
    
    user_points_to_add = a_data.get(user_id, {}).get("points_to_add", 0)

    main_menu_markup = get_main_menu_markup(user_id)

    bot.send_message(message.chat.id, f"""
<b>✨ مرحباً {u['name']}!</b>

<b>📋 معلومات حسابك:</b>
<b>🆔 الآيدي:</b> <code>{user_id}</code>
<b>👤 الاسم:</b> {u['name']}
<b>🔎 المعرف:</b> @{u['username']}
<b>💰 رصيدك:</b> {u['points']:,} نقطة
📊 <b>عدادك:</b> {user_points_to_add:,} 
<b>🤝 عدد الدعوات:</b> {u['referrals']}
<b>🎁 الهدايا اليومية:</b> {u.get("daily_gifts", 0)}

<b>🔗 رابط الدعوة الخاص بك:</b>
<code>https://t.me/{bot.get_me().username}?start={user_id}</code>

<b>🏅 شارتك:</b> {get_badge(u)}
""",
        reply_markup=main_menu_markup,
        parse_mode="HTML",
        disable_web_page_preview=True
    )
# --------------------------------------------------------------------------
# 📌 دالة مساعدة لتنفيذ الإحالة (موصى بها)
# --------------------------------------------------------------------------
def execute_referral(new_user_id, referrer_id, users):
    """تنفيذ عملية الإحالة وإرسال الإشعارات."""
    if referrer_id in users and referrer_id != new_user_id:
        # ⚠️ ملاحظة: تأكد من تعريف load_edit() في ملفك أو استخدام load_edit_settings()
        try:
            settings = load_edit()
        except NameError:
            settings = load_edit_settings()
            
        ref_points = settings.get("referral_points", 50)
        
        users[referrer_id]["points"] += ref_points
        users[referrer_id]["referrals"] += 1
        
        # تحديث رتبة المستخدم المُحيل
        # ⚠️ تأكد من تعريف دالة update_user_rank
        # update_user_rank(referrer_id) 

        # إشعار للمُحيل
        new_user_name = users[new_user_id].get('name', 'مستخدم جديد')
        # ⚠️ تأكد من تعريف دالة get_rank
        # referrer_rank = get_rank(users[referrer_id]["points"])
        
        try:
            bot.send_message(referrer_id, 
                             f"<b>🎁 تهانينا!</b> ربحت <b>{ref_points} نقطة</b> من دعوة المستخدم <b>{new_user_name}</b>.", 
                             parse_mode="HTML")
            # f"تصنيفك الآن: <b>{referrer_rank}</b>."
        except telebot.apihelper.ApiTelegramException:
            print(f"لا يمكن إرسال رسالة تنبيه الإحالة للمستخدم {referrer_id}")
# --------------------------------------------------------------------------
# 📌 دالة معالجة التحقق من الاشتراك (تم تبسيط الكولباك إلى 'check_sub_final')
# --------------------------------------------------------------------------
@bot.callback_query_handler(func=lambda call: call.data == 'check_sub_final')
def check_sub_handler(call):
    user_id = str(call.from_user.id)
    
    # 1. التحقق من الاشتراك الإجباري مرة أخرى
    if check_subscription(user_id, REQUIRED_CHANNEL_ID):
        
        # 2. تعديل رسالة التحقق
        bot.edit_message_text("✅ تم تأكيد اشتراكك بنجاح. يتم الآن تحديث معلوماتك...", 
                              call.message.chat.id, call.message.message_id)
        
        users = load_users()
        u = users.get(user_id)
        
        # 3. 🔑 تنفيذ الإحالة (إذا كانت معلقة)
        if u and u.get('referrer_id') and not u.get('referral_points_granted', False):
            ref_id = u['referrer_id']
            if ref_id in users:
                # تنفيذ عملية الإحالة لمنح النقاط للمُحيل
                execute_referral(user_id, ref_id, users)
                
                # وضع علامة على أن النقاط مُنحت لمنع التكرار
                users[user_id]["referral_points_granted"] = True
                save_users(users)
        users = load_users() 
        u = users.get(user_id)
        
        
        bot.send_message(call.message.chat.id, 
                         "🎉 تهانينا! اكتمل التحقق بنجاح.\nاضغط على `/start` لرؤية القائمة الرئيسية.", 
                         reply_markup=types.ReplyKeyboardRemove())
        
        try:
            a_data = load_a_json_data() 
        except NameError:
            a_data = load_a_json() # افتراض وجود دالة بديلة
            
        user_points_to_add = a_data.get(user_id, {}).get("points_to_add", 0)
        main_menu_markup = get_main_menu_markup(user_id)
        
        bot.send_message(call.message.chat.id, f"""
<b>✨ مرحباً {u['name']}!</b>

<b>📋 معلومات حسابك:</b>
<b>🆔 الآيدي:</b> <code>{user_id}</code>
<b>👤 الاسم:</b> {u['name']}
<b>🔎 المعرف:</b> @{u['username']}
<b>💰 رصيدك:</b> {u['points']:,} نقطة
📊 <b>عدادك:</b> {user_points_to_add:,} 
<b>🤝 عدد الدعوات:</b> {u['referrals']}
<b>🎁 الهدايا اليومية:</b> {u.get("daily_gifts", 0)}

<b>🔗 رابط الدعوة الخاص بك:</b>
<code>https://t.me/{bot.get_me().username}?start={user_id}</code>

<b>🏅 شارتك:</b> {get_badge(u)}
""",
            reply_markup=main_menu_markup,
            parse_mode="HTML",
            disable_web_page_preview=True
        )
        
        # ⚠️ يتم إرسال رسالتين الآن: "تم تأكيد اشتراكك" ثم "مرحباً {name}"،
        # وهذا هو السلوك الأنسب لضمان عدم توقف البوت.
            
    else:
        # فشل التحقق
        bot.answer_callback_query(call.id, "❌ لم يتم تأكيد الاشتراك بعد. يرجى الاشتراك ثم الضغط مجدداً.", show_alert=True)              
RULES_MESSAGE = """
**📜 ملاحظات وقوانين هامة للحفاظ على حسابك:**

1. **شراء النقاط:** ممنوع شراء النقاط من غير الوكلاء المدرجة أسماؤهم في البوت، والمخالفة تؤدي إلى **حضر الطرفين**.

2. **استلام النقاط:** يمنع استلام كميات كبيرة أو غير اعتيادية من حسابات وهمية أو حقيقية، وستؤدي المخالفة إلى **حضر الطرفين**.

3. **التحايل والانتحال:** أي محاولة للتحايل على الوكلاء أو قسم الدعم أو الانتحال كأحد أفراد الإدارة تؤدي إلى **الحضر الدائم**.

4. **التعامل مع القروض:** إرسال أو استلام النقاط من أصحاب القروض يؤدي إلى **إنذارات وحضر أسبوعي**.

5. **المطورين والمشاريع الأخرى:** ممنوع استثمار أي دعم أو مشاريع لمطورين آخرين داخل البوت بأي شكل كان.

6. **التسقيط والإساءة:** أي محاولة تسقيط أو تشويه سمعة المستخدمين أو الإدارة تُعاقب بـ**الحضر الشهري أو السنوي**.

7. **مسؤولية الحساب والأرباح:** المتجر غير مسؤول عن أي مشاكل تتعلق بحسابك في تيليجرام، وأرباح المتجر قابلة للصعود والنزول حسب طبيعة الاستثمار.

8. **تفعيل الحساب:** في حال لم يقم المستخدم بالسحب خلال مدة أقصاها **45 يوم**، يتم حظر الحساب بشكل تلقائي.
"""
agent_temp_data = {} 
@bot.message_handler(func=lambda message: message.text == "معلومات الوكيل") # 🛑 تم التعديل إلى زر نصي
def start_get_agent_info(message):
    sender_id = message.from_user.id 

    if sender_id != ADMIN_ID:
        return 

    str_sender_id = str(sender_id)
    if str_sender_id in agent_temp_data:
        del agent_temp_data[str_sender_id]

    agent_temp_data[str_sender_id] = {'action': 'get_agent_info'} 
    
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("❌ إلغاء العملية", callback_data="cancel_agent_info_get"))

    msg = bot.send_message(message.chat.id, 
                           "الرجاء إرسال آيدي الوكيل الذي تريد عرض معلوماته:", 
                           reply_markup=markup,
                           parse_mode="Markdown")
    
    bot.register_next_step_handler(msg, get_and_display_agent_info)

@bot.callback_query_handler(func=lambda call: call.data == "cancel_agent_info_get")
def cancel_get_agent_info_callback(call):
    sender_id = str(call.from_user.id)
    if sender_id in agent_temp_data and agent_temp_data[sender_id].get('action') == 'get_agent_info':
        del agent_temp_data[sender_id]
        
        bot.edit_message_text("❌ تم إلغاء عملية جلب معلومات الوكيل.", 
                              call.message.chat.id, 
                              call.message.message_id)
                              
        bot.answer_callback_query(call.id, "تم الإلغاء.")
    else:
        bot.answer_callback_query(call.id, "لا توجد عملية نشطة للإلغاء.")


def get_and_display_agent_info(message):
    sender_id = str(message.from_user.id)
    
    if sender_id not in agent_temp_data or agent_temp_data[sender_id].get('action') != 'get_agent_info':
        return bot.send_message(message.chat.id, "❌ انتهت صلاحية العملية. يرجى البدء مجدداً بزر 'معلومات الوكيل'.")

    target_agent_id = message.text.strip()
    
    try:
        agents = load_agents() # تحميل بيانات الوكلاء
    except NameError:
        del agent_temp_data[sender_id]
        return bot.send_message(message.chat.id, "❌ خطأ داخلي: دالة load_agents غير معرفة.")
    
    del agent_temp_data[sender_id] 

    if not target_agent_id.isdigit():
        return bot.send_message(message.chat.id, "❌ الآيدي غير صحيح. يجب أن يكون رقماً.")
        
    if target_agent_id not in agents:
        return bot.send_message(message.chat.id, 
                                f"❌ لا يوجد وكيل مسجل بالآيدي: <code>{target_agent_id}</code>.", 
                                parse_mode="HTML") # 🛑 استخدام HTML هنا

    agent_data = agents[target_agent_id]
    
    # 🛑 التنسيق الجديد: استخدام وسم <b> للخط الغامق و <code> للآيدي و <br> للأسطر الجديدة
    info_msg = (
        f"📋 <b>معلومات الوكيل:</b>\n"
        f"┄┄┄┄┄┄┄┄┄┄┄\n"
        f"<b>🆔 الآيدي:</b> <code>{target_agent_id}</code>\n"
        f"<b>👤 الاسم:</b> {agent_data.get('name', 'غير معروف')}\n"
        f"<b>🛠 الدور:</b> {agent_data.get('role', 'غير محدد')}\n"
        f"<b>💰 الرصيد الافتراضي:</b> <b>{agent_data.get('balance', 0):,}</b> نقطة\n"
        f"┄┄┄┄┄┄┄┄┄┄┄\n"
        f"<b>🔗 رابط الحساب:</b> <a href='{agent_data.get('account_link', '#')}'>اضغط هنا</a>\n"
        f"<b>📢 رابط القناة:</b> <a href='{agent_data.get('channel_link', '#')}'>اضغط هنا</a>"
    )
    
    # يجب أن يكون parse_mode="HTML" لاستخدام <b> و <a>
    bot.send_message(message.chat.id, info_msg, parse_mode="HTML")
# --- معالج الـ Callback لـ "من نحن؟" (تم التعديل) ---
@bot.callback_query_handler(func=lambda call: call.data == "about_us_inline")
def handle_about_us_query(call):
    
    # 🛑 1. تصحيح استخدام المنطقة الزمنية للحصول على الوقت الحالي
    # يجب استخدام timezone.utc ثم تحويلها إلى المنطقة الزمنية المحلية للخادم (.astimezone())
    now = datetime.now(timezone.utc).astimezone()
    current_time_str = now.strftime("%Y-%m-%d | %H:%M:%S")

    # ⚠️ ملاحظة: يجب أن تكون RULES_MESSAGE مُعرفة مسبقاً في ملفك
    # 2. إعداد الرسالة النهائية (القوانين + التحديث)
    final_message = RULES_MESSAGE + f"\n\nآخر تحديث لهذه القوانين: {current_time_str}"

    # 3. إنشاء لوحة المفاتيح InlineKeyboardMarkup
    markup = types.InlineKeyboardMarkup(row_width=2)
    
    # أزرار الروابط الخارجية
    btn_channel = types.InlineKeyboardButton("📢 قناة البوت", url="https://t.me/topcash2005") 
    btn_withdraw_channel = types.InlineKeyboardButton("💰 قناة السحب", url="https://t.me/Topcash124") 
    btn_owner = types.InlineKeyboardButton("🧑‍💻 المالك", url="https://t.me/A_E20877")
    
    # زر الرجوع (callback_data)
    btn_back = types.InlineKeyboardButton("🔙 رجوع", callback_data="back_to_main_menu")
    
    # إضافة الأزرار إلى لوحة المفاتيح
    markup.add(btn_channel, btn_withdraw_channel) 
    markup.add(btn_owner, btn_back) 

    # 4. إرسال الرسالة الجديدة
    bot.send_message(
        chat_id=call.message.chat.id,
        text=final_message,
        reply_markup=markup, 
        parse_mode='Markdown' # للاستفادة من التنسيق الغامق (**)
    )
            
    # 5. إنهاء الاستعلام
    bot.answer_callback_query(call.id, "تم عرض القوانين الهامة.")


@bot.callback_query_handler(func=lambda call: call.data == "claim_daily_gift_inline" and subscription_required_callback(call))
def claim_daily_gift_callback(call):
    user_id = str(call.from_user.id)

    # تخطي الايقاف للادمن
    if not is_bot_active(call.message) and not is_admin(user_id):
        return bot.answer_callback_query(call.id, "❌ البوت متوقف مؤقتاً.")
        
    users = load_users()
    settings = load_edit()

    if user_id not in users or users[user_id].get("banned", False):
        return bot.answer_callback_query(call.id, "❌ لقد تم حظرك من استخدام هذا البوت.")

    u = users[user_id]
    rank = get_rank(u["points"])

    if "daily_gifts" not in u:
        u["daily_gifts"] = 0

    now = datetime.now()
    last_claim_str = u.get("last_claim")
    can_claim = True

    if last_claim_str:
        last_claim_time = datetime.strptime(last_claim_str, "%Y-%m-%d %H:%M:%S")
        if now - last_claim_time < timedelta(days=1):
            can_claim = False
            time_remaining = timedelta(days=1) - (now - last_claim_time)
            hours_left, remainder = divmod(time_remaining.seconds, 3600)
            minutes_left, _ = divmod(remainder, 60)
    
    if can_claim or is_admin(user_id):  # الادمن يمكنه المطالبة دائمًا
        daily_gift_amount = settings.get("daily_gift_points", 10) 

        u["points"] += daily_gift_amount
        u["last_claim"] = now.strftime("%Y-%m-%d %H:%M:%S")
        u["daily_gifts"] += 1

        save_users(users)

        bot.answer_callback_query(call.id, f"🎁 تهانينا! حصلت على {daily_gift_amount} نقطة.", show_alert=True)
        # تعديل رسالة المنيو الرئيسية لتحديث زر الهدية
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=get_main_menu_markup(user_id))
    else:
        bot.answer_callback_query(call.id, f"⏳ الوقت المتبقي: {hours_left} س و {minutes_left} د.", show_alert=True)

# معالج عرض السلع
@bot.callback_query_handler(func=lambda call: call.data == "show_products_menu" and subscription_required_callback(call))
def buy_product_callback(call):
    """عرض قائمة المنتجات - لا يتأثر الأدمن بإيقاف البوت"""
    try:
        user_id = call.from_user.id

        # ✅ الأدمن لا يتأثر بتوقف البوت نهائيًا
        if user_id not in ADMIN_ID:
            import json, os
            if os.path.exists("bot_status.json"):
                with open("bot_status.json", "r", encoding="utf-8") as f:
                    status = json.load(f)
                if not status.get("active", True):
                    reason = status.get("reason", "تم إيقاف البوت مؤقتاً")
                    resume_time = status.get("resume_time", "غير محدد")
                    bot.answer_callback_query(
                        call.id,
                        f"❌ البوت متوقف مؤقتاً.\nالسبب: {reason}\nيعود للعمل في: {resume_time}",
                        show_alert=True
                    )
                    return
    except Exception as e:
        print(f"[buy_product_callback check error] {e}")

    # ✅ باقي الكود الأصلي كما هو تمامًا بدون أي تعديل
    user_id = str(call.from_user.id)
    users = load_users()
    if user_id not in users or users[user_id].get("banned", False):
        return bot.answer_callback_query(call.id, "❌ لقد تم حظرك من استخدام هذا البوت.")

    products = load_products()
    if not products:
        bot.answer_callback_query(call.id, "لا توجد سلع حالياً.")
        return

    markup = types.InlineKeyboardMarkup(row_width=1)
    for name, data in products.items():
        markup.add(types.InlineKeyboardButton(f"{name} - {data['price']} نقطة", callback_data=f"select_buy:{name}"))

    markup.add(types.InlineKeyboardButton("⬅️ رجوع للقائمة الرئيسية", callback_data="back_to_main_menu"))

    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text="اختر السلعة التي تريد شراءها:",
        reply_markup=markup
    )
    bot.answer_callback_query(call.id)


# معالج اختيار سلعة محددة للشراء
@bot.callback_query_handler(func=lambda call: call.data.startswith("select_buy:"))
def handle_select_purchase(call):
    item_full_name = call.data.split(":")[1]
    products = load_products()
    
    if item_full_name in products:
        price = products[item_full_name]["price"]
        markup = types.InlineKeyboardMarkup(row_width=2)
        markup.add(
            types.InlineKeyboardButton("✅ نعم", callback_data=f"confirm_buy:{item_full_name}"),
            types.InlineKeyboardButton("❌ لا", callback_data="back_to_main_menu")
        )
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=f"هل تريد شراء {item_full_name} مقابل {price} نقطة؟", 
            reply_markup=markup
        )
    else:
        bot.answer_callback_query(call.id, "السلعة غير موجودة.")

# معالج تأكيد الشراء (منطق إضافة العداد إلى a.json)
# معالج تأكيد الشراء (منطق إضافة العداد إلى a.json)
@bot.callback_query_handler(func=lambda call: call.data.startswith("confirm_buy:"))
def confirm_purchase(call):
    user_id = str(call.from_user.id)
    users = load_users()
    products = load_products()
    
    # ⚠️ نستخدم الآن المتغير BAGHDAD_TZ الذي تم تعريفه في بداية الملف
    
    if user_id not in users or users[user_id].get("banned", False):
        return bot.answer_callback_query(call.id, "❌ لقد تم حظرك من استخدام هذا البوت.")

    item_full_name = call.data.split(":")[1]
    
    if item_full_name not in products:
        return bot.answer_callback_query(call.id, "❌ السلعة غير موجودة.")

    product_data = products[item_full_name]
    price = product_data["price"]

    if users[user_id]["points"] >= price:
        
        # --- خصم النقاط وتحديث المشتريات ---
        users[user_id]["points"] -= price
        users[user_id]["purchases"] += 1
        users[user_id].setdefault("purchases_list", []).append({
            "item": item_full_name,
            # 🔑 استخدام BAGHDAD_TZ
            "date": datetime.now(BAGHDAD_TZ).strftime("%Y-%m-%d %H:%M:%S")
        })

        # --- منطق سلعة العداد (a.json) ---
        item_name_display = item_full_name
        counter_value = product_data.get("counter", 0)
        
        if product_data.get("is_counter", False) and counter_value > 0:
            a_data = load_a_json()
            
            # 🔑 تحديد الوقت الحالي (Localized) باستخدام BAGHDAD_TZ
            current_time = datetime.now(BAGHDAD_TZ)
            # 🔑 حساب تاريخ الانتهاء (سنة واحدة من الآن)
            expiry_time = current_time + timedelta(days=365)
            
            # --- منطق العداد ---
            is_valid_existing_counter = (
                user_id in a_data and 
                isinstance(a_data[user_id], dict) and
                a_data[user_id].get('expiry_date') != 'expired'
            )
            
            if is_valid_existing_counter:
                a_data[user_id]['points_to_add'] = a_data[user_id].get('points_to_add', 0) + counter_value
                new_counter_value = a_data[user_id]['points_to_add']
            else:
                current_count = a_data.get(user_id, 0)
                new_counter_value = current_count + counter_value
                
                a_data[user_id] = {
                    'points_to_add': new_counter_value,
                    'last_added_time': current_time.isoformat()
                }
            
            # 🔑 تحديث تاريخ الانتهاء (يجب أن يتم هذا على التاريخ الجديد دائماً)
            a_data[user_id]['expiry_date'] = expiry_time.strftime('%Y-%m-%d %H:%M:%S')

            save_a_json(a_data)
            
            expiry_date_display = expiry_time.strftime('%Y-%m-%d')
            
            item_name_display = f"{item_full_name} (عداد: +{counter_value} - الإجمالي: {new_counter_value})\n"
            item_name_display += f"🎉 *تم تفعيل العداد لمدة سنة! سينتهي في: {expiry_date_display}*"
            
        save_users(users)
        
        # تعديل الرسالة
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("⬅️ رجوع للقائمة الرئيسية", callback_data="back_to_main_menu"))
        
        # 🔑 استخدام BAGHDAD_TZ
        current_time_display = datetime.now(BAGHDAD_TZ).strftime('%Y-%m-%d %H:%M:%S')
        
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=f"✅ تم شراء *{item_name_display}* بنجاح!\n" 
                 f"📅 التاريخ: {current_time_display}\n"
                 f"رصيدك المتبقي: {users[user_id]['points']} نقطة.",
            reply_markup=markup,
            parse_mode="Markdown"
        )
        
        # إشعار للقناة (باستخدام BAGHDAD_TZ)
        bot.send_message(
            CHANNEL_ID2,
            f"""🛒 تم شراء سلعة جديدة:
السلعة: {item_full_name}
السعر: {price} نقطة
من: {users[user_id]['name']} (@{users[user_id].get('username', 'لا يوجد')})
الآيدي: <code>{user_id}</code>
📅 التاريخ: {current_time_display}
🔑 **العداد ينتهي في:** {expiry_date_display if 'expiry_date_display' in locals() else 'لا يوجد'}
""",
            parse_mode="HTML"
        )
        bot.answer_callback_query(call.id, "✅ تم الشراء بنجاح.")


    else:
        bot.edit_message_text(
            "❌ رصيدك غير كافي لإتمام عملية الشراء.",
            call.message.chat.id,
            call.message.message_id
        )
        bot.answer_callback_query(call.id, "❌ رصيدك غير كافي.")
# معالج مشترياتي
@bot.callback_query_handler(func=lambda call: call.data == "show_purchases_inline" and subscription_required_callback(call))
def show_purchases_callback(call):
    user_id = call.from_user.id  # احتفظ بالنوع int كما هو

    try:
        # ✅ الأدمن يتخطى الإيقاف
        if user_id not in ADMIN_IDS:
            import json, os
            if os.path.exists("bot_status.json"):
                with open("bot_status.json", "r", encoding="utf-8") as f:
                    status = json.load(f)
                if not status.get("active", True):
                    reason = status.get("reason", "تم إيقاف البوت مؤقتاً")
                    resume_time = status.get("resume_time", "غير محدد")
                    bot.answer_callback_query(
                        call.id,
                        f"❌ البوت متوقف مؤقتاً.\nالسبب: {reason}\nيعود للعمل في: {resume_time}",
                        show_alert=True
                    )
                    return
    except Exception as e:
        print(f"[show_purchases_callback check error] {e}")

    # ✅ باقي الكود الأصلي
    user_id_str = str(user_id)  # تحويل للاستخدام في dicts
    users = load_users()
    if user_id_str not in users or users[user_id_str].get("banned", False):
        return bot.answer_callback_query(call.id, "❌ لقد تم حظرك من استخدام هذا البوت.")

    purchases = users[user_id_str].get("purchases_list", [])

    msg = ""
    if not purchases:
        msg = "لم تقم بأي عملية شراء بعد."
    else:
        msg = "🧾 سجل مشترياتك:\n\n"
        for p in purchases:
            msg += f"- {p['item']} | {p['date']}\n"

    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("⬅️ رجوع للقائمة الرئيسية", callback_data="back_to_main_menu"))

    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=msg,
        reply_markup=markup
    )
    bot.answer_callback_query(call.id)


    

# معالج الكوبون (يطلب إرسال النص)
@bot.callback_query_handler(func=lambda call: call.data == "ask_for_coupon_inline" and subscription_required_callback(call))
def ask_for_coupon_callback(call):
    user_id = str(call.from_user.id)

    # تخطي الايقاف للادمن
    if not is_bot_active(call.message) and not is_admin(user_id):
        return bot.answer_callback_query(call.id, "❌ البوت متوقف مؤقتاً.")
        
    users = load_users()
    if user_id not in users or users[user_id].get("banned", False):
        return bot.answer_callback_query(call.id, "❌ لقد تم حظرك من استخدام هذا البوت.")
        
    # إرسال رسالة جديدة لتسجيل الخطوة التالية
    msg = bot.send_message(call.message.chat.id, "أرسل رمز الكوبون الذي تريد استخدامه:")
    bot.register_next_step_handler(msg, redeem_coupon_code)
    bot.answer_callback_query(call.id)



def redeem_coupon_code(message):
    """تفعيل الكوبون."""
    code = message.text.strip()
    user_id = str(message.from_user.id)
    users = load_users()
    coupons = load_coupons()

    if code in coupons:
        coupon = coupons[code]

        if user_id in coupon.get("used_by", []):
            bot.send_message(message.chat.id, "❌ لقد استخدمت هذا الكوبون من قبل.")
            return
        
        if len(coupon.get("used_by", [])) >= coupon.get("max_uses", float('inf')):
            bot.send_message(message.chat.id, "❌ تم استهلاك الكوبون بالكامل.")
            return
        
        # ********** 🚨 منطق التحقق من الانتهاء المعدل 🚨 **********
        expires_at_str = coupon.get("expires_at")
        
        # الشرط الجديد: نتجاهل التحقق إذا كانت القيمة "لا يوجد" أو غير موجودة أصلاً
        if expires_at_str and expires_at_str != "لا يوجد":
            try:
                # يجب التأكد من استيراد datetime وتعيين timezone في بداية الملف
                expire_time = datetime.strptime(expires_at_str, "%Y-%m-%d %H:%M:%S")
                
                # ملاحظة: إذا كنت تستخدم توقيت المنطقة الزمنية (timezone)، استخدم هذا السطر:
                # expire_time = datetime.strptime(expires_at_str, "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone)
                # now = datetime.now(timezone) 
                
                if datetime.now() > expire_time:
                    bot.send_message(message.chat.id, "❌ انتهت صلاحية هذا الكوبون.")
                    return
            except ValueError:
                # يمكن إضافة معالجة بسيطة للخطأ هنا، لكن الكود سيستمر في العمل إذا حدث خطأ غير متوقع في التاريخ
                pass 
        # *********************************************************

        # يتم حذف كتلة try-except KeyError السابقة لأننا نتحقق الآن من القيمة
            
        users[user_id]["points"] += coupon["points"]
        coupon.setdefault("used_by", []).append(user_id)
        
        save_users(users)
        save_coupons(coupons)

        badge = get_badge(users[user_id])
        bot.send_message(message.chat.id, f"✅ تم تفعيل الكوبون!\nتمت إضافة {coupon['points']} نقطة.\nرصيدك الحالي: {users[user_id]['points']}")

        bot.send_message(
            CHANNEL_ID,
            f"🎫 كوبون مستخدم!\n"
            f"الاسم: {message.from_user.first_name}\n"
            f"اليوزر: @{message.from_user.username or 'لا يوجد'}\n"
            f"الآيدي: <code>{user_id}</code>\n"
            f"النقاط المضافة: {coupon['points']}\n"
            f"الشارة: {badge}",
            parse_mode="HTML"
        )
    else:
        bot.send_message(message.chat.id, "❌ الكوبون غير صحيح.")

# --- منطق الأدمن والإدارة (Admin Panel) ---

@bot.message_handler(commands=["admin"])
def admin_panel(message):
    user_id = str(message.from_user.id)
    users = load_users()

    if user_id != ADMIN_IDS and users.get(user_id, {}).get("role") != "admin":
        bot.send_message(message.chat.id, "❌ ليس لديك صلاحية الوصول إلى لوحة التحكم.")
        return

    # استخدام ReplyKeyboardMarkup هنا لأنه يمثل لوحة تحكم الأدمن
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("إيقاف البوت", "تشغيل البوت")
    markup.add("تمويل وكيل", "معلومات الوكيل")
    markup.add("🔒 حظر مستخدم", "🔓 إلغاء الحظر")
    markup.add("🆕 إضافة سلعة", "🗑 حذف سلعة")
    markup.add("🚫 إيقاف الإرسال", "✅ تفعيل الإرسال")
    markup.add("➕ إضافة وكيل", "➖ إزالة وكيل", "🛠️ إدارة الأدمنز")
    markup.add("➕ إضافة عداد","➖ مسح عداد", "🔗 الاشتراك الإجباري")
    markup.add("➕ تعيين نقاط الدعوة", "🎁 تعيين نقاط الهدية")
    markup.add("➕ إرسال نقاط","خصم نقاط")
    markup.add("تصفير الكل", "🧼 تصفير الدعوة")
    markup.add("اذاعة", "📨 ارسال الى مستخدم")
    markup.add("سجل الكوبون","انشاء كوبون")
    markup.add("📊 عرض الإحصائيات", "النظام")
    markup.add("إعادة ضبط المصنع", "📄 جلب الملفات")
    
     
    bot.send_message(message.chat.id, f"""<b>⚙️ لوحة التحكم - الأدمن</b>

مرحباً بك في لوحة التحكم الخاصة بالأدمن.

<b>📊 الأوامر المتاحة:</b>
• 🏆 لعرض المتصدرين بالنقاط: /top
• 📁 لعرض ملف الأعضاء: /userss
• ℹ️ لعرض معلومات مستخدم عن طريق الآيدي: /info
• 💸 لإرسال نقاط لمستخدم معين كـ مرسل: /send

<b>🆔 آيديك:</b> <code>{user_id}</code>
""", reply_markup=markup, parse_mode="HTML")
@bot.message_handler(func=lambda message: message.text == "تمويل وكيل" and is_admin(message.from_user.id))
def handle_agent_funding_button(message):
    # 📌 لا تحتاج لفحص صلاحية الأدمن هنا إذا تم فحصها في message_handler
    manage_agent_balance_start(message)

def manage_agent_balance_start(message):
    sender_id = message.from_user.id # آيدي المرسل (رقم)
    
    # 💡 التصحيح: استخدام الدالة is_admin أو التحقق يدوياً
    if not is_admin(sender_id):
        # يمكنك إضافة رسالة خطأ هنا إذا أردت
        return bot.send_message(message.chat.id, "❌ صلاحيات غير كافية.") 

    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("💰 إضافة رصيد لوكيل", callback_data="admin_add_agent_balance"),
        types.InlineKeyboardButton("💸 خصم رصيد من وكيل", callback_data="admin_deduct_agent_balance"),
        types.InlineKeyboardButton("❌ إلغاء", callback_data="cancel_agent_balance_manage")
    )
    
    bot.send_message(message.chat.id, 
                     "🛠 **لوحة تحكم أرصدة الوكلاء**\n\nالرجاء اختيار نوع العملية:", 
                     reply_markup=markup, 
                     parse_mode="Markdown")
# --- 3. معالجات الأزرار الداخلية (Callback Handlers) ---

@bot.callback_query_handler(func=lambda call: call.data == "admin_add_agent_balance")
def start_add_agent_balance(call):
    sender_id = str(call.from_user.id) # 🛑 نستخدم الآيدي كنص كمفتاح تخزين آمن
    
    agent_temp_data[sender_id] = {'action': 'add', 'target_agent_id': None, 'amount': None}
    
    msg = bot.edit_message_text(
        "💰 **عملية إضافة رصيد لوكيل**\n\nالرجاء إرسال **آيدي الوكيل** الذي تريد إضافة النقاط له:", 
        call.message.chat.id, 
        call.message.message_id, 
        parse_mode="Markdown"
    )
    bot.register_next_step_handler(msg, get_agent_id_for_balance, action='add')

@bot.callback_query_handler(func=lambda call: call.data == "admin_deduct_agent_balance")
def start_deduct_agent_balance(call):
    sender_id = str(call.from_user.id) # 🛑 نستخدم الآيدي كنص كمفتاح تخزين آمن
    
    agent_temp_data[sender_id] = {'action': 'deduct', 'target_agent_id': None, 'amount': None}
    
    msg = bot.edit_message_text(
        "💸 **عملية خصم رصيد من وكيل**\n\nالرجاء إرسال **آيدي الوكيل** الذي تريد خصم النقاط منه:", 
        call.message.chat.id, 
        call.message.message_id, 
        parse_mode="Markdown"
    )
    bot.register_next_step_handler(msg, get_agent_id_for_balance, action='deduct')

@bot.callback_query_handler(func=lambda call: call.data == "cancel_agent_balance_manage")
def cancel_agent_balance_manage_callback(call):
    sender_id = str(call.from_user.id)
    if sender_id in agent_temp_data:
        del agent_temp_data[sender_id]
    try:
        bot.edit_message_text("❌ تم إلغاء عملية إدارة رصيد الوكيل.", call.message.chat.id, call.message.message_id)
        bot.answer_callback_query(call.id, "تم الإلغاء.")
    except Exception:
          bot.answer_callback_query(call.id, "تم الإلغاء.")


# --- 4. استلام آيدي الوكيل والتحقق منه ---
def get_agent_id_for_balance(message, action):
    sender_id = str(message.from_user.id)
    agents = load_agents()

    if sender_id not in agent_temp_data or agent_temp_data[sender_id]['action'] != action:
        return bot.send_message(message.chat.id, "❌ انتهت صلاحية العملية. يرجى البدء مجدداً بزر 'تمويل وكيل'.")

    target_agent_id = message.text.strip()

    if not target_agent_id.isdigit() or target_agent_id not in agents:
        msg = bot.send_message(message.chat.id, "❌ الآيدي غير صحيح أو ليس آيدي وكيل مُسجل. أعد إرسال آيدي الوكيل:")
        return bot.register_next_step_handler(msg, get_agent_id_for_balance, action)

    # حفظ الآيدي المستهدف مؤقتاً
    agent_temp_data[sender_id]['target_agent_id'] = target_agent_id
    agent_data = agents[target_agent_id]
    
    # عرض معلومات الوكيل المستهدف
    operation_label = 'إضافتها' if action == 'add' else 'خصمها'
    info_msg = (
        f"✅ **تم تحديد الوكيل:**\n\n"
        f"🆔 الآيدي: <code>{target_agent_id}</code>\n"
        f"👤 الاسم: {agent_data.get('name', 'غير معروف')}\n"
        f"💰 رصيده الحالي: **{agent_data.get('balance', 0)}** نقطة.\n\n"
        f"الآن، **كم عدد النقاط** التي تريد {operation_label}؟ (أرسل رقم موجب فقط)"
    )

    msg = bot.send_message(message.chat.id, info_msg, parse_mode="HTML")
                             
    # توجيه الخطوة التالية إلى التنفيذ النهائي
    bot.register_next_step_handler(msg, execute_agent_balance_operation)

# --- 5. دالة تنفيذ العملية وحفظ agents.json ---
def execute_agent_balance_operation(message):
    sender_id = str(message.from_user.id)
    agents = load_agents()
    
    if sender_id not in agent_temp_data:
        return bot.send_message(message.chat.id, "❌ انتهت صلاحية العملية.")
        
    operation_data = agent_temp_data[sender_id]
    target_agent_id = operation_data.get('target_agent_id')
    action = operation_data.get('action')

    # التحقق من القيمة المدخلة
    try:
        amount = int(message.text.strip())
        if amount <= 0:
            raise ValueError
    except ValueError:
        msg = bot.send_message(message.chat.id, "❌ قيمة النقاط غير صحيحة. يجب أن تكون عدداً موجباً. أعد إرسال عدد النقاط:")
        # إعادة توجيه لنفس الدالة
        return bot.register_next_step_handler(msg, execute_agent_balance_operation)

    # التحقق النهائي من الوكيل
    if target_agent_id not in agents:
        del agent_temp_data[sender_id]
        return bot.send_message(message.chat.id, "❌ خطأ: الوكيل المستهدف غير موجود.")

    # --- تنفيذ التعديل وحفظ agents.json ---
    try:
        current_balance = agents[target_agent_id].get('balance', 0)
        
        if action == 'add':
            new_balance = current_balance + amount
            operation_type_ar = "إضافة"
        elif action == 'deduct':
            # التحقق من الرصيد لمنع الرصيد السالب
            if current_balance < amount:
                del agent_temp_data[sender_id]
                return bot.send_message(message.chat.id, 
                                        f"❌ فشلت عملية الخصم! رصيد الوكيل الحالي ({current_balance} نقطة) غير كافٍ لخصم {amount} نقطة.", 
                                        parse_mode="Markdown")
            new_balance = current_balance - amount
            operation_type_ar = "خصم"
        else:
            raise Exception("نوع العملية غير معروف.")

        # تطبيق التعديل على القاموس
        agents[target_agent_id]['balance'] = new_balance
        
        # حفظ التغييرات في ملف agents.json
        save_agents(agents)

        # رسالة النجاح للمدير
        bot.send_message(message.chat.id, 
                          f"✅ **تمت عملية {operation_type_ar} بنجاح!**\n\n"
                          f"تم {operation_type_ar} **{amount}** نقطة من رصيد الوكيل <code>{target_agent_id}</code>.\n"
                          f"رصيده الجديد: **{new_balance}** نقطة.", 
                          parse_mode="HTML")
        
        # إشعار الوكيل نفسه
        try:
            bot.send_message(target_agent_id, 
                              f"🔔 **تحديث رصيد!**\n\n"
                              f"تم **{operation_type_ar} {amount}** نقطة من قبل الإدارة.\n"
                              f"رصيدك الجديد: **{new_balance}** نقطة.", 
                              parse_mode="Markdown")
        except Exception:
            pass
            
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ حدث خطأ غير متوقع أثناء التعديل: {str(e)}")
        
    finally:
        # مسح البيانات المؤقتة بعد الانتهاء
        if sender_id in agent_temp_data:
            del agent_temp_data[sender_id]

@bot.message_handler(func=lambda m: m.text in [ "🔒 حظر مستخدم", "🔓 إلغاء الحظر", "➕ إرسال نقاط", "🆕 إضافة سلعة", "🗑 حذف سلعة", "📊 عرض الإحصائيات", "خصم نقاط", "اذاعة", "رفع ادمن", "تصفير الكل","سجل الكوبون","➕ إضافة عداد","➖ مسح عداد" ,"🚫 إيقاف الإرسال", "✅ تفعيل الإرسال","انشاء كوبون","إيقاف البوت", "تشغيل البوت","إعادة ضبط المصنع","➕ تعيين نقاط الدعوة", "🎁 تعيين نقاط الهدية","📋 عرض جميع الإعدادات","🧼 تصفير الدعوة","📨 ارسال الى مستخدم", "➕ إضافة وكيل", "➖ إزالة وكيل", "📄 جلب الملفات", "تمويل وكيل","معلومات الوكيل"])
def handle_admin_actions(message):
    """معالج للتعامل مع جميع إجراءات الأدمن من الأزرار."""
    user_id = str(message.from_user.id)
    users = load_users()
    if user_id != str(ADMIN_IDS) and users.get(user_id, {}).get("role") not in ["admin", "owner"]:
        return
    if user_id != ADMIN_IDS and users.get(user_id, {}).get("role") != "admin":
        bot.send_message(message.chat.id, "❌ لا تملك صلاحية تنفيذ هذا الإجراء.")
        return
        
    action = message.text

    if action == "🆕 إضافة سلعة":
        msg = "أرسل اسم السلعة ثم فراغ ثم السعر (مثال: ساعة 100).\n*لإضافة سلعة عداد:* أرسل `عداد [القيمة] [السعر]` مثل: `عداد 100 1600`"
        bot.send_message(message.chat.id, msg)
        bot.register_next_step_handler(message, add_product)

    elif action == "تصفير الكل":
        reset_all_users_points(message)    
    elif action == "➕ إضافة عداد":
        bot.send_message(message.chat.id, "أرسل الآيدي متبوعاً بعدد النقاط التي تريد *إضافتها* لعداد a.json، مثلًا:\n`123456789 100`", parse_mode="Markdown")
        bot.register_next_step_handler(message, add_to_json)
    elif action == "سجل الكوبون":
        try:
            with open("coupons.json", "r", encoding="utf-8") as f:
                logs = f.readlines()  # آخر 20 سطر فقط
                if logs:
                    log_text = "".join(logs)
                    bot.send_message(message.chat.id, f"سجل العمليات للكوبون:\n\n{log_text}")
                else:
                    bot.send_message(message.chat.id, "لا يوجد عمليات حالياً.")
        except FileNotFoundError:
            bot.send_message(message.chat.id, "لم يتم العثور على ملف السجل.")    

    elif action == "➖ مسح عداد":
        bot.send_message(message.chat.id, "أرسل آيدي المستخدم لمسح قيمة عداده في a.json.")
        bot.register_next_step_handler(message, clear_a_json_count)
        
    elif action == "إعادة ضبط المصنع":
        msg = bot.send_message(message.chat.id, "⚠️ تحذير: سيتم مسح جميع البيانات (نقاط، مشتريات، إعدادات) وإعادة تعيين البوت.\nأرسل كلمة السر (`علي`) لتأكيد العملية.")
        bot.register_next_step_handler(msg, factory_reset_confirmation)

    elif action == "🔒 حظر مستخدم":
        msg = bot.send_message(message.chat.id, "أرسل آيدي المستخدم الذي تريد حظره:")
        bot.register_next_step_handler(msg, ban_user)
        
    elif action == "🔓 إلغاء الحظر":
        msg = bot.send_message(message.chat.id, "أرسل آيدي المستخدم الذي تريد إلغاء حظره:")
        bot.register_next_step_handler(msg, unban_user)

    elif action == "➕ إرسال نقاط":
        msg = bot.send_message(message.chat.id, "أرسل آيدي المستخدم وعدد النقاط التي تريد إرسالها (مثال: 12345 500):")
        bot.register_next_step_handler(msg, send_points_to_user)

    elif action == "خصم نقاط":
        msg = bot.send_message(message.chat.id, "أرسل آيدي المستخدم وعدد النقاط التي تريد خصمها (مثال: 12345 500):")
        bot.register_next_step_handler(msg, deduct_points)
        

    elif action == "🗑 حذف سلعة":
        products = load_products()
        if not products:
            bot.send_message(message.chat.id, "لا توجد سلع لحذفها.")
            return

        product_list = "\n".join([f"- {name}" for name in products.keys()])
        msg = bot.send_message(message.chat.id, f"أرسل اسم السلعة التي تريد حذفها بالضبط:\n{product_list}")
        bot.register_next_step_handler(msg, delete_product)

    elif action == "اذاعة":
        msg = bot.send_message(message.chat.id, "أرسل رسالة الإذاعة التي تريد إرسالها لجميع المستخدمين:")
        bot.register_next_step_handler(msg, broadcast_message)

    elif action == "📨 ارسال الى مستخدم":
        msg = bot.send_message(message.chat.id, "أرسل آيدي المستخدم ثم الرسالة (مثال: 12345 مرحبا بك):")
        bot.register_next_step_handler(msg, send_message_to_user)
        
    elif action == "🧼 تصفير الدعوة":
        msg = bot.send_message(message.chat.id, "أرسل آيدي المستخدم لتصفير عداد دعواته:")
        bot.register_next_step_handler(msg, clear_referrals)

    elif action == "➕ تعيين نقاط الدعوة":
        msg = bot.send_message(message.chat.id, "أرسل قيمة نقاط الدعوة الجديدة:")
        bot.register_next_step_handler(msg, set_referral_points)

    elif action == "🎁 تعيين نقاط الهدية":
        msg = bot.send_message(message.chat.id, "أرسل قيمة نقاط الهدية اليومية الجديدة:")
        bot.register_next_step_handler(msg, set_daily_gift_points)

    elif action == "🚫 إيقاف الإرسال":
        bot.send_message(message.chat.id, "تم إيقاف الإرسال التلقائي للعدادات.")
        config = load_config()
        config["auto_send_enabled"] = False
        save_config(config)

    elif action == "✅ تفعيل الإرسال":
        bot.send_message(message.chat.id, "تم تفعيل الإرسال التلقائي للعدادات.")
        config = load_config()
        config["auto_send_enabled"] = True
        save_config(config)

    elif action == "إيقاف البوت":
        msg = bot.send_message(message.chat.id, "🛑 أرسل سبب إيقاف البوت:")
        bot.register_next_step_handler(msg, get_stop_reason)

    elif action == "تشغيل البوت":
        bot.send_message(message.chat.id, "تم إعادة تشغيل البوت.")
        status = load_bot_status()
        status["active"] = True
        status["reason"] = "البوت في وضع التشغيل"
        status["resume_time"] = ""
        save_bot_status(status)

    elif action == "📊 عرض الإحصائيات":
        display_stats(message)
def reset_all_users_points(message):
    users = load_users()
    for uid in users:
        users[uid]["points"] = 0
    save_users(users)

    for uid in users:
        try:
            bot.send_message(uid, "⚠️ تم تصفير رصيدك من النقاط من قبل الإدارة.")
        except:
            continue

    bot.send_message(message.chat.id, "✅ تم تصفير النقاط لجميع المستخدمين وإبلاغهم.")
def delete_product(message):
    item_name = message.text.strip()
    products = load_products()

    if item_name in products:
        del products[item_name]
        save_products(products)
        bot.send_message(message.chat.id, f"✅ تم حذف السلعة: {item_name}")
    else:
        bot.send_message(message.chat.id, "❌ لم يتم العثور على السلعة بهذا الاسم.")

def factory_reset_confirmation(message):
    if message.text.strip().lower() == FACTORY_RESET_PASSWORD:
        # مسح جميع الملفات وإعادة إنشائها
        files_to_reset = ["users.json", "products.json", "a.json", "edit.json", "config.json", "bot_status.json", "coupons.json", "withdrawals.json"]
        for f in files_to_reset:
            if os.path.exists(f):
                os.remove(f)
        
        initialize_files() # إعادة إنشاء الملفات بالقيم الافتراضية
        
        bot.send_message(message.chat.id, "✅ تم إعادة ضبط المصنع بنجاح. تم مسح جميع بيانات المستخدمين والسلع والإعدادات.")
    else:
        bot.send_message(message.chat.id, "❌ كلمة السر غير صحيحة. تم إلغاء عملية إعادة ضبط المصنع.")

def get_stop_reason(message):
    reason = message.text.strip()
    msg = bot.send_message(message.chat.id, "⏱️ أرسل مدة الإيقاف (بالثواني أو الساعات):")
    bot.register_next_step_handler(msg, get_stop_duration, reason)

def get_stop_duration(message, reason):
    try:
        duration_input = message.text.strip()
        if duration_input.endswith("s"):
            seconds = int(duration_input[:-1])
        elif duration_input.endswith("h"):
            seconds = int(duration_input[:-1]) * 3600
        else:
            seconds = int(duration_input)
    except:
        bot.send_message(message.chat.id, "❌ أرسل وقت صحيح، مثل: 60s أو 1h أو فقط رقم.")
        return

    resume_time = (datetime.now() + timedelta(seconds=seconds)).strftime("%Y-%m-%d %H:%M:%S")
    save_bot_status({"active": False, "reason": reason, "resume_time": resume_time})

    msg = f"""❌ تم إيقاف البوت مؤقتاً.
السبب: {reason}
⏳ يعود للعمل في: {resume_time}"""

    # نشر للمستخدمين والقناة
    users = load_users()
    for uid in users:
        try:
            bot.send_message(uid, msg)
        except:
            continue
    bot.send_message(CHANNEL_ID, msg)

def display_stats(message):
    # ⚠️ ملاحظة: يجب أن تكون الدالتان load_users و load_data_a معرفتين في الكود
    users = load_users() # افترضنا وجود هذه الدالة لقراءة users
    total_users = len(users)
    total_points = sum(u.get("points", 0) for u in users.values())
    total_purchases = sum(u.get("purchases", 0) for u in users.values())
    
    a_data = load_data_a() # نستخدم دالة التحميل الآمنة
    
    total_a_points = 0
    # جمع نقاط العداد (points_to_add) فقط
    for user_id, user_data in a_data.items():
        # نتحقق من أن البيانات هي قاموس قبل المحاولة
        if isinstance(user_data, dict):
            try:
                # نستخرج قيمة points_to_add ونحولها إلى رقم
                points = int(user_data.get('points_to_add', 0))
                total_a_points += points
            except (ValueError, TypeError):
                # نتجاهل الأرصدة التالفة (مثل النصوص أو القواميس التي ليس بها الحقل)
                pass

    msg = f"""
📊 إحصائيات البوت:

👥 إجمالي المستخدمين: *{total_users}*
💰 إجمالي النقاط الموزعة: *{total_points}* نقطة
🛒 إجمالي المشتريات المنجزة: *{total_purchases}* عملية
➕ إجمالي نقاط العداد (a.json): *{total_a_points}* نقطة
"""
    bot.send_message(message.chat.id, msg, parse_mode="Markdown")

# ⚠️ يجب التأكد من وجود الدالة is_admin(user_id) ودوال load_...() و load_config() في كودك.

@bot.message_handler(func=lambda message: message.text == "النظام" and is_admin(message.from_user.id))
def show_system_status(message):
    chat_id = message.chat.id
    
    try:
        # تحميل جميع قواعد البيانات والإعدادات
        users = load_users()
        agents = load_agents()
        coupons = load_coupons()
        bot_status = load_bot_status()
        config_settings = load_config() # 📌 تم تحميل config.json
    except Exception as e:
        print(f"Error loading system data: {e}")
        return bot.send_message(chat_id, "❌ فشل تحميل بيانات النظام. تأكد من وجود جميع ملفات JSON.", parse_mode="HTML")

    # 1. إحصائيات المستخدمين والأدمن
    total_users = len(users)
    banned_users = 0
    admins_list = []
    
    for uid, data in users.items():
        if data.get("banned", False) is True:
            banned_users += 1
        if data.get("role", "user") in ["admin", "owner"] and str(uid) in ADMIN_IDS:
             # جمع معلومات الأدمن فقط إذا كان دوره 'admin' أو 'owner' ومدرج في القائمة
             username = data.get("username", "لا يوجد")
             name = data.get("name", "مستخدم غير مسجل")
             admins_list.append(f"• 👤 <a href='tg://user?id={uid}'>{name}</a> (@{username}) | <code>{uid}</code>")
    
    # 2. إحصائيات الوكلاء والكوبونات
    total_agents = len(agents)
    total_coupons = len(coupons)

    # 3. حالة تشغيل البوت وحالة الإرسال التلقائي
    is_active = bot_status.get("active", True)
    status_text = "قيد التشغيل ✅" if is_active else "متوقف ❌"
    reason = bot_status.get("reason", "لا يوجد سبب محدد")
    
    # 📌 جلب حالة الإرسال التلقائي
    is_auto_send_enabled = config_settings.get('auto_send_enabled', True)
    auto_send_status = f"{'مفعل ✅' if is_auto_send_enabled else 'متوقف ❌'}"
    
    # 4. رسالة حالة النظام
    status_message = f"""
⚙️ <b>حالة النظام والبيانات الإحصائية</b>

📊 <b>إحصائيات قاعدة البيانات:</b>
• إجمالي المستخدمين: <b>{total_users:,}</b>
• المستخدمون المحظورون: <b>{banned_users:,}</b> 🚫
• عدد الوكلاء: <b>{total_agents:,}</b> 💼
• عدد الكوبونات المتاحة: <b>{total_coupons:,}</b> 🏷️

🛡️ <b>بيانات الأدمن والإدارة:</b>
• إجمالي الأدمنز المسجلين: <b>{len(admins_list)}</b> ({len(ADMIN_IDS)} في الكود)
{'• لا يوجد أدمن مسجلين.' if not admins_list else '\n'.join(admins_list)}

⚙️ <b>حالة الإعدادات والتشغيل:</b>
• حالة تشغيل البوت: <b>{status_text}</b>
• سبب الإيقاف (إن وجد): <i>{reason}</i>
• حالة الإرسال التلقائي للعدادات: <b>{auto_send_status}</b> ⏱️
"""

    
    bot.send_message(chat_id, status_message, parse_mode="HTML")

def set_referral_points(message):
    try:
        points = int(message.text.strip())
        edit = load_edit()
        edit["referral_points"] = points
        save_edit(edit)
        bot.send_message(message.chat.id, f"✅ تم تعيين نقاط الدعوة الجديدة إلى: {points} نقطة.")
    except ValueError:
        bot.send_message(message.chat.id, "❌ خطأ: يجب أن تكون قيمة صحيحة.")

def set_daily_gift_points(message):
    try:
        points = int(message.text.strip())
        edit = load_edit()
        edit["daily_gift_points"] = points
        save_edit(edit)
        bot.send_message(message.chat.id, f"✅ تم تعيين نقاط الهدية اليومية الجديدة إلى: {points} نقطة.")
    except ValueError:
        bot.send_message(message.chat.id, "❌ خطأ: يجب أن تكون قيمة صحيحة.")

# الدالة المخصصة لإضافة العداد إلى a.json
def add_to_json(message):
    try:
        parts = message.text.split()
        if len(parts) != 2:
            bot.send_message(message.chat.id, "صيغة غير صحيحة. يجب أن تكون: [آيدي المستخدم] [عدد النقاط للعداد].")
            return

        target_user_id = parts[0]
        points_to_add = int(parts[1])

        a_data = load_a_json()
        
        # 1. جلب التوقيت الحالي لـ بغداد
        current_time_baghdad = datetime.now(BAGHDAD_TZ)
        
        # 🔑 1. حساب تاريخ الانتهاء (سنة واحدة من تاريخ الإضافة الآن)
        expiry_time = current_time_baghdad + timedelta(days=365)

        # 2. التحقق من حالة العداد الحالية
        if target_user_id in a_data and not isinstance(a_data[target_user_id], int):
            # الحالة: المستخدم يمتلك عداداً بالتنسيق الجديد (Hashed)
            a_data[target_user_id]['points_to_add'] = a_data[target_user_id].get('points_to_add', 0) + points_to_add
            new_counter_value = a_data[target_user_id]['points_to_add']
        else:
            # الحالة: أول عداد للمستخدم أو كان بالتنسيق القديم (INT)
            current_count = a_data.get(target_user_id, 0)
            new_counter_value = current_count + points_to_add
            
            # إعداد البيانات بالتنسيق الجديد
            a_data[target_user_id] = {
                'points_to_add': new_counter_value,
                # تعيين التوقيت الحالي لـ بغداد كبداية لدورة الـ 24 ساعة
                'last_added_time': current_time_baghdad.isoformat()
            }
        
        # 🔑 2. تحديث تاريخ الانتهاء (يتم في كلتا الحالتين)
        a_data[target_user_id]['expiry_date'] = expiry_time.strftime('%Y-%m-%d %H:%M:%S')
        
        save_a_json(a_data)

        expiry_date_display = expiry_time.strftime('%Y-%m-%d') # لغرض العرض
        
        # --------------------------------------------------------
        # 🔑 الإشعار للمستخدم المستهدف
        # --------------------------------------------------------
        try:
            bot.send_message(
                int(target_user_id),
                f"🎉 **إشعار إضافة عداد يدوي!** 🎉\n\n"
                f"قام المسؤول بإضافة عداد إليك يدوياً:\n"
                f"▪️ **القيمة المضافة:** {points_to_add:,} نقطة\n"
                f"▪️ **إجمالي العداد الحالي:** {new_counter_value:,} نقطة\n"
                f"▪️ **تاريخ الانتهاء الجديد:** {expiry_date_display}\n\n"
                f"_تم تمديد صلاحية العداد لمدة سنة كاملة من تاريخ الإضافة._",
                parse_mode="Markdown"
            )
        except Exception as user_e:
            # إذا كان المستخدم قد حظر البوت
            print(f"❌ فشل إرسال إشعار إضافة العداد إلى المستخدم {target_user_id}: {user_e}")

        # 🔑 3. رسالة تأكيد النجاح للأدمن
        bot.send_message(message.chat.id, 
                          f"✅ تم إضافة {points_to_add} نقطة إلى عداد المستخدم `{target_user_id}` في ملف a.json.\n"
                          f"القيمة الإجمالية الآن: **{new_counter_value}** نقطة.\n"
                          f"🎉 **تم تفعيل العداد لمدة سنة! سينتهي في: {expiry_date_display}**\n"
                          f"🔔 **تم إرسال إشعار للمستخدم بنجاح.**", 
                          parse_mode="Markdown")
        
    except ValueError:
        bot.send_message(message.chat.id, "❌ خطأ: الآيدي يجب أن يكون رقمياً والعداد يجب أن يكون رقماً صحيحاً.")
    except Exception as e:
        bot.send_message(message.chat.id, f"حدث خطأ غير متوقع: {str(e)}")

# ----------------------------------------------------------------------
# الدالة المخصصة لمسح عداد a.json (تصفير القيمة مع الحفاظ على الهيكل)
# ----------------------------------------------------------------------
def clear_a_json_count(message):
    target_user_id = message.text.strip()
    a_data = load_a_json()
    
    # 1. التحقق من وجود المستخدم
    if target_user_id in a_data:
        
        # 2. التعامل مع التنسيق الجديد
        if isinstance(a_data[target_user_id], dict) and 'points_to_add' in a_data[target_user_id]:
            
            # إذا كان بالتنسيق الجديد، نصفر القيمة فقط ونحافظ على وقت آخر إضافة
            a_data[target_user_id]['points_to_add'] = 0
            
            save_a_json(a_data)
            bot.send_message(message.chat.id, 
                             f"✅ تم مسح عداد المستخدم `{target_user_id}` في ملف a.json. القيمة أصبحت 0.")
            
        else:
            # التعامل مع التنسيق القديم (INT) أو أي شيء آخر غير معروف
            a_data[target_user_id] = 0
            save_a_json(a_data)
            bot.send_message(message.chat.id, 
                             f"✅ تم مسح عداد المستخدم `{target_user_id}` في ملف a.json. القيمة أصبحت 0.")
    else:
        bot.send_message(message.chat.id, f"❌ المستخدم `{target_user_id}` ليس لديه قيمة في ملف a.json.")

# دالة إضافة السلعة (تم تعديلها لدعم منطق العداد)
def add_product(message):
    try:
        parts = message.text.split()
        if len(parts) < 2:
            bot.send_message(message.chat.id, "صيغة غير صحيحة. يجب أن تكون: [اسم السلعة] [السعر] أو [عداد القيمة] [السعر].")
            return

        price = int(parts[-1])
        item_full_name = " ".join(parts[:-1]) 
        
        counter_value = 0
        is_counter_item = False
        
        # منطق التحقق من صيغة العداد: "عداد [القيمة]"
        name_parts = item_full_name.split()
        if len(name_parts) >= 2 and name_parts[0].lower() == "عداد":
             try:
                # القيمة تكون في الجزء التالي مباشرة
                counter_value = int(name_parts[1]) 
                is_counter_item = True
             except ValueError:
                 pass 

        products = load_products()
        
        products[item_full_name.strip()] = {
            "price": price, 
            "is_counter": is_counter_item, 
            "counter": counter_value
        }
        save_products(products)

        bot.send_message(message.chat.id, f"✅ تم إضافة السلعة: {item_full_name.strip()} بسعر {price} نقطة. (سلعة عداد: {'نعم' if is_counter_item else 'لا'})")

    except ValueError:
        bot.send_message(message.chat.id, "❌ خطأ: السعر أو العداد يجب أن يكون رقماً صحيحاً.")
    except Exception as e:
        bot.send_message(message.chat.id, f"حدث خطأ غير متوقع: {str(e)}")
        
# --- الدوال الأساسية المتبقية (Top, Info, Help, Broadcast, إلخ) ---
# يجب أن يكون هذا المعالج موجوداً لكي تبدأ العملية

@bot.message_handler(commands=['top'], func=lambda message: is_admin(message.from_user.id))
def top_users(message):
    try:
        users = load_users() # ⚠️ تأكد من تعريف دالة load_users()
    except NameError:
        return bot.send_message(message.chat.id, "❌ خطأ داخلي: قاعدة بيانات المستخدمين غير متوفرة.", parse_mode="HTML")
    
    # ----------------------------------------
    # 📌 الإحصائيات الجديدة المطلوبة
    # ----------------------------------------
    total_users = 0
    banned_users = 0
    total_points = 0
    
    user_list = []
    
    for uid, data in users.items():
        total_users += 1
        
        # التأكد من أن 'points' هي قيمة قابلة للفرز (رقم)
        points = data.get("points", 0)
        if not isinstance(points, (int, float)):
            points = 0
        
        total_points += points
        
        # حساب عدد المحظورين
        if data.get("banned", False) is True:
            banned_users += 1
            
        user_list.append({
            "id": uid,
            "name": data.get("name", "مستخدم"),
            "points": points,
            "username": data.get("username", None),
            "is_banned": data.get("banned", False) # إضافة حالة الحظر
        })

    user_list.sort(key=lambda x: x["points"], reverse=True)
    
    # ----------------------------------------
    # 📌 بناء رسالة الإحصائيات
    # ----------------------------------------
    stats_msg = (
        "📊 <b>إحصائيات عامة عن المستخدمين:</b>\n"
        f"• العدد الإجمالي: <b>{total_users:,}</b> مستخدم\n"
        f"• المستخدمون المحظورون: <b>{banned_users:,}</b> مستخدم\n"
        f"• إجمالي النقاط الموزعة: <b>{int(total_points):,}</b> نقطة\n\n"
        "---------------------------------------\n"
    )

    # ----------------------------------------
    # 📌 بناء رسالة المتصدرين
    # ----------------------------------------
    top_msg = "🏆 <b>قائمة المتصدرين بالنقاط (أعلى 10):</b> 🏆\n\n"
    
    if not user_list:
        final_msg = stats_msg + "لا يوجد مستخدمون مسجلون بعد."
    else:
        for i, user in enumerate(user_list[:10]): 
            
            emoji = "🥇" if i == 0 else "🥈" if i == 1 else "🥉" if i == 2 else f"<b>{i + 1}</b>"
            
            # إضافة إشارة الحظر إن وجدت
            ban_indicator = " 🚫" if user['is_banned'] else "" 
            
            if user['username']:
                # إنشاء رابط Mention باستخدام HTML
                display_name = f"<a href='https://t.me/{user['username']}'>@{user['username']}</a>"
            else:
                # رابط Mention بالاسم في حال عدم وجود يوزر
                display_name = f"<a href='tg://user?id={user['id']}'>{user['name']}</a>"
            
            points_display = f"<b>{user['points']:,}</b>" # تنسيق الرقم بفواصل

            top_msg += f"{emoji} {display_name}{ban_indicator} | {points_display} نقطة\n"
            
        final_msg = stats_msg + top_msg


    bot.send_message(message.chat.id, final_msg, parse_mode="HTML")




# ⚠️ تأكد من وجود دالة is_admin(user_id) ودوال load_a_json() و load_loans() ودالة get_badge(user_data) في كودك.

@bot.message_handler(commands=['info'], func=lambda message: is_admin(message.from_user.id))
def get_user_info(message):
    chat_id = message.chat.id
    
    # رسالة للمستخدم
    msg = bot.send_message(chat_id, "أرسل **آيدي المستخدم** الذي تريد الحصول على معلوماته:", parse_mode="Markdown")
    
    # تسجيل الخطوة التالية
    bot.register_next_step_handler(msg, show_user_info)

def show_user_info(message):
    # 🛑 تحقق إضافي لضمان أن العملية تُجرى من الأدمن
    if not is_admin(message.from_user.id):
        return bot.send_message(message.chat.id, "❌ أنت لست المسؤول لإكمال هذه العملية.")
        
    target_id = message.text.strip()
    chat_id = message.chat.id
    
    try:
        # تحميل البيانات
        users = load_users()
        a_data = load_a_json()
        loans_data = load_loans() 
    except NameError:
        return bot.send_message(chat_id, "❌ خطأ: فشل تحميل قاعدة البيانات.", parse_mode="HTML")
    except Exception as e:
        print(f"Error loading data: {e}")
        return bot.send_message(chat_id, "❌ خطأ غير متوقع أثناء تحميل البيانات.", parse_mode="HTML")
    
    if target_id in users:
        u = users[target_id]
        
        # 1. بيانات العداد (a.json)
        counter_entry = a_data.get(target_id)
        counter_value = 0
        expiry_date = "لا يوجد"
        
        if isinstance(counter_entry, dict):
            counter_value = counter_entry.get('points_to_add', 0)
            expiry_date = counter_entry.get('expiry_date', 'لا يوجد')
            # تنسيق تاريخ الانتهاء إذا كان موجوداً
            if expiry_date not in ['لا يوجد', 'expired', None] and 'T' in expiry_date:
                try:
                    # قص الجزء الثاني من التاريخ ليصبح أكثر وضوحاً
                    expiry_date = expiry_date.split('T')[0]
                except:
                    pass
        elif isinstance(counter_entry, int):
            counter_value = counter_entry
        
        # 2. معلومات القرض النشط
        user_loans = loans_data.get(target_id, [])
        active_loan = next((loan for loan in user_loans if loan['status'] == 'active'), None)
        
        loan_info = "لا يوجد"
        if active_loan:
            loan_amount = active_loan['amount']
            due_date = active_loan['due_date'].split(' ')[0] # فقط التاريخ
            loan_info = f"<b>{loan_amount:,}</b> نقطة (يستحق: {due_date})"
            
        # 3. الشارة
        badge = get_badge(u) # ⚠️ يجب أن تكون هذه الدالة معرفة
        
        info_msg = f"""
<b>ℹ️ معلومات المستخدم:</b>
 
🆔 الآيدي: <code>{target_id}</code>
👤 الاسم: {u.get('name', 'غير معروف')}
🔎 المعرف: @{u.get('username', 'لا يوجد')}
 
<b>بيانات النقاط والإحصائيات:</b>
💰 الرصيد: <b>{u.get('points', 0):,}</b> نقطة
🤝 الدعوات: {u.get('referrals', 0)}
🛒 المشتريات: {u.get('purchases', 0)}
🏅 الشارة: {badge}
 
<b>حالة العداد (a.json):</b>
🔢 قيمة العداد التلقائي: <b>{counter_value:,}</b> نقطة
📅 تاريخ الانتهاء: <b>{expiry_date}</b>
 
<b>بيانات القروض:</b>
🏦 القرض النشط: {loan_info}
 
<b>الحالة الإدارية:</b>
🚫 محظور: {'<b>نعم ❌</b>' if u.get('banned', False) else 'لا ✅'}
⭐ الدور: <b>{u.get('role', 'user')}</b>
"""
        bot.send_message(chat_id, info_msg, parse_mode="HTML")
    else:
        bot.send_message(chat_id, f"❌ لم يتم العثور على مستخدم بالآيدي: <code>{target_id}</code>", parse_mode="HTML") 


def ban_user(message):
    target_id = message.text.strip()
    users = load_users()
    if target_id in users:
        users[target_id]["banned"] = True
        save_users(users)
        bot.send_message(message.chat.id, f"✅ تم حظر المستخدم ذو الآيدي: {target_id}")
        try:
            bot.send_message(target_id, "❌ لقد تم حظرك من استخدام هذا البوت.")
        except telebot.apihelper.ApiTelegramException: pass
    else:
        bot.send_message(message.chat.id, f"❌ لا يوجد مستخدم بالآيدي: {target_id}")

def unban_user(message):
    target_id = message.text.strip()
    users = load_users()
    if target_id in users:
        users[target_id]["banned"] = False
        save_users(users)
        bot.send_message(message.chat.id, f"✅ تم إلغاء حظر المستخدم ذو الآيدي: {target_id}")
        try:
            bot.send_message(target_id, "✅ تم إلغاء الحظر، يمكنك الآن استخدام البوت.")
        except telebot.apihelper.ApiTelegramException: pass
    else:
        bot.send_message(message.chat.id, f"❌ لا يوجد مستخدم بالآيدي: {target_id}")

def send_points_to_user(message):
    try:
        target_id, points_str = message.text.split()
        points = int(points_str)
        users = load_users()
        if target_id in users:
            users[target_id]["points"] += points
            save_users(users)
            bot.send_message(message.chat.id, f"✅ تم إرسال {points} نقطة للمستخدم: {target_id}")
            try:
                bot.send_message(target_id, f"🎉 تم إضافة {points} نقطة إلى رصيدك من قبل الأدمن.\nرصيدك الحالي: {users[target_id]['points']}")
            except telebot.apihelper.ApiTelegramException: pass
        else:
            bot.send_message(message.chat.id, f"❌ لا يوجد مستخدم بالآيدي: {target_id}")
    except ValueError:
        bot.send_message(message.chat.id, "❌ صيغة غير صحيحة. يجب أن تكون: [آيدي المستخدم] [عدد النقاط].")

def deduct_points(message):
    try:
        target_id, points_str = message.text.split()
        points = int(points_str)
        users = load_users()
        if target_id in users:
            users[target_id]["points"] = max(0, users[target_id]["points"] - points)
            save_users(users)
            bot.send_message(message.chat.id, f"✅ تم خصم {points} نقطة من المستخدم: {target_id}")
            try:
                bot.send_message(target_id, f"⚠️ تم خصم {points} نقطة من رصيدك من قبل الأدمن.\nرصيدك الحالي: {users[target_id]['points']}")
            except telebot.apihelper.ApiTelegramException: pass
        else:
            bot.send_message(message.chat.id, f"❌ لا يوجد مستخدم بالآيدي: {target_id}")
    except ValueError:
        bot.send_message(message.chat.id, "❌ صيغة غير صحيحة. يجب أن تكون: [آيدي المستخدم] [عدد النقاط].")

def promote_sender(message):
    target_id = message.text.strip()
    users = load_users()
    if target_id in users:
        users[target_id]["role"] = "sender"
        save_users(users)
        bot.send_message(message.chat.id, f"✅ تم تعيين المستخدم {target_id} كـ 'مرسل'.")
    else:
        bot.send_message(message.chat.id, f"❌ لا يوجد مستخدم بالآيدي: {target_id}")

def demote_sender(message):
    target_id = message.text.strip()
    users = load_users()
    if target_id in users:
        users[target_id]["role"] = "user"
        save_users(users)
        bot.send_message(message.chat.id, f"✅ تم إزالة صلاحية 'المرسل' من المستخدم {target_id}.")
    else:
        bot.send_message(message.chat.id, f"❌ لا يوجد مستخدم بالآيدي: {target_id}")

def broadcast_message(message):
    broadcast_text = message.text
    users = load_users()
    success_count = 0
    fail_count = 0
    
    for uid in users.keys():
        try:
            bot.send_message(uid, broadcast_text)
            success_count += 1
        except telebot.apihelper.ApiTelegramException:
            fail_count += 1
    
    bot.send_message(message.chat.id, f"✅ تم الانتهاء من الإذاعة.\nتم الإرسال بنجاح إلى: {success_count}\nفشل الإرسال إلى: {fail_count}")

def send_message_to_user(message):
    try:
        parts = message.text.split(maxsplit=1)
        if len(parts) != 2:
            bot.send_message(message.chat.id, "صيغة غير صحيحة. يجب أن تكون: [آيدي المستخدم] [الرسالة].")
            return

        target_id = parts[0]
        msg_text = parts[1]
        
        try:
            bot.send_message(target_id, f"📬 رسالة خاصة من الأدمن:\n\n{msg_text}")
            bot.send_message(message.chat.id, f"✅ تم إرسال الرسالة بنجاح للمستخدم: {target_id}")
        except telebot.apihelper.ApiTelegramException as e:
            bot.send_message(message.chat.id, f"❌ فشل إرسال الرسالة للمستخدم {target_id}. قد يكون المستخدم قد حظر البوت. (الخطأ: {e})")
            
    except Exception as e:
        bot.send_message(message.chat.id, f"حدث خطأ غير متوقع: {str(e)}")

def clear_referrals(message):
    target_id = message.text.strip()
    users = load_users()
    if target_id in users:
        users[target_id]["referrals"] = 0
        save_users(users)
        bot.send_message(message.chat.id, f"✅ تم تصفير عداد دعوات المستخدم {target_id}.")
    else:
        bot.send_message(message.chat.id, f"❌ لا يوجد مستخدم بالآيدي: {target_id}")
        

####3
# --- دوال إدارة بيانات الوكلاء (Agents) ---
AGENTS_FILE = 'agents.json'

def load_agents():
    """تحميل بيانات الوكلاء من ملف JSON."""
    if not os.path.exists(AGENTS_FILE):
        return {}
    with open(AGENTS_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_agents(agents_data):
    """حفظ بيانات الوكلاء في ملف JSON."""
    with open(AGENTS_FILE, 'w', encoding='utf-8') as f:
        json.dump(agents_data, f, indent=4, ensure_ascii=False)

# لحفظ بيانات التحويل المؤقتة للوكلاء: {sender_id: {'target_id': ID, 'amount': X}}
agent_temp_data = {}
# --- دالة معالج الأمر /agent (لعرض معلومات الوكيل) ---
@bot.message_handler(commands=['agent'])
def agent_info_command(message):
    user_id = str(message.from_user.id)
    agents = load_agents()
    
    # 1. التحقق من أن المستخدم وكيل
    if user_id not in agents:
        bot.send_message(message.chat.id, "❌ عذراً، هذا الأمر مخصص للوكلاء فقط.")
        return

    agent_data = agents[user_id]
    
    # 2. بناء رسالة المعلومات
    agent_msg = f"""
<b>✨ مرحباً بك أيها الوكيل {agent_data.get('name', 'الوكيل')}!</b>

<b>📋 معلومات حساب الوكيل:</b>
<b>🆔 آيدي الوكيل:</b> <code>{user_id}</code>
<b>👤 الاسم:</b> {agent_data.get('name', 'غير معروف')}
<b>🔎 المعرف:</b> @{message.from_user.username or 'لا يوجد'}

<b>💰 رصيد التحويل المتاح:</b> {agent_data.get('balance', 0)} نقطة
<b>⭐ الدور:</b> {agent_data.get('role', 'Agent')}

<b>التعليمات:</b>
لبدء إرسال النقاط، استخدم الأمر:
<code>/send</code>
"""
    
    # 3. إرسال الرسالة
    bot.send_message(message.chat.id, 
                     agent_msg,
                     parse_mode="HTML",
                     disable_web_page_preview=True)
# --- 1. دالة معالج الأمر /send (البدء بطلب الآيدي) ---
@bot.message_handler(commands=['send'])
def start_send_process(message):
    sender_id = str(message.from_user.id)
    agents = load_agents()
    
    # التحقق من أن المرسل وكيل (موجود في agents.json)
    if sender_id not in agents:
        bot.send_message(message.chat.id, "❌ عذراً، لا تمتلك صلاحية استخدام هذا الأمر. هذا الأمر مخصص للوكلاء فقط.")
        return

    agent_data = agents[sender_id]
    
    # إعداد بيانات الوكيل المؤقتة
    agent_temp_data[sender_id] = {'target_id': None, 'amount': None, 'agent_name': agent_data.get('name', 'وكيل')}

    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("❌ إلغاء العملية", callback_data="cancel_agent_send"))

    msg = bot.send_message(message.chat.id, 
                           f"💰 **بدء إرسال النقاط**\n\nرصيدك المتاح للتحويل: **{agent_data.get('balance', 0)}** نقطة.\n\nالرجاء إرسال **آيدي المستخدم** الذي تريد التحويل له:", 
                           reply_markup=markup,
                           parse_mode="Markdown")
                           
    bot.register_next_step_handler(msg, get_target_id)


# --- معالج إلغاء العملية (Callback) ---
@bot.callback_query_handler(func=lambda call: call.data == "cancel_agent_send")
def cancel_agent_send_callback(call):
    sender_id = str(call.from_user.id)
    if sender_id in agent_temp_data:
        del agent_temp_data[sender_id]
        bot.edit_message_text("❌ تم إلغاء عملية إرسال النقاط.", call.message.chat.id, call.message.message_id)
        bot.answer_callback_query(call.id, "تم الإلغاء.")
    else:
        bot.answer_callback_query(call.id, "لا توجد عملية إرسال نشطة للإلغاء.")
# --- 2. استلام الآيدي وعرض معلومات المستلم ---
def get_target_id(message):
    sender_id = str(message.from_user.id)
    users = load_users()
    
    if sender_id not in agent_temp_data:
        return bot.send_message(message.chat.id, "❌ انتهت صلاحية العملية. يرجى البدء مجدداً بالأمر /send.")

    target_id = message.text.strip()
    
    if not target_id.isdigit():
        msg = bot.send_message(message.chat.id, "❌ الآيدي غير صحيح. يجب أن يكون رقماً. أعد إرسال الآيدي:")
        return bot.register_next_step_handler(msg, get_target_id)
        
    if target_id not in users:
        msg = bot.send_message(message.chat.id, f"❌ لا يوجد مستخدم بالآيدي: **{target_id}** في قاعدة بيانات البوت. أعد إرسال الآيدي:")
        return bot.register_next_step_handler(msg, get_target_id)

    # حفظ الآيدي المستهدف مؤقتاً
    agent_temp_data[sender_id]['target_id'] = target_id
    u = users[target_id]
    
    # عرض معلومات المستخدم المستهدف
    info_msg = (
        f"✅ **تم تحديد المستلم:**\n\n"
        f"🆔 الآيدي: <code>{target_id}</code>\n"
        f"👤 الاسم: {u.get('name', 'غير معروف')}\n"
        f"🔎 المعرف: @{u.get('username', 'لا يوجد')}\n\n"
        f"💰 رصيده الحالي: **{u.get('points', 0)}** نقطة."
    )
    
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("❌ إلغاء العملية", callback_data="cancel_agent_send"))
    
    msg = bot.send_message(message.chat.id, 
                           info_msg + "\n\nالآن، **كم عدد النقاط** التي تريد إرسالها؟ (أرسل رقم فقط)", 
                           reply_markup=markup,
                           parse_mode="HTML")
                           
    bot.register_next_step_handler(msg, get_amount_and_confirm)
# --- 3. استلام النقاط وتنفيذ التحويل ---
def get_amount_and_confirm(message):
    sender_id = str(message.from_user.id)
    agents = load_agents()
    users = load_users()
    
    if sender_id not in agent_temp_data:
        return bot.send_message(message.chat.id, "❌ انتهت صلاحية العملية. يرجى البدء مجدداً بالأمر /send.")
        
    try:
        amount = int(message.text.strip())
        if amount <= 0:
            raise ValueError
    except ValueError:
        msg = bot.send_message(message.chat.id, "❌ قيمة النقاط غير صحيحة. يجب أن تكون عدداً موجباً. أعد إرسال عدد النقاط:")
        return bot.register_next_step_handler(msg, get_amount_and_confirm)

    target_id = agent_temp_data[sender_id]['target_id']
    agent_data = agents[sender_id]
    
    # التحقق من رصيد الوكيل المخصص للتحويل
    agent_balance = agent_data.get('balance', 0)
    if agent_balance < amount:
        del agent_temp_data[sender_id]
        return bot.send_message(message.chat.id, 
                                f"❌ فشلت العملية! رصيدك كوكيل ({agent_balance} نقطة) غير كافٍ لإرسال **{amount}** نقطة.", 
                                parse_mode="Markdown")

    # --- تنفيذ عملية الإرسال (الخصم والإضافة) ---
    try:
        # 1. خصم النقاط من رصيد الوكيل (في agents.json)
        agents[sender_id]['balance'] -= amount
        save_agents(agents)
        
        # 2. إضافة النقاط للمستلم (في users.json)
        users[target_id]['points'] += amount
        save_users(users)

        # 3. إشعار المرسل (الوكيل)
        bot.send_message(message.chat.id, 
                         f"✅ **تم التحويل بنجاح!**\n\nتم إرسال **{amount}** نقطة إلى المستخدم <code>{target_id}</code>.\nرصيدك المتبقي كوكيل: **{agents[sender_id]['balance']}** نقطة.", 
                         parse_mode="HTML")

        # 4. إشعار المستلم
        try:
            agent_name = agent_data.get('name', 'وكيل/مدير')
            bot.send_message(target_id, 
                             f"💰 **تم استلام نقاط!**\n\nقام الوكيل **{agent_name}** بإرسال **{amount}** نقطة لحسابك.\nرصيدك الجديد: **{users[target_id]['points']}** نقطة.", 
                             parse_mode="Markdown")
        except Exception:
            pass

        # 5. تسجيل العملية في القناة (الإشراف)
        channel_msg = (
            f"**💸 عملية إرسال نقاط جديدة (وكيل):**\n\n"
            f"**الوكيل المُرسل:** {agent_data.get('name', 'غير معروف')} (@{message.from_user.username or 'لا يوجد'})\n"
            f"**آيدي الوكيل:** <code>{sender_id}</code>\n"
            f"**رصيده المتبقي:** {agents[sender_id]['balance']}\n"
            f"**--------------------**\n"
            f"**المستلم:** {users[target_id].get('name', 'غير معروف')} (@{users[target_id].get('username', 'لا يوجد')})\n"
            f"**آيدي المستلم:** <code>{target_id}</code>\n"
            f"**عدد النقاط المُرسلة:** {amount}\n"
        )
        bot.send_message(CHANNEL_ID2, channel_msg, parse_mode="HTML")

    except Exception as e:
        bot.send_message(message.chat.id, f"❌ حدث خطأ غير متوقع أثناء عملية الإرسال: {str(e)}")
        
    finally:
        # مسح البيانات المؤقتة بعد الانتهاء
        if sender_id in agent_temp_data:
            del agent_temp_data[sender_id]
##
AGENTS_FILE = 'agents.json'
def load_agents():
    """تحميل بيانات الوكلاء من agents.json."""
    if not os.path.exists(AGENTS_FILE):
        return {}
    try:
        # قراءة البيانات مع دعم UTF-8 للأحرف العربية
        with open(AGENTS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return {} # إرجاع قاموس فارغ في حال وجود خطأ في الملف

def save_agents(agents_data):
    """حفظ بيانات الوكلاء إلى agents.json."""
    # ensure_ascii=False للحفاظ على الأحرف العربية، و indent=4 للتنسيق
    with open(AGENTS_FILE, 'w', encoding='utf-8') as f:
        json.dump(agents_data, f, indent=4, ensure_ascii=False)
# #            
threading.Thread(target=loan_repayment_checker, daemon=True).start()   
@bot.message_handler(func=lambda message: message.text == "🛠️ إدارة الأدمنز" and is_admin(message.from_user.id))
def manage_admins_menu(message):
    
    admins_display = "\n".join([f"• <code>{uid}</code>" for uid in ADMIN_IDS])
    
    msg = f"""
🛠️ <b>إدارة الأدمنز</b>

الآيديات الحالية في قائمة ADMIN_IDS ({len(ADMIN_IDS)}):
{admins_display}

اختر الإجراء المطلوب:
"""
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("➕ رفع آيدي كـ أدمن", callback_data="add_admin_start"),
        types.InlineKeyboardButton("❌ إزالة آيدي من الأدمنز", callback_data="remove_admin_start")
    )
    
    bot.send_message(message.chat.id, msg, reply_markup=markup, parse_mode="HTML")
@bot.callback_query_handler(func=lambda call: call.data == "add_admin_start" and is_admin(call.from_user.id))
def add_admin_start(call):
    msg = bot.send_message(call.message.chat.id, "أرسل **آيدي المستخدم** الذي تريد رفعه كـ أدمن:")
    bot.register_next_step_handler(msg, add_admin_finish)
    bot.answer_callback_query(call.id)

def add_admin_finish(message):
    if not is_admin(message.from_user.id):
        return bot.send_message(message.chat.id, "❌ أنت لست المسؤول لإكمال هذه العملية.")
        
    new_admin_id = message.text.strip()
    
    if not new_admin_id.isdigit():
        return bot.send_message(message.chat.id, "❌ الآيدي المدخل غير صالح (يجب أن يكون رقماً).")

    new_admin_id = str(new_admin_id) # التأكد من أنه نصي ليطابق بيانات القائمة
    
    if new_admin_id in ADMIN_IDS:
        return bot.send_message(message.chat.id, f"⚠️ الآيدي <code>{new_admin_id}</code> هو أدمن بالفعل.")
        
    # 1. تحديث القائمة والحفظ
    new_admin_list = ADMIN_IDS + [new_admin_id]
    save_admin_ids(new_admin_list)
    
    # 2. تحديث دور المستخدم في users.json (لضمان ظهوره كأدمن في التقارير)
    users = load_users()
    if new_admin_id in users:
        users[new_admin_id]['role'] = 'admin'
        save_users(users)
        
    bot.send_message(message.chat.id, 
                     f"✅ تم رفع الآيدي <code>{new_admin_id}</code> كـ أدمن بنجاح.\n\n<b>الرجاء إعادة تشغيل البوت لتحديث الصلاحيات بشكل كامل في بعض الأحيان.</b>",
                     parse_mode="HTML")
@bot.callback_query_handler(func=lambda call: call.data == "remove_admin_start" and is_admin(call.from_user.id))
def remove_admin_start(call):
    msg = bot.send_message(call.message.chat.id, "أرسل **آيدي الأدمن** الذي تريد إزالته من القائمة:")
    bot.register_next_step_handler(msg, remove_admin_finish)
    bot.answer_callback_query(call.id)

def remove_admin_finish(message):
    if not is_admin(message.from_user.id):
        return bot.send_message(message.chat.id, "❌ أنت لست المسؤول لإكمال هذه العملية.")
        
    target_admin_id = message.text.strip()

    if not target_admin_id.isdigit():
        return bot.send_message(message.chat.id, "❌ الآيدي المدخل غير صالح (يجب أن يكون رقماً).")

    target_admin_id = str(target_admin_id)

    # لا يمكن إزالة نفسك أو الآيدي الأول (المالك)
    if target_admin_id == str(message.from_user.id):
        return bot.send_message(message.chat.id, "❌ لا يمكنك إزالة نفسك من قائمة الأدمنز.")
        
    if target_admin_id not in ADMIN_IDS:
        return bot.send_message(message.chat.id, f"⚠️ الآيدي <code>{target_admin_id}</code> ليس موجوداً في قائمة الأدمنز أصلاً.")
        
    # 1. تحديث القائمة والحفظ
    new_admin_list = [uid for uid in ADMIN_IDS if uid != target_admin_id]
    save_admin_ids(new_admin_list)
    
    # 2. تحديث دور المستخدم في users.json
    users = load_users()
    if target_admin_id in users:
        users[target_admin_id]['role'] = 'user' # إعادة دوره إلى مستخدم عادي
        save_users(users)
        
    bot.send_message(message.chat.id, 
                     f"✅ تم إزالة الآيدي <code>{target_admin_id}</code> من قائمة الأدمنز بنجاح.",
                     parse_mode="HTML")       
@bot.message_handler(commands=['userss'], func=lambda message: message.from_user.id == ADMIN_IDS)
def send_users_txt(message):
    chat_id = message.chat.id
    
    try:
        users = load_users() # ⚠️ تأكد من تعريف دالة load_users()
    except NameError:
        return bot.send_message(chat_id, "❌ خطأ داخلي: فشل تحميل قاعدة البيانات.")
    
    file_content = "قائمة المستخدمين:\n\n"

    for uid, data in users.items():
        name = data.get('name', 'غير معروف')
        username = f"@{data.get('username')}" if data.get('username') else "لا يوجد"
        points = data.get('points', 0)
        file_content += f"الاسم: {name}\nالمعرف: {username}\nالآيدي: {uid}\nالنقاط: {points}\n\n"

    file_path = "users_list.txt"
    
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(file_content)
    except Exception as e:
        return bot.send_message(chat_id, f"❌ خطأ أثناء إنشاء الملف: {e}")

    try:
        with open(file_path, "rb") as f:
            bot.send_document(chat_id, f, caption="✅ قائمة المستخدمين بالكامل.")
    except Exception as e:
        bot.send_message(chat_id, f"❌ خطأ أثناء إرسال الملف: {e}")
        
    import os
    if os.path.exists(file_path):
        os.remove(file_path)        
@bot.message_handler(commands=['s'], func=subscription_required)
def check_referrer(message):
    user_id = str(message.from_user.id)
    chat_id = message.chat.id
    
    try:
        users = load_users()
    except NameError:
        return bot.send_message(chat_id, "❌ خطأ داخلي: فشل تحميل قاعدة البيانات.")
    
    if user_id not in users:
        return bot.send_message(chat_id, "⚠️ لم يتم تسجيلك بعد. يرجى إرسال /start.")
        
    user_data = users[user_id]
    referrer_id = user_data.get("referrer_id")
    
    if not referrer_id or referrer_id == 'none':
        response = "🚫 **لم يتم دعوتك عن طريق أي مستخدم**.\n\n"
        response += "بإمكانك البدء بدعوة أصدقائك للحصول على نقاط إضافية الآن!"
        bot.send_message(chat_id, response, parse_mode="Markdown")
        return

    referrer_data = users.get(referrer_id)
    
    if not referrer_data:
        response = "⚠️ تم دعوتك، لكن **حساب الداعي غير موجود حالياً** في قاعدة البيانات."
        bot.send_message(chat_id, response, parse_mode="Markdown")
        return

    referrer_name = referrer_data.get('name', 'غير معروف')
    referrer_username = referrer_data.get('username', 'لا يوجد')
    
    
    message_text = (
        f"👥 **الداعي الخاص بك:**\n\n"
        f"▪️ **تمت دعوتك بواسطة:** `{referrer_name}`\n"
        f"▪️ **آيدي الداعي:** <code>{referrer_id}</code>\n"
        f"▪️ **المعرف (إن وجد):** @{referrer_username}\n\n"
        f"شكراً له لدعوتك!"
    )
    
    bot.send_message(chat_id, message_text, parse_mode="HTML")
# --------------------------------------------------------------------------
# 📌 دالة فحص انتهاء العدادات (يجب إضافتها في app.py / test.py)
# --------------------------------------------------------------------------
# --------------------------------------------------------------------------
# 📌 دالة فحص انتهاء العدادات (المصححة والمعدلة لـ 3 ثواني انتظار)
# --------------------------------------------------------------------------
def counter_expiry_checker():
    # ⚠️ تأكد أنك قمت بتعريف BAGHDAD_TZ = pytz.timezone('Asia/Baghdad') في أعلى الملف
    while True:
        try:
            # 1. الحصول على الوقت الحالي Naive
            current_dt_naive = datetime.now() 
            # 2. جعله Localized باستخدام كائن pytz (BAGHDAD_TZ)
            current_dt = BAGHDAD_TZ.localize(current_dt_naive)
            
            a_data = load_a_json()
            
            for user_id, data in a_data.items():
                expiry_str = data.get('expiry_date')
                
                # التحقق من وجود تاريخ انتهاء وكون العداد لا يزال فعالاً
                if expiry_str and expiry_str != 'expired' and data.get('points_to_add', 0) > 0:
                    
                    # 3. تحويل التاريخ المحفوظ إلى كائن Naive
                    naive_dt = datetime.strptime(expiry_str, '%Y-%m-%d %H:%M:%S')
                    
                    # 4. استخدام BAGHDAD_TZ.localize (للتصحيح)
                    expiry_dt = BAGHDAD_TZ.localize(naive_dt) 
                    
                    # إذا انتهت الصلاحية (التاريخ الحالي بعد تاريخ الانتهاء)
                    if current_dt > expiry_dt:
                        
                        # 1. إرسال رسالة الانتهاء
                        try:
                            bot.send_message(int(user_id), 
                                             "🔔 **إشعار انتهاء العداد:**\n\n"
                                             "انتهت صلاحية العداد الخاص بك (المشتريات الإضافية) لمدة سنة.\n"
                                             "لتجديد الخدمة، يرجى زيارة المتجر وشراء عداد جديد.", 
                                             parse_mode="Markdown")
                        except Exception as e:
                            print(f"❌ Failed to notify user {user_id} of expiry: {e}")
                        
                        # 2. إزالة بيانات العداد
                        data['points_to_add'] = 0 
                        data['expiry_date'] = 'expired'
                        
            save_a_json(a_data)
            
        except Exception as e:
            # تم إصلاح الخطأ السابق بتغيير 'timezone' إلى 'BAGHDAD_TZ'
            print(f"❌ Error in counter_expiry_checker: {e}")
            
        # 🔑 التعديل المطلوب: الانتظار لمدة 3 ثواني فقط
        time.sleep(3)
# 📌 يجب وضع هذا السطر قبل bot.polling() لضمان عمل الفحص التلقائي
threading.Thread(target=counter_expiry_checker, daemon=True).start() 
# ⚠️ يجب أن تكون دالة load_config() مُعرَّفة في بداية الكود.

@bot.message_handler(func=lambda message: message.text == "🔗 الاشتراك الإجباري" and is_admin(message.from_user.id))
def manage_forced_subscription(message):
    chat_id = message.chat.id
    config = load_config()
    
    # جلب الآيدي والرابط المحفوظين
    required_id = config.get('required_channel_id', REQUIRED_CHANNEL_ID) 
    required_link = config.get('required_channel_link', 'غير محدد')
    
    channel_info_msg = ""
    members_count = "غير متوفر"
    channel_name = "غير معروفة"

    try:
        # 🔑 محاولة جلب معلومات القناة من تيليجرام
        chat_object = bot.get_chat(required_id)
        channel_name = chat_object.title
        members_count = bot.get_chat_member_count(required_id)
        
        channel_info_msg = (
            f"• اسم القناة: <b>{channel_name}</b>\n"
            f"• عدد الأعضاء: <b>{members_count:,}</b> مشترك\n"
        )
    except Exception as e:
        channel_name = "⚠️ البوت ليس مشرفاً أو الآيدي غير صحيح."
        channel_info_msg = f"• حالة البوت في القناة: <b>{channel_name}</b>\n"
        print(f"Error fetching channel info: {e}")
        

    msg = f"""
🔗 <b>إعدادات الاشتراك الإجباري</b>

• آيدي القناة الحالية (للتحقق): <code>{required_id}</code>
• رابط القناة للعرض: <code>{required_link}</code>

{channel_info_msg}

لتغيير القناة، اضغط على الزر أدناه.
"""
    
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("🔄 تغيير القناة (آيدي + رابط)", callback_data="change_required_channel_id_start")
    )
    
    
    bot.send_message(chat_id, msg, reply_markup=markup, parse_mode="HTML")


# -------------------- دالة معالجة الإلغاء --------------------

@bot.callback_query_handler(func=lambda call: call.data == "cancel_admin_op" and is_admin(call.from_user.id))
def cancel_admin_operation(call):
    chat_id = call.message.chat.id
    
    # 1. حذف حالة المستخدم المؤقتة
    if chat_id in user_states:
        del user_states[chat_id]
        
    # 2. مسح الخطوات المعلقة (للتأكد)
    bot.clear_step_handler_by_chat_id(chat_id)
    
    # 3. تعديل الرسالة للإشعار بالإلغاء
    bot.edit_message_text(chat_id=chat_id, 
                          message_id=call.message.message_id, 
                          text="✅ **تم إلغاء العملية بنجاح.**",
                          parse_mode="HTML")
                          
    bot.answer_callback_query(call.id, "تم إلغاء العملية.")


# -------------------- خطوة 1: طلب الآيدي --------------------

@bot.callback_query_handler(func=lambda call: call.data == "change_required_channel_id_start" and is_admin(call.from_user.id))
def change_required_channel_id_start(call):
    chat_id = call.message.chat.id
    
    # لوحة مفاتيح مع زر إلغاء
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("❌ إلغاء العملية", callback_data="cancel_admin_op")
    )
    
    msg = bot.send_message(chat_id, 
                           "أرسل الآن **آيدي القناة الجديد** (مثال: `-100xxxxxxxxxx`).\n\n"
                           "<b>تأكد من أن البوت مشرف في القناة الجديدة.</b>", 
                           reply_markup=markup, 
                           parse_mode="HTML")
                           
    # تسجيل الخطوة التالية: حفظ الآيدي وطلب الرابط
    bot.register_next_step_handler(msg, save_required_channel_id_step)
    bot.answer_callback_query(call.id, "جارٍ البدء في عملية التغيير...")

# -------------------- خطوة 2: حفظ الآيدي وطلب الرابط --------------------

def save_required_channel_id_step(message):
    chat_id = message.chat.id
    
    if not is_admin(message.from_user.id):
        return bot.send_message(chat_id, "❌ أنت لست المسؤول لإكمال هذه العملية.")
        
    # 🛑 فحص أمر الإلغاء (لمعالجة إلغاء المستخدم عبر الكتابة)
    if message.text and message.text.startswith('/start'):
        return manage_forced_subscription(message)
        
    new_id_text = message.text.strip()
    
    # 1. التحقق من صحة الآيدي
    if not new_id_text.startswith('-100') or not new_id_text[1:].isdigit():
        return bot.send_message(chat_id, "❌ الآيدي غير صحيح. يجب أن يبدأ بـ `-100` ويليه أرقام فقط.")
    
    # 2. حفظ الآيدي مؤقتاً في حالة المستخدم للانتقال للخطوة التالية
    user_states[chat_id] = {'new_channel_id': new_id_text}
    
    # لوحة مفاتيح مع زر إلغاء
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("❌ إلغاء العملية", callback_data="cancel_admin_op")
    )
    
    # 3. طلب رابط القناة
    msg = bot.send_message(chat_id, 
                           "✅ تم حفظ الآيدي مؤقتاً. الآن، أرسل **رابط القناة (URL) أو اليوزر نيم**.\n"
                           "مثال: `https://t.me/my00002` أو `@my00002`",
                           reply_markup=markup, 
                           parse_mode="HTML")
    
    # تسجيل الخطوة التالية: حفظ الرابط والإنهاء
    bot.register_next_step_handler(msg, save_required_channel_link_finish)


# -------------------- خطوة 3: حفظ الرابط والإنهاء --------------------

def save_required_channel_link_finish(message):
    global REQUIRED_CHANNEL_ID 
    chat_id = message.chat.id
    
    if not is_admin(message.from_user.id):
        return bot.send_message(chat_id, "❌ أنت لست المسؤول لإكمال هذه العملية.")
    
    # 🛑 فحص أمر الإلغاء (لمعالجة إلغاء المستخدم عبر الكتابة)
    if message.text and message.text.startswith('/start'):
        return manage_forced_subscription(message)

    # 1. جلب الآيدي المحفوظ
    if chat_id not in user_states or 'new_channel_id' not in user_states[chat_id]:
        return bot.send_message(chat_id, "❌ فشلت العملية. لم يتم العثور على الآيدي المحفوظ. يرجى البدء من جديد.")

    new_id_text = user_states[chat_id]['new_channel_id']
    new_link_text = message.text.strip()
    
    # 2. تنظيف الرابط/اليوزر نيم
    if new_link_text.startswith('@'):
        new_link_text = f"https://t.me/{new_link_text.replace('@', '')}"
    elif not new_link_text.startswith('http'):
        new_link_text = f"https://t.me/{new_link_text}"
        
    # 3. تحديث وحفظ الإعدادات في config.json
    config = load_config()
    config['required_channel_id'] = new_id_text
    config['required_channel_link'] = new_link_text # حفظ الرابط الجديد
    save_config(config)
    
    # 4. تحديث المتغير العام في الذاكرة
    REQUIRED_CHANNEL_ID = new_id_text
    
    # 5. تنظيف حالة المستخدم
    del user_states[chat_id]

    # 6. رسالة النجاح
    bot.send_message(chat_id, 
                     f"✅ تم تحديث إعدادات قناة الاشتراك الإجباري بنجاح:\n"
                     f"• الآيدي: <code>{new_id_text}</code>\n"
                     f"• الرابط: {new_link_text}", 
                     parse_mode="HTML")
    
    # إعادة عرض قائمة الإدارة بعد التحديث
    manage_forced_subscription(message)
if __name__ == "__main__":
    bot.polling(none_stop=True)
