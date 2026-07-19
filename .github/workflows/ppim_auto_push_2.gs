/**
 * PPIM Auto Push — Google Apps Script
 * ดึงไฟล์ CSV ล่าสุดจาก Drive Folder แล้ว Push ขึ้น GitHub
 * Trigger: ทันทีเมื่อมีไฟล์ใหม่เข้า Folder (Drive onChange)
 */

const CONFIG = {
  DRIVE_FOLDER_ID: '1YZfC27xatz1iCpd7cXfPEjtOzrNbfcJ3',
  GITHUB_OWNER:    'Pasasorn',
  GITHUB_REPO:     'ppim-dashboard',
  GITHUB_BRANCH:   'main',
  GITHUB_PATH:     'data/',
  GITHUB_TOKEN:    'YOUR_GITHUB_TOKEN_HERE',  // ← ใส่ Token ของคุณตรงนี้
};

/**
 * ฟังก์ชันหลัก — ตรวจสอบว่ามีไฟล์ CSV ใหม่ แล้ว Push ขึ้น GitHub
 * ถูกเรียกโดย Drive onChange Trigger อัตโนมัติ
 */
function checkAndPushLatestCSV() {
  try {
    Logger.log('🔍 กำลังตรวจสอบไฟล์ CSV ใหม่ใน Drive...');

    const folder = DriveApp.getFolderById(CONFIG.DRIVE_FOLDER_ID);
    const files  = folder.getFilesByType(MimeType.CSV);

    // หาไฟล์ล่าสุด
    let latestFile = null;
    let latestDate = new Date(0);
    while (files.hasNext()) {
      const f = files.next();
      const d = f.getLastUpdated();
      if (d > latestDate) { latestDate = d; latestFile = f; }
    }

    if (!latestFile) {
      Logger.log('❌ ไม่พบไฟล์ CSV ใน Folder');
      return;
    }

    const fileName   = latestFile.getName();
    const fileTimeMs = latestDate.getTime();

    // เปรียบเทียบกับไฟล์ที่ Push ครั้งล่าสุด (เก็บไว้ใน PropertiesService)
    const props        = PropertiesService.getScriptProperties();
    const lastPushed   = props.getProperty('LAST_PUSHED_FILE');
    const lastPushedMs = parseInt(props.getProperty('LAST_PUSHED_TIME') || '0');

    if (lastPushed === fileName && fileTimeMs <= lastPushedMs) {
      Logger.log(`⏭ ไม่มีไฟล์ใหม่ (ล่าสุดคือ ${fileName} ที่ Push ไปแล้ว)`);
      return;
    }

    Logger.log(`📄 พบไฟล์ใหม่: ${fileName} (อัพเดต: ${latestDate})`);

    // อ่านและแปลงเป็น Base64
    const content = Utilities.base64Encode(latestFile.getBlob().getBytes());
    const apiPath = `${CONFIG.GITHUB_PATH}${fileName}`;
    const sha     = getFileSHA(apiPath);

    // Push ขึ้น GitHub
    const url     = `https://api.github.com/repos/${CONFIG.GITHUB_OWNER}/${CONFIG.GITHUB_REPO}/contents/${apiPath}`;
    const payload = {
      message: `Auto-update: ${fileName} (${Utilities.formatDate(new Date(), 'Asia/Bangkok', 'yyyy-MM-dd HH:mm')})`,
      content: content,
      branch:  CONFIG.GITHUB_BRANCH,
    };
    if (sha) payload.sha = sha;

    const response = UrlFetchApp.fetch(url, {
      method:             'PUT',
      headers:            { 'Authorization': `token ${CONFIG.GITHUB_TOKEN}`, 'Content-Type': 'application/json', 'Accept': 'application/vnd.github+json' },
      payload:            JSON.stringify(payload),
      muteHttpExceptions: true,
    });

    const code = response.getResponseCode();
    if (code === 200 || code === 201) {
      // บันทึกว่า Push ไฟล์ไหนไปแล้ว
      props.setProperty('LAST_PUSHED_FILE', fileName);
      props.setProperty('LAST_PUSHED_TIME', String(fileTimeMs));
      Logger.log(`✅ Push สำเร็จ! ${fileName} → GitHub data/${fileName}`);
      Logger.log('⚡ GitHub Actions จะรัน process.py และอัพเดต Dashboard อัตโนมัติ');
    } else {
      Logger.log(`❌ Push ล้มเหลว (HTTP ${code}): ${response.getContentText()}`);
    }

  } catch (err) {
    Logger.log(`❌ Error: ${err.message}`);
  }
}

/**
 * ดึง SHA ของไฟล์บน GitHub (ต้องใช้ตอน update ไฟล์เดิม)
 */
function getFileSHA(path) {
  try {
    const url = `https://api.github.com/repos/${CONFIG.GITHUB_OWNER}/${CONFIG.GITHUB_REPO}/contents/${path}?ref=${CONFIG.GITHUB_BRANCH}`;
    const res = UrlFetchApp.fetch(url, {
      headers:            { 'Authorization': `token ${CONFIG.GITHUB_TOKEN}`, 'Accept': 'application/vnd.github+json' },
      muteHttpExceptions: true,
    });
    if (res.getResponseCode() === 200) return JSON.parse(res.getContentText()).sha;
    return null;
  } catch (e) { return null; }
}

/**
 * ตั้ง Trigger แบบ Drive onChange
 * รันฟังก์ชันนี้ครั้งเดียว — จะ Trigger ทุกครั้งที่มีการเปลี่ยนแปลงใน Drive
 */
function setTrigger() {
  // ลบ Trigger เก่าทิ้งก่อน
  ScriptApp.getProjectTriggers().forEach(t => ScriptApp.deleteTrigger(t));

  // Trigger 1: Drive onChange — ทำงานทันทีเมื่อมีไฟล์เปลี่ยนแปลงใน Drive
  ScriptApp.newTrigger('checkAndPushLatestCSV')
    .forUserCalendar(Session.getActiveUser().getEmail())
    .onEventUpdated()
    .create();

  // Trigger 2: สำรอง — รันทุก 1 ชั่วโมง เผื่อ Drive Trigger พลาด
  ScriptApp.newTrigger('checkAndPushLatestCSV')
    .timeBased()
    .everyHours(1)
    .create();

  Logger.log('✅ ตั้ง Trigger เรียบร้อย:');
  Logger.log('   - Drive onChange: ทำงานทันทีเมื่อมีไฟล์ใหม่');
  Logger.log('   - Backup Timer: รันทุก 1 ชั่วโมง');
}

/**
 * ทดสอบการเชื่อมต่อ Drive และ GitHub
 */
function setup() {
  try {
    const folder = DriveApp.getFolderById(CONFIG.DRIVE_FOLDER_ID);
    Logger.log(`✅ Drive Folder: "${folder.getName()}" — เข้าถึงได้`);
  } catch(e) {
    Logger.log(`❌ Drive Error: ${e.message}`);
    return;
  }

  const res = UrlFetchApp.fetch(
    `https://api.github.com/repos/${CONFIG.GITHUB_OWNER}/${CONFIG.GITHUB_REPO}`,
    { headers: { 'Authorization': `token ${CONFIG.GITHUB_TOKEN}` }, muteHttpExceptions: true }
  );
  if (res.getResponseCode() === 200) {
    Logger.log(`✅ GitHub: เชื่อมต่อ repo "${CONFIG.GITHUB_REPO}" ได้`);
    Logger.log('👍 พร้อมใช้งาน! รัน setTrigger() เพื่อตั้ง Trigger');
  } else {
    Logger.log(`❌ GitHub Token Error (HTTP ${res.getResponseCode()})`);
  }
}
