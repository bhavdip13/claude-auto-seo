"""
Claude Auto SEO — Global Festival Auto-Poster
Posts branded festival content at 1:00 AM on festival days.
Covers: India, USA, UK, Africa, Europe (Germany, France, Spain, Italy), and more.

Usage:
  python3 scripts/festival_poster.py --check-today       # Check today's festivals
  python3 scripts/festival_poster.py --check-upcoming 7  # Next 7 days
  python3 scripts/festival_poster.py --post-now          # Post today's festivals NOW
  python3 scripts/festival_poster.py --install-cron      # Install 1AM cron job
  python3 scripts/festival_poster.py --preview           # Preview without posting
"""

import os
import sys
import json
import re
import random
import subprocess
import requests
from datetime import datetime, date, timedelta
from typing import Dict, List, Optional, Tuple
from dotenv import load_dotenv

load_dotenv()

BASE_DIR  = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_FILE  = os.path.join(BASE_DIR, "data", "festival-log.json")
DATA_DIR  = os.path.join(BASE_DIR, "data")

# ── GLOBAL FESTIVAL CALENDAR ──────────────────────────────────────────────────
# Format: (month, day, name, regions, type, hashtags, colors)
# For moveable feasts: (month, day) = approximate — will be updated annually

FIXED_FESTIVALS = [

    # ══ INDIA ══════════════════════════════════════════════════════════════════
    (1,  14, "Makar Sankranti / Pongal / Lohri", ["India"], "major",
     ["#MakarSankranti", "#Pongal", "#Lohri", "#HarvestFestival", "#India"], "#FF6B35"),
    (1,  26, "Republic Day India", ["India"], "national",
     ["#RepublicDay", "#RepublicDayIndia", "#JaiHind", "#India75", "#ProudIndian"], "#FF9933"),
    (2,  14, "Valentine's Day", ["India","USA","UK","Europe","Africa"], "commercial",
     ["#ValentinesDay", "#ValentineDay2025", "#Love", "#HappyValentinesDay"], "#FF69B4"),
    (3,   8, "International Women's Day", ["India","USA","UK","Europe","Africa","Germany"], "global",
     ["#IWD2025", "#InternationalWomensDay", "#WomensDay", "#GenderEquality"], "#8B5CF6"),
    (3,  22, "Gudi Padwa / Telugu New Year", ["India"], "major",
     ["#GudiPadwa", "#TeluguNewYear", "#YugiYuga", "#HinduNewYear"], "#FF8C00"),
    (4,  13, "Baisakhi / Vaisakhi", ["India"], "major",
     ["#Baisakhi", "#Vaisakhi", "#HarvestFestival", "#Punjab", "#India"], "#FFD700"),
    (4,  14, "Ambedkar Jayanti / Tamil New Year", ["India"], "national",
     ["#AmbedkarJayanti", "#TamilNewYear", "#Puthandu"], "#1E40AF"),
    (5,  12, "Buddha Purnima", ["India"], "religious",
     ["#BuddhaPurnima", "#BuddhaJayanti", "#VesakDay", "#Peace"], "#FFD700"),
    (8,  15, "Independence Day India", ["India"], "national",
     ["#IndependenceDay", "#IndependenceDayIndia", "#JaiHind", "#HarAzaadHaiIndia"], "#FF9933"),
    (8,  26, "Krishna Janmashtami (approx)", ["India"], "religious",
     ["#Janmashtami", "#HappyJanmashtami", "#JaiShriKrishna", "#Krishnashtami"], "#1E40AF"),
    (9,   5, "Teachers Day India", ["India"], "cultural",
     ["#TeachersDay", "#HappyTeachersDay", "#ThankYouTeacher", "#GuruMantro"], "#4CAF50"),
    (10,  2, "Gandhi Jayanti", ["India"], "national",
     ["#GandhiJayanti", "#MahatmaGandhi", "#BaruDe", "#TruthAndNonviolence"], "#FF9933"),
    (10, 15, "Dussehra / Navratri (approx)", ["India"], "major",
     ["#Dussehra", "#Navratri", "#DurgaPuja", "#HappyDussehra", "#Navratri2025"], "#FF6B35"),
    (11,  1, "Diwali (approx)", ["India","UK","USA"], "major",
     ["#Diwali", "#HappyDiwali", "#DiwaliCelebrations", "#FestivalOfLights", "#Deepawali"], "#FFD700"),
    (11, 14, "Children's Day India", ["India"], "cultural",
     ["#ChildrensDay", "#HappyChildrensDay", "#BaalDiwas", "#Children"], "#FF6B35"),
    (12, 25, "Christmas", ["India","USA","UK","Europe","Africa","Germany"], "major",
     ["#Christmas", "#MerryChristmas", "#Christmas2025", "#Xmas", "#HappyChristmas"], "#C41E3A"),
    (12, 31, "New Year's Eve", ["India","USA","UK","Europe","Africa","Germany"], "global",
     ["#NewYearsEve", "#NYE2025", "#HappyNewYear2026", "#Countdown", "#NewYear"], "#FFD700"),
    (1,   1, "New Year's Day", ["India","USA","UK","Europe","Africa","Germany"], "global",
     ["#HappyNewYear", "#NewYear2026", "#NewYearNewBeginnings", "#2026"], "#FFD700"),

    # ══ USA ════════════════════════════════════════════════════════════════════
    (1,  15, "Martin Luther King Jr. Day (3rd Mon Jan)", ["USA"], "national",
     ["#MLKDay", "#MartinLutherKingJr", "#MLKDay2025", "#IHaveADream"], "#1E40AF"),
    (2,  17, "Presidents Day (3rd Mon Feb)", ["USA"], "national",
     ["#PresidentsDay", "#USA", "#AmericanHistory"], "#B22222"),
    (5,  26, "Memorial Day (Last Mon May)", ["USA"], "national",
     ["#MemorialDay", "#MemorialDay2025", "#HonorTheFallen", "#USA"], "#B22222"),
    (6,  19, "Juneteenth", ["USA"], "national",
     ["#Juneteenth", "#Juneteenth2025", "#FreedomDay", "#BlackHistory"], "#006400"),
    (7,   4, "Independence Day USA", ["USA"], "national",
     ["#IndependenceDay", "#4thOfJuly", "#July4th", "#USA", "#America"], "#B22222"),
    (9,   1, "Labor Day (1st Mon Sep)", ["USA"], "national",
     ["#LaborDay", "#LaborDay2025", "#WorkersDay", "#USA"], "#B22222"),
    (10, 31, "Halloween", ["USA","UK","Europe"], "cultural",
     ["#Halloween", "#Halloween2025", "#TrickOrTreat", "#HappyHalloween", "#Spooky"], "#FF6B35"),
    (11, 11, "Veterans Day", ["USA"], "national",
     ["#VeteransDay", "#VeteransDay2025", "#HonorVeterans", "#ThankYouVeterans"], "#B22222"),
    (11, 27, "Thanksgiving (4th Thu Nov)", ["USA","Canada"], "national",
     ["#Thanksgiving", "#Thanksgiving2025", "#HappyThanksgiving", "#Grateful"], "#FF8C00"),
    (11, 28, "Black Friday", ["USA","UK","Europe"], "commercial",
     ["#BlackFriday", "#BlackFriday2025", "#Deals", "#ShoppingDay", "#Sales"], "#000000"),
    (12,  1, "Cyber Monday (1st Mon Dec)", ["USA","UK"], "commercial",
     ["#CyberMonday", "#CyberMonday2025", "#OnlineDeals", "#Shopping"], "#1E40AF"),
    (12, 26, "Kwanzaa", ["USA"], "cultural",
     ["#Kwanzaa", "#HappyKwanzaa", "#Kwanzaa2025", "#AfricanHeritage"], "#006400"),

    # ══ UK ═════════════════════════════════════════════════════════════════════
    (3,  17, "St. Patrick's Day", ["UK","USA","Ireland"], "cultural",
     ["#StPatricksDay", "#StPaddysDay", "#Paddy", "#Irish", "#GreenDay"], "#006400"),
    (4,  23, "St. George's Day (UK)", ["UK"], "national",
     ["#StGeorgesDay", "#England", "#UK", "#StGeorge"], "#B22222"),
    (5,   5, "Early May Bank Holiday", ["UK"], "national",
     ["#BankHoliday", "#MayDay", "#UK"], "#003087"),
    (5,  26, "Spring Bank Holiday (UK)", ["UK"], "national",
     ["#BankHoliday", "#SpringBankHoliday", "#UK"], "#003087"),
    (8,  25, "Summer Bank Holiday (UK)", ["UK"], "national",
     ["#SummerBankHoliday", "#BankHoliday", "#UK"], "#003087"),
    (11,  5, "Guy Fawkes Night (Bonfire Night)", ["UK"], "cultural",
     ["#BonfireNight", "#GuyFawkes", "#Fireworks", "#RememberRemember", "#UK"], "#FF6B35"),
    (11, 11, "Remembrance Day (UK)", ["UK"], "national",
     ["#RemembranceDay", "#Poppy", "#LestWeForget", "#ArmedForces", "#UK"], "#B22222"),
    (12, 26, "Boxing Day (UK)", ["UK","Australia","Canada"], "national",
     ["#BoxingDay", "#BoxingDay2025", "#UK", "#Holidays"], "#003087"),

    # ══ AFRICA ═════════════════════════════════════════════════════════════════
    (2,  21, "Feast of Eid al-Fitr (approx)", ["Africa","India","UK"], "religious",
     ["#EidAlFitr", "#EidMubarak", "#Eid2025", "#RamadanKareem"], "#006400"),
    (5,  25, "Africa Day", ["Africa"], "cultural",
     ["#AfricaDay", "#AfricaDay2025", "#AfricanUnity", "#Africa", "#ProudAfrican"], "#006400"),
    (6,  16, "Youth Day South Africa", ["Africa"], "national",
     ["#YouthDay", "#YouthMonth", "#SouthAfrica", "#June16", "#Freedom"], "#007A4D"),
    (7,  18, "Nelson Mandela International Day", ["Africa","global"], "global",
     ["#MandelaDay", "#67Minutes", "#MandelaDay2025", "#Mandela", "#ChangeMaker"], "#006400"),
    (9,  24, "Heritage Day South Africa", ["Africa"], "national",
     ["#HeritageDay", "#BraaiDay", "#SouthAfrica", "#NationalBraaiDay"], "#007A4D"),
    (12, 11, "Eid al-Adha (approx)", ["Africa","India","UK"], "religious",
     ["#EidAlAdha", "#EidAdha2025", "#BakraEid", "#HappyEid"], "#006400"),

    # ══ EUROPE / GERMANY ══════════════════════════════════════════════════════
    (1,   6, "Epiphany / Three Kings Day", ["Europe","Germany","Spain","Italy"], "religious",
     ["#Epiphany", "#ThreeKingsDay", "#Heilige3Konige", "#Dreikonige"], "#8B5CF6"),
    (3,  19, "St. Joseph's Day (Spain/Italy)", ["Europe","Spain","Italy"], "religious",
     ["#SanGiuseppe", "#StJoseph", "#FathersDay"], "#FF6B35"),
    (4,  30, "Walpurgis Night (Germany)", ["Germany","Europe"], "cultural",
     ["#Walpurgisnacht", "#WalpurgisNight", "#Germany", "#Hexennacht"], "#8B5CF6"),
    (5,   1, "Labour Day / May Day", ["Europe","Germany","India","Africa"], "global",
     ["#MayDay", "#LabourDay", "#WorkersDay", "#TagDerArbeit", "#InternationalWorkersDay"], "#B22222"),
    (6,   3, "Whit Monday (Germany)", ["Germany","Europe"], "religious",
     ["#Pfingstmontag", "#WhitMonday", "#Pentecost", "#Germany"], "#4CAF50"),
    (6,  21, "Midsummer (Scandinavia/Europe)", ["Europe"], "cultural",
     ["#Midsommar", "#Midsummer", "#SummerSolstice", "#Europe", "#LongestDay"], "#FFD700"),
    (8,  15, "Assumption Day (Europe)", ["Europe","Germany","France","Italy"], "religious",
     ["#AssumptionDay", "#MariaHimmelfahrt", "#Europe"], "#1E40AF"),
    (10,  3, "German Unity Day", ["Germany"], "national",
     ["#TagDerDeutschenEinheit", "#GermanUnityDay", "#Deutschland", "#Unity"], "#000000"),
    (10,  4, "Oktoberfest (starts late Sep)", ["Germany","global"], "cultural",
     ["#Oktoberfest", "#Oktoberfest2025", "#Bavaria", "#Germany", "#Prost"], "#1E40AF"),
    (10, 31, "Reformation Day (Germany)", ["Germany"], "religious",
     ["#Reformationstag", "#ReformationDay", "#Luther", "#Germany"], "#FFD700"),
    (11,  1, "All Saints Day (Europe)", ["Europe","Germany","France","Spain"], "religious",
     ["#AllSaintsDay", "#Allerheiligen", "#ToussaintDay", "#Europe"], "#8B5CF6"),
    (12,   6, "St. Nicholas Day (Germany/Europe)", ["Germany","Europe"], "cultural",
     ["#Nikolaustag", "#StNicholas", "#Germany", "#SantaClaus"], "#B22222"),
    (12, 24, "Christmas Eve", ["Europe","USA","UK","India","Africa","Germany"], "major",
     ["#ChristmasEve", "#HeiligenAbend", "#XmasEve", "#Christmas2025"], "#C41E3A"),

    # ══ GLOBAL ════════════════════════════════════════════════════════════════
    (1,  27, "Holocaust Remembrance Day", ["global"], "memorial",
     ["#HolocaustRemembranceDay", "#NeverForget", "#HolocaustMemorialDay"], "#1E40AF"),
    (3,  21, "World Poetry Day / Spring Equinox", ["global"], "cultural",
     ["#WorldPoetryDay", "#SpringEquinox", "#FirstDayOfSpring", "#Poetry"], "#8B5CF6"),
    (4,   1, "April Fools Day", ["USA","UK","Europe","India"], "cultural",
     ["#AprilFoolsDay", "#AprilFools", "#Pranks", "#AprilFools2025"], "#FF6B35"),
    (4,   7, "World Health Day", ["global"], "awareness",
     ["#WorldHealthDay", "#HealthForAll", "#WHD2025", "#GlobalHealth"], "#4CAF50"),
    (4,  22, "Earth Day", ["global"], "awareness",
     ["#EarthDay", "#EarthDay2025", "#ClimateAction", "#GoGreen", "#SaveThePlanet"], "#4CAF50"),
    (5,   4, "Star Wars Day", ["global"], "fun",
     ["#StarWarsDay", "#MayThe4thBeWithYou", "#StarWars", "#May4th"], "#FFD700"),
    (5,  31, "World No Tobacco Day", ["global"], "awareness",
     ["#WorldNoTobaccoDay", "#NoTobacco", "#QuitSmoking", "#Health"], "#4CAF50"),
    (6,   5, "World Environment Day", ["global"], "awareness",
     ["#WorldEnvironmentDay", "#ForNature", "#WED2025", "#Environment"], "#4CAF50"),
    (6,  21, "International Yoga Day", ["India","global"], "cultural",
     ["#InternationalYogaDay", "#YogaDay", "#Yoga", "#IDY2025", "#YogaForLife"], "#8B5CF6"),
    (9,   5, "International Day of Charity", ["global"], "awareness",
     ["#InternationalDayOfCharity", "#Charity", "#GiveBack", "#MakeADifference"], "#4CAF50"),
    (10, 10, "World Mental Health Day", ["global"], "awareness",
     ["#WorldMentalHealthDay", "#MentalHealthAwareness", "#WMHD2025", "#MentalHealth"], "#8B5CF6"),
    (11, 19, "World Toilet Day", ["global"], "awareness",
     ["#WorldToiletDay", "#Sanitation", "#CleanWater", "#WASH"], "#1E40AF"),
    (12, 10, "Human Rights Day", ["global"], "awareness",
     ["#HumanRightsDay", "#HumanRights", "#StandUp4HumanRights"], "#1E40AF"),
]


# ── Content Generator ─────────────────────────────────────────────────────────

def get_todays_festivals(check_date: date = None) -> List[Dict]:
    """Return all festivals happening on a given date."""
    check_date = check_date or date.today()
    today_m, today_d = check_date.month, check_date.day
    matching = []

    for fest in FIXED_FESTIVALS:
        month, day, name, regions, fest_type, hashtags, color = fest
        if month == today_m and day == today_d:
            matching.append({
                "name": name,
                "regions": regions,
                "type": fest_type,
                "hashtags": hashtags,
                "color": color,
                "date": check_date.isoformat(),
            })

    return matching


def get_upcoming_festivals(days: int = 30) -> List[Dict]:
    """Return festivals in the next N days."""
    upcoming = []
    today = date.today()

    for i in range(days + 1):
        check = today + timedelta(days=i)
        festivals = get_todays_festivals(check)
        for f in festivals:
            f["days_away"] = i
            upcoming.append(f)

    return upcoming


def generate_festival_content(festival: Dict, platform: str,
                               site_name: str = "", site_url: str = "") -> str:
    """Generate unique, engaging festival content for each platform."""
    name     = festival["name"]
    hashtags = " ".join(festival["hashtags"][:15])
    regions  = ", ".join(festival["regions"][:3])
    site     = site_name or os.environ.get("SITE_NAME", "Our Brand")

    # Multiple content variations per festival (rotated randomly)
    templates = {
        "instagram": [
            f"✨ Wishing everyone celebrating {name} a joyful and blessed day! 🎉\n\nMay this special occasion bring happiness, prosperity, and wonderful memories to you and your loved ones.\n\nWith warm wishes from all of us at {site}. 💙\n\n{hashtags}",
            f"🎊 Happy {name}! 🎊\n\nTo everyone celebrating today — may this day be filled with light, love, and laughter.\n\nWe're grateful for our community across {regions}. Thank you for being part of our journey.\n\n— Team {site}\n\n{hashtags}",
            f"🌟 {name.upper()} 🌟\n\nThis beautiful occasion reminds us of what matters most: connection, gratitude, and celebrating together. 🙏\n\nSending warm wishes to everyone observing today!\n\n📍 From the {site} family\n\n{hashtags}",
        ],
        "facebook": [
            f"🎉 Happy {name}! 🎉\n\nWe want to take a moment to wish all our friends celebrating {name} a wonderful and joyful day.\n\nThis occasion brings communities together and reminds us of the beautiful diversity that makes our world so special.\n\nHere at {site}, we're proud to serve a global community. We hope this day brings you peace, happiness, and wonderful memories with your loved ones.\n\nWarm wishes from our entire team! 💙\n\n{hashtags}",
            f"✨ Celebrating {name} with Our Community ✨\n\nToday we join millions of people across {regions} in celebrating {name}.\n\nWhether you're spending time with family, participating in traditions, or simply reflecting on the meaning of the day — we hope it's truly special.\n\nThank you for being part of the {site} community. 🙏\n\n{hashtags}",
        ],
        "linkedin": [
            f"Today marks {name} — celebrated by communities across {regions}.\n\nAt {site}, we believe in recognizing the cultural and traditional milestones that matter to our community members around the world.\n\nTo everyone observing this occasion: wishing you a meaningful and joyful celebration.\n\nDiversity and cultural awareness make stronger businesses and stronger communities.\n\n{' '.join(festival['hashtags'][:5])}",
        ],
        "twitter": [
            f"🎉 Happy {name}! Wishing everyone celebrating a wonderful day filled with joy and happiness. From all of us at {site}. {' '.join(festival['hashtags'][:2])}",
            f"✨ Warmest {name} wishes to our community! May this day bring you peace and prosperity. — {site} {' '.join(festival['hashtags'][:2])}",
        ],
        "gmb": [
            f"Happy {name} from {site}! 🎉 We wish all our customers and the community a joyful and peaceful celebration. May this special occasion bring happiness to you and your loved ones. Visit us at {site_url or 'our website'} to learn more about how we can serve you.",
        ],
    }

    options = templates.get(platform, templates["facebook"])
    return random.choice(options)


# ── Image Generator ───────────────────────────────────────────────────────────

def generate_festival_banner(festival: Dict, platform: str = "instagram") -> Optional[str]:
    """Generate a festival-themed banner image."""
    try:
        img_gen = os.path.join(BASE_DIR, "scripts", "image_generator.py")
        title = festival["name"]
        keyword = festival["hashtags"][0].lstrip("#") if festival["hashtags"] else ""

        # Override brand color with festival color for banner
        env = os.environ.copy()
        env["BRAND_COLOR_PRIMARY"] = festival.get("color", "#0f3460")

        result = subprocess.run(
            [sys.executable, img_gen,
             "--title", f"Happy {title}!",
             "--keyword", keyword,
             "--type", platform],
            env=env,
            capture_output=True, text=True, cwd=BASE_DIR
        )

        # Find generated image
        import glob
        slug = re.sub(r"[^a-z0-9]+", "-", title.lower())[:30]
        images = glob.glob(os.path.join(BASE_DIR, "output", "images", f"*{platform}*.jpg"))
        images += glob.glob(os.path.join(BASE_DIR, "output", "images", f"*{platform}*.svg"))
        return images[-1] if images else None

    except Exception as e:
        print(f"    Image gen error: {e}")
        return None


# ── Publisher ─────────────────────────────────────────────────────────────────

def post_festival(festival: Dict, preview: bool = False) -> Dict:
    """Post festival content to all enabled social platforms."""
    site_name = os.environ.get("SITE_NAME", "Our Brand")
    site_url  = os.environ.get("WP_URL", "")
    results   = {}

    print(f"\n🎊 Festival: {festival['name']}")
    print(f"   Regions: {', '.join(festival['regions'])}")
    print(f"   Type: {festival['type']}")

    platforms = ["instagram", "facebook", "linkedin", "twitter", "gmb"]

    for platform in platforms:
        content = generate_festival_content(festival, platform, site_name, site_url)

        if preview:
            print(f"\n   [{platform.upper()} PREVIEW]")
            print(f"   {content[:200]}...")
            results[platform] = {"success": True, "preview": True}
            continue

        # Generate festival banner
        print(f"   🎨 Generating {platform} banner...")
        image_path = generate_festival_banner(festival, platform)

        # Publish
        social_script = os.path.join(BASE_DIR, "scripts", "social_publisher.py")
        cmd = [
            sys.executable, social_script,
            "--topic", f"Happy {festival['name']}",
            "--keyword", festival["hashtags"][0].lstrip("#") if festival["hashtags"] else "",
            "--platforms", platform,
            "--url", site_url,
        ]
        if image_path:
            cmd.extend(["--image", image_path])

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=BASE_DIR)
            success = result.returncode == 0
            results[platform] = {"success": success, "output": result.stdout[:200]}
            status = "✅" if success else "❌"
            print(f"   {status} {platform.title()}: {'Posted' if success else 'Failed'}")
        except Exception as e:
            results[platform] = {"success": False, "error": str(e)}
            print(f"   ❌ {platform.title()}: {e}")

    return results


def run_festival_posting(preview: bool = False):
    """Main function: check today's festivals and post all of them."""
    today = date.today()
    festivals = get_todays_festivals(today)

    log = load_log()
    today_str = today.isoformat()

    if not festivals:
        print(f"📅 No festivals today ({today_str})")
        return

    print(f"\n🎉 Claude Auto SEO — Festival Poster")
    print(f"{'='*50}")
    print(f"Date: {today_str} | Time: {datetime.now().strftime('%H:%M')}")
    print(f"Festivals today: {len(festivals)}")
    print(f"Mode: {'PREVIEW' if preview else 'LIVE'}")
    print(f"{'='*50}")

    for festival in festivals:
        # Check if already posted today
        already_posted = any(
            p.get("festival") == festival["name"] and p.get("date") == today_str
            for p in log.get("posts", [])
        )

        if already_posted and not preview:
            print(f"\n⏭️  Already posted: {festival['name']}")
            continue

        results = post_festival(festival, preview)

        if not preview:
            success_count = sum(1 for r in results.values() if r.get("success"))
            log["posts"].append({
                "festival": festival["name"],
                "date": today_str,
                "posted_at": datetime.now().isoformat(),
                "regions": festival["regions"],
                "platforms_success": success_count,
                "platforms_total": len(results),
            })
            save_log(log)

    print(f"\n✅ Festival posting complete!")
    if not preview:
        print(f"Log: {LOG_FILE}")


def load_log() -> Dict:
    os.makedirs(DATA_DIR, exist_ok=True)
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE) as f:
            try:
                return json.load(f)
            except Exception:
                pass
    return {"posts": []}


def save_log(log: Dict):
    with open(LOG_FILE, "w") as f:
        json.dump(log, f, indent=2)


def install_cron():
    """Install cron job to run at 1:00 AM daily."""
    script = os.path.abspath(__file__)
    cron_line = f"0 1 * * * cd {BASE_DIR} && {sys.executable} {script} --post-now >> {DATA_DIR}/festival-cron.log 2>&1"

    result = subprocess.run(["crontab", "-l"], capture_output=True, text=True)
    existing = result.stdout if result.returncode == 0 else ""

    if "festival_poster" in existing:
        print("⚠️  Festival cron already installed. Check with: crontab -l")
        return

    new_crontab = existing.rstrip() + "\n" + cron_line + "\n"
    proc = subprocess.run(["crontab", "-"], input=new_crontab, capture_output=True, text=True)

    if proc.returncode == 0:
        print("✅ Festival poster installed! Runs at 1:00 AM every day.")
        print("   On festival days, posts to all enabled social platforms.")
        print("   View cron: crontab -l")
    else:
        print(f"❌ Install failed. Add manually:\n  {cron_line}")


def show_upcoming(days: int = 14):
    """Show upcoming festivals."""
    upcoming = get_upcoming_festivals(days)
    today = date.today()

    print(f"\n📅 Upcoming Festivals — Next {days} Days")
    print(f"{'='*60}")

    if not upcoming:
        print("No festivals in this period.")
        return

    for f in upcoming:
        fest_date = date.today() + timedelta(days=f["days_away"])
        day_label = "TODAY" if f["days_away"] == 0 else \
                    "TOMORROW" if f["days_away"] == 1 else \
                    f"In {f['days_away']} days ({fest_date.strftime('%b %d')})"
        print(f"\n  🎊 {f['name']}")
        print(f"     {day_label} | Regions: {', '.join(f['regions'][:3])}")
        print(f"     Tags: {' '.join(f['hashtags'][:4])}")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Claude Auto SEO — Festival Auto-Poster")
    parser.add_argument("--post-now",      action="store_true", help="Post today's festivals")
    parser.add_argument("--check-today",   action="store_true", help="Show today's festivals")
    parser.add_argument("--check-upcoming",type=int, metavar="DAYS", default=0, help="Show next N days")
    parser.add_argument("--install-cron",  action="store_true", help="Install 1AM daily cron")
    parser.add_argument("--preview",       action="store_true", help="Preview without posting")
    args = parser.parse_args()

    if args.post_now or args.preview:
        run_festival_posting(preview=args.preview)
    elif args.check_today:
        festivals = get_todays_festivals()
        if festivals:
            print(f"Today's festivals ({len(festivals)}):")
            for f in festivals:
                print(f"  🎊 {f['name']} — {', '.join(f['regions'])}")
        else:
            print("No festivals today.")
    elif args.check_upcoming:
        show_upcoming(args.check_upcoming)
    elif args.install_cron:
        install_cron()
    else:
        show_upcoming(14)
