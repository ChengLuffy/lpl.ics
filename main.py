import time
import requests
import json
import os

SOURCE_URL = os.getenv("URL")
YEAR_STR = os.getenv("YEAR")

def request_data():
    response = requests.get(url=SOURCE_URL, headers={"User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 15_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 lolapp/9.1.5.1900", "Accept-Language": "zh-CN,zh-Hans;q=0.9", "Accept": "application/json, text/plain, */*"})
    content_str = response.content.decode("utf-8")
    json_obj = json.loads(content_str)
    result_obj = json_obj["msg"]
    return result_obj

def generate_ics_content(year_str: str, matchs) -> str:
    if len(matchs) == 0:
        assert("no data")
    ret = "BEGIN:VCALENDAR\nVERSION:2.0\nPRODID: LPL"+ year_str + "\nX-WR-CALNAME:LPL" + year_str + "赛程"
    game_names = [year_str + "职业联赛", year_str + "全球总决赛", year_str + "季中冠军赛"]
    for match in matchs:
        if match["GameName"] in game_names:
            ret += "\nBEGIN:VEVENT"
            teams = match["bMatchName"].split('vs')
            if len(teams) == 2:
                team_a = teams[0].strip()
                team_b = teams[1].strip()
                ret += "\nSUMMARY:%s vs %s" % (team_a, team_b)
            else:
                ret += "\nSUMMARY:%s" % match["bMatchName"].strip()
            if match["ScoreA"] != "0" or match["ScoreB"] != "0":
                ret += "    %s : %s" % (match["ScoreA"], match["ScoreB"])
                pass
            ret += "\nUID:lpl%s_%s" % (year_str, match["bMatchId"])
            dateStr = match["MatchDate"]
            dateStu = time.strptime(dateStr, "%Y-%m-%d %H:%M:%S")
            timestamp = time.mktime(dateStu) - 8 * 3600
            timestamp_end = time.mktime(dateStu) - 8 * 3600
            if match["GameModeName"] == "BO1":
                timestamp_end = time.mktime(dateStu) - 7 * 3600
                pass
            elif match["GameModeName"] == "BO3":
                timestamp_end = time.mktime(dateStu) - 6 * 3600
                pass
            elif match["GameModeName"] == "BO5":
                timestamp_end = time.mktime(dateStu) - 5 * 3600
                pass
            dateStrNew = time.strftime("%Y%m%dT%H%M%SZ", time.localtime(timestamp))
            dateStrNew_end = time.strftime("%Y%m%dT%H%M%SZ", time.localtime(timestamp_end))
            ret += "\nDTSTART:%s" % dateStrNew
            ret += "\nDTEND:%s" % dateStrNew_end
            ret += "\nBEGIN:VALARM\nTRIGGER:-PT5M"
            ret += "\nUID:lpl%s_%s" % (year_str, match["bMatchId"])
            ret += "\nATTACH;VALUE=URI:Chord\nACTION:AUDIO\nEND:VALARM"
            ret += "\nEND:VEVENT"
            pass
        pass
    ret += "\nEND:VCALENDAR"
    return ret

def write_to_file(year_str: str, content: str):
    FILE_PATH = "./LPL" + year_str + ".ics"
    with open(FILE_PATH, 'wt', encoding="utf8") as f:
        f.write(content)
        f.close()

if __name__ == '__main__':
    matchs = request_data()
    content = generate_ics_content(year_str=YEAR_STR, matchs=matchs)
    write_to_file(year_str=YEAR_STR, content=content)
