// ══════════════════════════════════════════════
//  ★ 반드시 본인 값으로 수정하세요 ★
// ══════════════════════════════════════════════
var SPREADSHEET_ID   = 'YOUR_SPREADSHEET_ID';
var TEACHER_PASSWORD = 'math2026';
// ══════════════════════════════════════════════

// ── 페이지 라우팅 ──────────────────────────────
function doGet(e) {
  var page  = (e && e.parameter && e.parameter.page) || 'student';
  var file  = (page === 'teacher') ? 'teacher' : 'student';
  var title = (page === 'teacher') ? '교사용 대시보드' : '플레이리스트로 순열 살펴보기';
  
  return HtmlService.createHtmlOutputFromFile(file)
    .setTitle(title)
    .setXFrameOptionsMode(HtmlService.XFrameOptionsMode.ALLOWALL);
}

// ── 교사 비밀번호 검증 ─────────────────────────
function checkTeacherPassword(pw) {
  if (pw !== TEACHER_PASSWORD) return { ok: false };
  var url = ScriptApp.getService().getUrl() + '?page=teacher';
  return { ok: true, url: url };
}

// ── 시트 가져오기 (없으면 자동 생성) ──────────────
function getSheet_() {
  var ss    = SpreadsheetApp.openById(SPREADSHEET_ID);
  var sheet = ss.getSheetByName('submissions');

  if (!sheet) {
    sheet = ss.insertSheet('submissions');
    sheet.appendRow([
      '최종수정', '이름', '반/조', '현재단계',
      '선택조건', '경우의수', '풀이과정', '조별토의',
      '역설계목표', '전체데이터', '세션ID', '제출여부'
    ]);
    sheet.setFrozenRows(1);
    sheet.getRange(1, 1, 1, 12)
         .setBackground('#1a73e8')
         .setFontColor('#ffffff')
         .setFontWeight('bold');
    sheet.setColumnWidth(10, 400); 
  }
  return sheet;
}

// ── 세션 upsert (없으면 추가, 있으면 업데이트) ───────
function upsertSession(sessionId, data) {
  try {
    var sheet   = getSheet_();
    var lastRow = sheet.getLastRow();
    var rowIdx  = -1;

    if (lastRow > 1) {
      var ids = sheet.getRange(2, 11, lastRow - 1, 1).getValues();
      for (var i = 0; i < ids.length; i++) {
        if (ids[i][0] === sessionId) {
          rowIdx = i + 2;
          break;
        }
      }
    }

    var row = [
      new Date(),
      data.studentName  || '',
      data.classCode    || '',
      data.currentStep  || 1,
      data.condition    ? data.condition.label  : '전체 조건 완료', // 하위 호환성
      data.condition    ? data.condition.result : '',
      data.solution     || '',
      data.discussion   || '',
      data.targetCount  || '',
      JSON.stringify(data), // 새 구조의 데이터는 전체데이터(JSON)로 저장
      sessionId,                         
      data.submitted ? '제출완료' : '진행중'
    ];

    if (rowIdx === -1) {
      sheet.appendRow(row);
    } else {
      sheet.getRange(rowIdx, 1, 1, row.length).setValues([row]);
    }
    return { success: true };
  } catch (err) {
    return { success: false, error: err.toString() };
  }
}

// ── 전체 제출 목록 조회 (교사용 대시보드) ─────────────
function getSubmissions() {
  try {
    var sheet   = getSheet_();
    var lastRow = sheet.getLastRow();
    if (lastRow <= 1) return [];

    var rows = sheet.getRange(2, 10, lastRow - 1, 1).getValues();
    return rows
      .map(function(row) {
        try   { return JSON.parse(row[0]); }
        catch { return null; }
      })
      .filter(Boolean)
      .reverse();
  } catch (err) {
    return [];
  }
}

// ── 세션 삭제 (교사용) ──────────────────────────────
function deleteSession(sessionId) {
  try {
    var sheet   = getSheet_();
    var lastRow = sheet.getLastRow();
    if (lastRow <= 1) return { success: false, error: '데이터 없음' };

    var ids = sheet.getRange(2, 11, lastRow - 1, 1).getValues();
    for (var i = 0; i < ids.length; i++) {
      if (ids[i][0] === sessionId) {
        sheet.deleteRow(i + 2);
        return { success: true };
      }
    }
    return { success: false, error: '해당 세션을 찾을 수 없습니다.' };
  } catch (err) {
    return { success: false, error: err.toString() };
  }
}

// ── 이름+반+조로 이전 세션 불러오기 (새로고침 복원용) ──────
function getSavedSessionByIdentity(name, cls, group, members) {
  try {
    var sheet   = getSheet_();
    var lastRow = sheet.getLastRow();
    if (lastRow <= 1) return { success: true, found: false };

    var rowCount = lastRow - 1;

    // 각 컬럼을 별도로 읽기 (정확한 인덱스 보장)
    // col2 = 이름, col3 = classCode(반), col10 = 전체JSON
    var nameVals = sheet.getRange(2, 2,  rowCount, 1).getValues();
    var clsVals  = sheet.getRange(2, 3,  rowCount, 1).getValues();
    var jsonVals = sheet.getRange(2, 10, rowCount, 1).getValues();

    // 역순(최신순)으로 탐색
    for (var i = rowCount - 1; i >= 0; i--) {
      var rowName = String(nameVals[i][0] || '').trim();
      var rowCls  = String(clsVals[i][0]  || '').trim();

      // 이름과 반이 일치하는 행 탐색
      if (rowName !== name || rowCls !== cls) continue;

      try {
        var data = JSON.parse(jsonVals[i][0]);

        // 조도 확인 (저장된 JSON 안의 groupName과 비교)
        var dataGroup = String(data.groupName || '').trim();
        if (group && dataGroup && dataGroup !== group) continue;

        return { success: true, found: true, data: data };
      } catch(e) {
        continue; // JSON 파싱 실패 시 다음 행으로
      }
    }

    return { success: true, found: false };

  } catch (err) {
    return { success: false, error: err.toString() };
  }
}
