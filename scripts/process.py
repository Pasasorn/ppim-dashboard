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

JOINTS_ORDER = ["กฟจ.พะเยา","กฟจ.ลำปาง","กฟจ.ลำพูน","กฟจ.เชียงราย","กฟจ.เชียงใหม่",
                "กฟจ.เชียงใหม่ 2","กฟจ.แม่ฮ่องสอน","กฟส.เกาะคา","กฟส.จอมทอง","กฟส.ฝาง",
                "กฟส.พาน","กฟส.สันกำแพง","กฟส.สันทราย","กฟส.สันป่าตอง","กฟส.หางดง",
                "กฟส.เทิง","กฟส.แม่ริม","กฟส.แม่สาย","กฟน.1"]

TIER_LABEL = {
    'red1': ('🟡 8-15วัน', 'KPI=4 — ควรเร่งดำเนินการ'),
    'red2': ('🟠 เกิน16-21วัน', 'KPI=3 — ควรเร่งดำเนินการ'),
    'red3': ('🟠 เกิน22-28วัน', 'KPI=2 — ควรเร่งดำเนินการ'),
    'red4': ('🔴 เกิน28วัน+', 'KPI=1 — ควรเร่งดำเนินการ'),
}

def find_latest_csv(data_folder="data"):
    files = sorted(Path(data_folder).glob("ppim_report_*.csv"),
                    key=lambda x: x.stat().st_mtime, reverse=True)
    return files[0] if files else None

def sla_tier(days):
    if days <= 7: return 'green', 5
    elif days <= 15: return 'red1', 4
    elif days <= 21: return 'red2', 3
    elif days <= 28: return 'red3', 2
    else: return 'red4', 1

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

    df["dt_sla"]   = df["วันที่ยื่นแก้ไขคำขอ"].fillna(df["วันที่ยื่นคำขอ"])
    df["elapsed"]  = df["dt_sla"].apply(biz)
    df["has_edit"] = df["วันที่ยื่นแก้ไขคำขอ"].notna()

    is_check = df["สถานะคำขอ"] == "รอตรวจสอบคำขอ"
    tier_kpi = df.apply(lambda r: sla_tier(r["elapsed"]) if is_check[r.name] else (None, None), axis=1)
    df["sla_tier"] = tier_kpi.apply(lambda x: x[0])
    df["kpi"]      = tier_kpi.apply(lambda x: x[1])
    df["sla_ov7"]  = is_check & (df["elapsed"] > 7)
    df["sla_ok7"]  = is_check & (df["elapsed"] <= 7)

    # Aggregated rows
    rows = []
    for (jt, yr, mo, st), grp in df.groupby(["joint","year","month","สถานะคำขอ"], dropna=False):
        r = {"j":str(jt),"y":int(yr) if pd.notna(yr) else 0,"m":str(mo),"s":str(st),"n":len(grp)}
        ok = int(grp["sla_ok7"].sum()); ov = int(grp["sla_ov7"].sum())
        if ok: r["ok"] = ok
        if ov: r["ov"] = ov
        rows.append(r)

    # Detail records
    details = []
    for _, row in df.iterrows():
        d = {"id":str(row["เลขคำขอ"]),"st":str(row["สถานะคำขอ"]),"j":str(row["joint"]),
             "y":int(row["year"]) if pd.notna(row["year"]) else 0,
             "m":str(row["month"]),"sub":str(row["วันที่ยื่นคำขอ"])[:10] if pd.notna(row["วันที่ยื่นคำขอ"]) else "-"}
        if pd.notna(row["วันที่ยื่นแก้ไขคำขอ"]): d["edt"] = str(row["วันที่ยื่นแก้ไขคำขอ"])[:10]
        if pd.notna(row["วันที่อนุมัติเชื่อมต่อ"]): d["app"] = str(row["วันที่อนุมัติเชื่อมต่อ"])[:10]
        if pd.notna(row["วันที่เชื่อมต่อเข้าระบบ"]): d["con"] = str(row["วันที่เชื่อมต่อเข้าระบบ"])[:10]
        kw = row.get("กำลังการผลิตที่ขอ (kW)")
        if pd.notna(kw) and kw: d["kw"] = float(kw)
        tp = row.get("ประเภทพลังงาน")
        if pd.notna(tp) and str(tp) != "nan": d["tp"] = str(tp)
        if row["สถานะคำขอ"] == "รอตรวจสอบคำขอ":
            d["sla_start"]     = str(row["dt_sla"])[:10] if pd.notna(row["dt_sla"]) else "-"
            d["sla_days"]      = int(row["elapsed"])
            d["sla_tier"]      = row["sla_tier"]
            d["sla_from_edit"] = bool(row["has_edit"])
            d["kpi"]           = int(row["kpi"])
        details.append(d)

    # KPI summary per joint
    check_df = df[is_check].copy()
    kpi_summary = []
    for j in JOINTS_ORDER:
        sub = check_df[check_df["joint"] == j]
        n = len(sub)
        if n == 0:
            kpi_summary.append({"j": j, "avg_kpi": 5.0, "n": 0, "ov_count": 0, "max_days": 0})
            continue
        avg_kpi = round(sub["kpi"].mean(), 2)
        ov_count = int((sub["elapsed"] > 7).sum())
        max_days = int(sub["elapsed"].max())
        kpi_summary.append({"j": j, "avg_kpi": avg_kpi, "n": n, "ov_count": ov_count, "max_days": max_days})

    # SLA overdue list (>7 days) for the alert box
    sla_ov_list = df[df["sla_ov7"]][["เลขคำขอ","joint","month","elapsed","has_edit","dt_sla","sla_tier","kpi"]].copy()
    sla_ov_list["dt_sla"] = sla_ov_list["dt_sla"].astype(str).str[:10]
    sla_ov_list = sla_ov_list.to_dict(orient="records")
    sla_ok_count = int(df["sla_ok7"].sum())
    total = len(df)

    # งานยื่นขอขนาน ทุกสถานะ — แกนเดือน/ปีต่างกันตามกลุ่ม:
    #   - เชื่อมต่อเรียบร้อยแล้ว (C_done): ใช้ "วันที่อนุมัติเชื่อมต่อ" (จบงานจริง)
    #   - ทุกสถานะอื่น (A, B, C_cancel): ใช้ "วันที่ยื่นคำขอ" (ยังไม่จบ หรือไม่มีวันจบงานเก็บไว้)
    GROUP_MAP = {
        "รอตรวจสอบคำขอ":"A","รอผู้ยื่นคำขอส่งเอกสารแก้ไข":"A","รอตรวจสอบระบบผลิต":"A",
        "รออนุมัติเชื่อมต่อ/รับพิจารณา":"A","รออนุมัติเชื่อมต่อ (200 kW ขึ้นไป)":"A","รอชำระเงิน":"A",
        "รอดำเนินการหลังอนุมัติเชื่อมต่อ / รับพิจารณา":"B","รอแก้ไขเอกสารหลังอนุมัติเชื่อมต่อ / รับพิจารณา":"B",
        "รอทดสอบเชื่อมต่อ":"B","รออนุมัติแจ้งวันเริ่มเชื่อมต่อ":"B",
        "เชื่อมต่อเรียบร้อยแล้ว":"C_done","ยกเลิก":"C_cancel"
    }
    df["pgrp"] = df["สถานะคำขอ"].map(GROUP_MAP)

    df["month_approve"] = df["วันที่อนุมัติเชื่อมต่อ"].dt.to_period("M").astype(str)
    df["year_approve"]  = df["วันที่อนุมัติเชื่อมต่อ"].dt.year.astype("Int64")

    is_done = df["pgrp"] == "C_done"
    df["axis_m"] = df["month_approve"].where(is_done, df["month"])
    df["axis_y"] = df["year_approve"].where(is_done, df["year"])

    rows_started = []
    for (j, ay, am, st, grp, sy), g in df.groupby(["joint","axis_y","axis_m","สถานะคำขอ","pgrp","year"], dropna=False):
        rows_started.append({
            "j": str(j), "ys": int(ay) if pd.notna(ay) else 0, "m": str(am),
            "st": str(st), "grp": str(grp), "n": len(g),
            "yss": int(sy) if pd.notna(sy) else 0
        })

    print(f"✅ rows={len(rows)}, records={total}, SLA เกิน 7 วัน={len(sla_ov_list)}, SLA ใน={sla_ok_count}")
    print(f"✅ งานยื่นขอ (ทุกสถานะ): {sum(r['n'] for r in rows_started)} ราย")

    # Conversion Rate แยกตามจุดร่วมงาน × ปี
    CONV_YEARS = [2024, 2025, 2026]
    conv_data = []
    for j in JOINTS_ORDER:
        row = {"j": j}
        for yr in CONV_YEARS:
            sub = df[(df["joint"] == j) & (df["year"] == yr)]
            tot = len(sub)
            done = int((sub["สถานะคำขอ"] == "เชื่อมต่อเรียบร้อยแล้ว").sum())
            cancel = int((sub["สถานะคำขอ"] == "ยกเลิก").sum())
            row[f"total_{yr}"] = tot
            row[f"done_{yr}"] = done
            row[f"cancel_{yr}"] = cancel
            row[f"pct_{yr}"] = round(done / tot * 100, 1) if tot else 0
            row[f"cpct_{yr}"] = round(cancel / tot * 100, 1) if tot else 0
        conv_data.append(row)

    # Trend: รายเดือน ยื่น/เชื่อมต่อ/ยกเลิก/คงค้าง
    trend_data = []
    for m, g in df.groupby("month"):
        trend_data.append({"m": str(m), "total": len(g),
            "done":    int((g["สถานะคำขอ"] == "เชื่อมต่อเรียบร้อยแล้ว").sum()),
            "cancel":  int((g["สถานะคำขอ"] == "ยกเลิก").sum()),
            "pending": int((~g["สถานะคำขอ"].isin(["เชื่อมต่อเรียบร้อยแล้ว","ยกเลิก"])).sum())})

    # Lead Time: ยื่น → เชื่อมต่อเข้าระบบ แยกจุดร่วมงาน
    done_df = df[df["สถานะคำขอ"] == "เชื่อมต่อเรียบร้อยแล้ว"].copy()
    done_df["lead"] = (done_df["วันที่เชื่อมต่อเข้าระบบ"] - done_df["วันที่ยื่นคำขอ"]).dt.days
    done_df = done_df[done_df["lead"].between(0, 730)]
    lead_agg = done_df.groupby("joint")["lead"].agg(["mean","median","count"]).round(1).reset_index()
    lead_agg.columns = ["j","avg","med","n"]
    lead_data = lead_agg.to_dict(orient="records")

    # MW Analysis
    df["kw_num"] = pd.to_numeric(df["กำลังการผลิตที่ขอ (kW)"], errors="coerce")
    mw_status = df.groupby("สถานะคำขอ")["kw_num"].sum().round(1).reset_index()
    mw_status.columns = ["st","kw_total"]
    mw_voltage = df.groupby("ระดับแรงดันมิเตอร์")["kw_num"].agg(kw_total="sum", n="count").round(1).reset_index()
    mw_voltage.columns = ["v","kw_total","n"]
    mw_monthly = df[df["สถานะคำขอ"]=="เชื่อมต่อเรียบร้อยแล้ว"].groupby("month")["kw_num"].sum().round(1).reset_index()
    mw_monthly.columns = ["m","kw"]
    mw_done_total    = round(float(df[df["สถานะคำขอ"]=="เชื่อมต่อเรียบร้อยแล้ว"]["kw_num"].sum() / 1000), 2)
    mw_pending_total = round(float(df[~df["สถานะคำขอ"].isin(["เชื่อมต่อเรียบร้อยแล้ว","ยกเลิก"])]["kw_num"].sum() / 1000), 2)

    # Map: lat/lon งานที่ยังค้าง (กรองเฉพาะภาคเหนือ)
    df["lat_n"] = pd.to_numeric(df["ละติจูด"], errors="coerce")
    df["lon_n"] = pd.to_numeric(df["ลองจิจูด"], errors="coerce")
    pending_map = df[~df["สถานะคำขอ"].isin(["เชื่อมต่อเรียบร้อยแล้ว","ยกเลิก"])].copy()
    pending_map = pending_map[(pending_map["lat_n"].between(17,21)) & (pending_map["lon_n"].between(97,106))]
    map_data = []
    for _, r in pending_map.iterrows():
        d = {"id":str(r["เลขคำขอ"]),"st":str(r["สถานะคำขอ"]),"j":str(r["joint"]),
             "lat":round(float(r["lat_n"]),5),"lon":round(float(r["lon_n"]),5)}
        if pd.notna(r["kw_num"]): d["kw"] = round(float(r["kw_num"]),1)
        map_data.append(d)

    print(f"✅ Trend {len(trend_data)} months | Lead {len(lead_data)} joints | MW done={mw_done_total}MW | Map {len(map_data)} points")

    return {
        "rows": rows, "details": details, "kpi_summary": kpi_summary,
        "sla_ov_list": sla_ov_list, "sla_ok_count": sla_ok_count,
        "rows_started": rows_started, "conv_data": conv_data,
        "trend_data": trend_data, "lead_data": lead_data,
        "mw_status": mw_status.to_dict(orient="records"),
        "mw_voltage": mw_voltage.to_dict(orient="records"),
        "mw_monthly": mw_monthly.to_dict(orient="records"),
        "mw_done_total": mw_done_total, "mw_pending_total": mw_pending_total,
        "map_data": map_data,
        "file_date": file_date, "csv_name": csv_path.name, "today": today, "total": total
    }

def build_sla_rows(sla_ov_list):
    if not sla_ov_list:
        return "<tr><td colspan='8' style='text-align:center;color:var(--green);padding:10px'>✅ ไม่มีรายการเกิน SLA</td></tr>"
    rows_html = ""
    for r in sla_ov_list:
        from_edit = "✏️ วันแก้ไขคำขอ" if r["has_edit"] else "📋 วันยื่นคำขอ"
        label, kpi_txt = TIER_LABEL.get(r["sla_tier"], ("🔴 เกิน SLA", ""))
        rows_html += f"""<tr>
          <td style='color:var(--gold2);font-weight:600'>{r['joint']}</td>
          <td>{r['month']}</td>
          <td><span class='id-chip'>{r['เลขคำขอ']}</span></td>
          <td>{r['dt_sla']}</td>
          <td style='font-size:10px;color:var(--text2)'>{from_edit}</td>
          <td style='color:var(--red);font-weight:700'>{r['elapsed']} วัน</td>
          <td style='font-weight:700'>{label}</td>
          <td><span class="kpi-badge">{kpi_txt}</span></td>
        </tr>"""
    return rows_html

def build_html(data):
    print("🔨 Building HTML from template_v6.html...")
    rows_js        = json.dumps(data["rows"],        ensure_ascii=False, separators=(",",":"))
    details_js     = json.dumps(data["details"],     ensure_ascii=False, separators=(",",":"))
    kpi_summary_js = json.dumps(data["kpi_summary"],  ensure_ascii=False, separators=(",",":"))
    rows_started_js = json.dumps(data["rows_started"], ensure_ascii=False, separators=(",",":"))
    conv_data_js    = json.dumps(data["conv_data"],    ensure_ascii=False, separators=(",",":"))
    trend_data_js   = json.dumps(data["trend_data"],   ensure_ascii=False, separators=(",",":"))
    lead_data_js    = json.dumps(data["lead_data"],    ensure_ascii=False, separators=(",",":"))
    mw_status_js    = json.dumps(data["mw_status"],    ensure_ascii=False, separators=(",",":"))
    mw_voltage_js   = json.dumps(data["mw_voltage"],   ensure_ascii=False, separators=(",",":"))
    mw_monthly_js   = json.dumps(data["mw_monthly"],   ensure_ascii=False, separators=(",",":"))
    map_data_js     = json.dumps(data["map_data"],     ensure_ascii=False, separators=(",",":"))

    sla_rows  = build_sla_rows(data["sla_ov_list"])
    sla_badge = (f'<span class="sla-badge">เกิน SLA (7วัน) {len(data["sla_ov_list"])} ราย!</span>'
                 if data["sla_ov_list"] else '<span class="sla-badge-ok">✅ ทุกรายการอยู่ใน SLA</span>')

    with open("scripts/template_v6.html", encoding="utf-8") as f:
        html = f.read()

    html = (html
        .replace("%%ROWS%%",        rows_js)
        .replace("%%DETAILS%%",     details_js)
        .replace("%%KPI_SUMMARY%%", kpi_summary_js)
        .replace("%%ROWS_STARTED%%", rows_started_js)
        .replace("%%CONV_DATA%%",    conv_data_js)
        .replace("%%TREND_DATA%%",   trend_data_js)
        .replace("%%LEAD_DATA%%",    lead_data_js)
        .replace("%%MW_STATUS%%",    mw_status_js)
        .replace("%%MW_VOLTAGE%%",   mw_voltage_js)
        .replace("%%MW_MONTHLY%%",   mw_monthly_js)
        .replace("%%MW_DONE_MW%%",   str(data["mw_done_total"]))
        .replace("%%MW_PENDING_MW%%",str(data["mw_pending_total"]))
        .replace("%%MAP_DATA%%",     map_data_js)
        .replace("%%TOTAL%%",       str(data["total"]))
        .replace("%%FILE_DATE%%",   data["file_date"])
        .replace("%%CSV_NAME%%",    data["csv_name"])
        .replace("%%TODAY%%",       data["today"])
        .replace("%%SLA_ROWS%%",    sla_rows)
        .replace("%%SLA_BADGE%%",   sla_badge)
        .replace("%%SLA_OK%%",      str(data["sla_ok_count"]))
    )
    return html

def main():
    csv_path = find_latest_csv("data")
    if not csv_path:
        print("❌ ไม่พบไฟล์ ppim_report_*.csv ใน data/")
        sys.exit(1)

    data = process(csv_path)
    html = build_html(data)

    with open("PPIM_Dashboard_v6.html", "w", encoding="utf-8") as f:
        f.write(html)
    print(f"✅ สร้าง PPIM_Dashboard_v6.html สำเร็จ ({len(html)//1024} KB)")

if __name__ == "__main__":
    main()
