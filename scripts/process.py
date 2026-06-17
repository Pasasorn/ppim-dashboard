import pandas as pd
import json
import os
import sys
from datetime import datetime
from pathlib import Path

MAPPING = {
    "กฟจ.พะเยา":"กฟจ.พะเยา","กฟย.แม่กา":"กฟจ.พะเยา","กฟอ.จุน":"กฟจ.พะเยา",
    "กฟอ.เชียงคำ":"กฟจ.พะเยา","กฟอ.เชียงม่วน":"กฟจ.พะเยา","กฟอ.ดอกคำใต้":"กฟจ.พะเยา",
    "กฟอ.ปง":"กฟจ.พะเยา","กฟอ.ภูกามยาว":"กฟจ.พะเยา","กฟอ.ภูซาง":"กฟจ.พะเยา","กฟอ.แม่ใจ":"กฟจ.พะเยา",
    "กฟจ.แม่ฮ่องสอน":"กฟจ.แม่ฮ่องสอน","กฟอ.กัลยาณิวัฒนา":"กฟจ.แม่ฮ่องสอน",
    "กฟอ.ขุนยวม":"กฟจ.แม่ฮ่องสอน","กฟอ.ปางมะผ้า":"กฟจ.แม่ฮ่องสอน",
    "กฟอ.ปาย":"กฟจ.แม่ฮ่องสอน","กฟอ.แม่ลาน้อย":"กฟจ.แม่ฮ่องสอน",
    "กฟอ.แม่สะเรียง":"กฟจ.แม่ฮ่องสอน","กฟอ.สบเมย":"กฟจ.แม่ฮ่องสอน",
    "กฟน.1":"กฟน.1",
    "กฟอ.เกาะคา":"กฟส.เกาะคา","กฟอ.เถิน":"กฟส.เกาะคา","กฟอ.แม่ทะ":"กฟส.เกาะคา",
    "กฟอ.แม่พริก":"กฟส.เกาะคา","กฟอ.สบปราบ":"กฟส.เกาะคา",
    "กฟอ.เสริมงาม":"กฟส.เกาะคา","กฟอ.ห้างฉัตร":"กฟส.เกาะคา",
    "กฟอ.จอมทอง":"กฟส.จอมทอง","กฟอ.ดอยเต่า":"กฟส.จอมทอง","กฟอ.ดอยหล่อ":"กฟส.จอมทอง",
    "กฟอ.แม่แจ่ม":"กฟส.จอมทอง","กฟอ.อมก๋อย":"กฟส.จอมทอง",
    "กฟอ.ฮอด":"กฟส.จอมทอง","กฟต.บ่อหลวง":"กฟส.จอมทอง",
    "กฟจ.เชียงราย":"กฟจ.เชียงราย","กฟต.ห้วยสัก":"กฟจ.เชียงราย",
    "กฟส.นางแล":"กฟจ.เชียงราย","กฟอ.เวียงชัย":"กฟจ.เชียงราย","กฟอ.เวียงเชียงรุ้ง":"กฟจ.เชียงราย",
    "กฟอ.ขุนตาล":"กฟส.เทิง","กฟอ.เชียงของ":"กฟส.เทิง","กฟอ.เทิง":"กฟส.เทิง",
    "กฟอ.พญาเม็งราย":"กฟส.เทิง","กฟอ.เวียงแก่น":"กฟส.เทิง",
    "กฟอ.ไชยปราการ":"กฟส.ฝาง","กฟอ.ฝาง":"กฟส.ฝาง",
    "กฟอ.ป่าแดด":"กฟส.พาน","กฟอ.พาน":"กฟส.พาน","กฟอ.แม่ลาว":"กฟส.พาน",
    "กฟอ.แม่สรวย":"กฟส.พาน","กฟอ.เวียงป่าเป้า":"กฟส.พาน",
    "กฟจ.เชียงใหม่":"กฟจ.เชียงใหม่","กฟอ.งาว":"กฟจ.เชียงใหม่","กฟอ.สารภี":"กฟจ.เชียงใหม่",
    "กฟจ.เชียงใหม่ 2":"กฟจ.เชียงใหม่ 2","กฟอ.ดอยสะเก็ด":"กฟจ.เชียงใหม่ 2",
    "กฟต.ป่าแป๋":"กฟส.แม่ริม","กฟอ.เชียงดาว":"กฟส.แม่ริม","กฟอ.แม่แตง":"กฟส.แม่ริม",
    "กฟอ.แม่ริม":"กฟส.แม่ริม","กฟอ.เวียงแหง":"กฟส.แม่ริม","กฟอ.สะเมิง":"กฟส.แม่ริม",
    "กฟต.แม่สลองนอก":"กฟส.แม่สาย","กฟบ.เทอดไทย":"กฟส.แม่สาย",
    "กฟฟ.ดอยตุง":"กฟส.แม่สาย","กฟส.ดอยหลวง":"กฟส.แม่สาย",
    "กฟส.แม่ฟ้าหลวง":"กฟส.แม่สาย","กฟอ.เชียงแสน":"กฟส.แม่สาย",
    "กฟอ.แม่จัน":"กฟส.แม่สาย","กฟอ.แม่สาย":"กฟส.แม่สาย","กฟอ.แม่อาย":"กฟส.แม่สาย",
    "กฟจ.ลำปาง":"กฟจ.ลำปาง","กฟต.พบชส.":"กฟจ.ลำปาง","กฟอ.งาว":"กฟจ.ลำปาง",
    "กฟอ.แจ้ห่ม":"กฟจ.ลำปาง","กฟอ.เมืองปาน":"กฟจ.ลำปาง",
    "กฟอ.แม่เมาะ":"กฟจ.ลำปาง","กฟอ.วังเหนือ":"กฟจ.ลำปาง",
    "กฟจ.ลำพูน":"กฟจ.ลำพูน","กฟต.นครเจดีย์":"กฟจ.ลำพูน","กฟส.ป่าซาง":"กฟจ.ลำพูน",
    "กฟอ.ทุ่งหัวช้าง":"กฟจ.ลำพูน","กฟอ.บ้านธิ":"กฟจ.ลำพูน","กฟอ.บ้านโฮ่ง":"กฟจ.ลำพูน",
    "กฟอ.แม่ทา":"กฟจ.ลำพูน","กฟอ.ลี้":"กฟจ.ลำพูน",
    "กฟอ.เวียงหนองล่อง":"กฟจ.ลำพูน","กฟอ.แม่ตืน":"กฟจ.ลำพูน",
    "กฟส.แม่ออน":"กฟส.สันกำแพง","กฟอ.สันกำแพง":"กฟส.สันกำแพง",
    "กฟอ.พร้าว":"กฟส.สันทราย","กฟอ.สันทราย":"กฟส.สันทราย",
    "กฟอ.แม่วาง":"กฟส.สันป่าตอง","กฟอ.สันป่าตอง":"กฟส.สันป่าตอง",
    "กฟอ.หางดง":"กฟส.หางดง"
}

JOINTS = ["กฟจ.พะเยา","กฟจ.ลำปาง","กฟจ.ลำพูน","กฟจ.เชียงราย","กฟจ.เชียงใหม่",
          "กฟจ.เชียงใหม่ 2","กฟจ.แม่ฮ่องสอน","กฟส.เกาะคา","กฟส.จอมทอง","กฟส.ฝาง",
          "กฟส.พาน","กฟส.สันกำแพง","กฟส.สันทราย","กฟส.สันป่าตอง","กฟส.หางดง",
          "กฟส.เทิง","กฟส.แม่ริม","กฟส.แม่สาย","กฟน.1"]

STATUSES = ["เชื่อมต่อเรียบร้อยแล้ว","ยกเลิก","รอชำระเงิน",
            "รอดำเนินการหลังอนุมัติเชื่อมต่อ / รับพิจารณา","รอตรวจสอบคำขอ",
            "รอตรวจสอบระบบผลิต","รอทดสอบเชื่อมต่อ","รอผู้ยื่นคำขอส่งเอกสารแก้ไข",
            "รออนุมัติเชื่อมต่อ (200 kW ขึ้นไป)","รออนุมัติเชื่อมต่อ/รับพิจารณา",
            "รออนุมัติแจ้งวันเริ่มเชื่อมต่อ","รอแก้ไขเอกสารหลังอนุมัติเชื่อมต่อ / รับพิจารณา"]

ST_SHORT = ["✅เชื่อมต่อ","❌ยกเลิก","💰ชำระ","📋ดำเนินการ","🔍ตรวจสอบ","⚙️ระบบผลิต",
            "🔌ทดสอบ","📄เอกสาร","⚡200kW","📝อนุมัติ","📅วันเริ่ม","✏️แก้ไข"]

ST_COLOR = ["#2ECC71","#E74C3C","#F39C12","#5DADE2","#C77DFF","#1ABC9C",
            "#AEB6BF","#E67E22","#E74C3C","#D4AF37","#5DADE2","#A569BD"]

def find_latest_csv(data_folder="data"):
    files = sorted(Path(data_folder).glob("ppim_report_*.csv"),
                   key=lambda x: x.stat().st_mtime, reverse=True)
    return files[0] if files else None

def process(csv_path):
    print(f"📂 Processing: {csv_path.name}")
    df = pd.read_csv(csv_path, sep="|", encoding="utf-8")
    today = datetime.now().strftime("%Y-%m-%d")
    today_ts = pd.Timestamp(today)
    file_date = datetime.fromtimestamp(csv_path.stat().st_mtime).strftime("%d %B %Y")

    for col in ["วันที่ยื่นคำขอ","วันที่ยื่นแก้ไขคำขอ","วันที่ชำระเงิน",
                "วันที่อนุมัติเชื่อมต่อ","วันที่เชื่อมต่อเข้าระบบ"]:
        df[col] = df[col].replace("-", None)
        df[col] = pd.to_datetime(df[col], errors="coerce")

    df["joint"] = df["กฟฟ.ที่ตรวจสอบ"].str.strip().map(MAPPING).fillna(df["กฟฟ.ที่ตรวจสอบ"].str.strip())
    df["year"]  = df["วันที่ยื่นคำขอ"].dt.year.astype("Int64")
    df["month"] = df["วันที่ยื่นคำขอ"].dt.to_period("M").astype(str)

    def biz(s):
        if pd.isna(s): return 0
        return max(0, len(pd.bdate_range(pd.Timestamp(s).normalize(), today_ts.normalize())) - 1)

    df["dt_sla"]  = df["วันที่ยื่นแก้ไขคำขอ"].fillna(df["วันที่ยื่นคำขอ"])
    df["elapsed"] = df["dt_sla"].apply(biz)
    df["sla_ov"]  = (df["สถานะคำขอ"] == "รอตรวจสอบคำขอ") & (df["elapsed"] > 15)
    df["sla_ok"]  = (df["สถานะคำขอ"] == "รอตรวจสอบคำขอ") & (df["elapsed"] <= 15)

    rows = []
    for (jt, yr, mo, st), grp in df.groupby(["joint","year","month","สถานะคำขอ"], dropna=False):
        r = {"j":str(jt),"y":int(yr) if pd.notna(yr) else 0,"m":str(mo),"s":str(st),"n":len(grp)}
        ok = int(grp["sla_ok"].sum()); ov = int(grp["sla_ov"].sum())
        if ok: r["ok"] = ok
        if ov: r["ov"] = ov
        rows.append(r)

    details = []
    for _, row in df.iterrows():
        d = {"id":str(row["เลขคำขอ"]),"st":str(row["สถานะคำขอ"]),"j":str(row["joint"]),
             "y":int(row["year"]) if pd.notna(row["year"]) else 0,
             "m":str(row["month"]),"sub":str(row["วันที่ยื่นคำขอ"])[:10] if pd.notna(row["วันที่ยื่นคำขอ"]) else "-"}
        if pd.notna(row["วันที่อนุมัติเชื่อมต่อ"]): d["app"] = str(row["วันที่อนุมัติเชื่อมต่อ"])[:10]
        if pd.notna(row["วันที่เชื่อมต่อเข้าระบบ"]): d["con"] = str(row["วันที่เชื่อมต่อเข้าระบบ"])[:10]
        if pd.notna(row["วันที่ชำระเงิน"]): d["pay"] = str(row["วันที่ชำระเงิน"])[:10]
        kw = row.get("กำลังการผลิตที่ขอ (kW)")
        if pd.notna(kw) and kw: d["kw"] = float(kw)
        tp = row.get("ประเภทพลังงาน")
        if pd.notna(tp) and str(tp) != "nan": d["tp"] = str(tp)
        details.append(d)

    sla_ov_list = df[df["sla_ov"]][["เลขคำขอ","joint","month","elapsed"]].to_dict(orient="records")
    sla_ok_count = int(df["sla_ok"].sum())
    total = len(df)

    print(f"✅ rows={len(rows)}, records={total}, SLA เกิน={len(sla_ov_list)}")
    return rows, details, sla_ov_list, sla_ok_count, file_date, csv_path.name, today, total

def build_html(rows, details, sla_ov_list, sla_ok_count, file_date, csv_name, today, total):
    print("🔨 Building HTML...")
    rows_js    = json.dumps(rows,    ensure_ascii=False, separators=(",",":"))
    details_js = json.dumps(details, ensure_ascii=False, separators=(",",":"))

    if sla_ov_list:
        sla_rows = "".join(f"""<tr>
          <td style='color:var(--gold2);font-weight:600'>{r['joint']}</td>
          <td>{r['month']}</td><td><span class='id-chip'>{r['เลขคำขอ']}</span></td>
          <td style='color:var(--red);font-weight:700'>{r['elapsed']} วันทำการ</td>
          <td style='color:var(--red);font-weight:700'>🔴 เกิน {r['elapsed']-15} วัน</td>
        </tr>""" for r in sla_ov_list)
        sla_badge = f'<span class="sla-badge">เกิน SLA {len(sla_ov_list)} ราย!</span>'
    else:
        sla_rows = "<tr><td colspan='5' style='text-align:center;color:var(--green);padding:10px'>✅ ไม่มีรายการเกิน SLA</td></tr>"
        sla_badge = '<span class="sla-badge-ok">✅ ทุกรายการอยู่ใน SLA</span>'

    st_short_js = json.dumps(ST_SHORT, ensure_ascii=False)
    st_color_js = json.dumps(ST_COLOR, ensure_ascii=False)
    statuses_js = json.dumps(STATUSES, ensure_ascii=False)
    joints_js   = json.dumps(JOINTS,   ensure_ascii=False)

    html = open("scripts/template.html", encoding="utf-8").read()
    html = (html
        .replace("%%ROWS%%",        rows_js)
        .replace("%%DETAILS%%",     details_js)
        .replace("%%TOTAL%%",       str(total))
        .replace("%%FILE_DATE%%",   file_date)
        .replace("%%CSV_NAME%%",    csv_name)
        .replace("%%TODAY%%",       today)
        .replace("%%SLA_ROWS%%",    sla_rows)
        .replace("%%SLA_BADGE%%",   sla_badge)
        .replace("%%SLA_OK%%",      str(sla_ok_count))
        .replace("%%JOINTS%%",      joints_js)
        .replace("%%STATUSES%%",    statuses_js)
        .replace("%%ST_SHORT%%",    st_short_js)
        .replace("%%ST_COLOR%%",    st_color_js)
    )
    return html

def main():
    csv_path = find_latest_csv("data")
    if not csv_path:
        print("❌ ไม่พบไฟล์ ppim_report_*.csv ใน data/")
        sys.exit(1)

    rows, details, sla_ov, sla_ok, file_date, csv_name, today, total = process(csv_path)
    html = build_html(rows, details, sla_ov, sla_ok, file_date, csv_name, today, total)

    with open("PPIM_Dashboard_v2.html", "w", encoding="utf-8") as f:
        f.write(html)
    print(f"✅ สร้าง PPIM_Dashboard_v2.html สำเร็จ ({len(html)//1024} KB)")

if __name__ == "__main__":
    main()
