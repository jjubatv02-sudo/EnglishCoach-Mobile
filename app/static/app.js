let sessionId = null;
let exercise = null;
let total = 1;

const $ = (s) => document.querySelector(s);

async function api(url, options = {}) {
  const r = await fetch(url, options);
  if (!r.ok) throw new Error(`HTTP ${r.status}`);
  return r.json();
}

async function startSession() {
  try {
    const d = await api('/api/session/start', {method:'POST'});
    sessionId = d.session_id;
    total = d.total;
    $('#start').hidden = true;
    $('#done').hidden = true;
    $('#learn').hidden = false;
    showExercise(d);
  } catch (e) {
    alert('서버에 연결할 수 없습니다. PC의 EnglishCoach 서버가 실행 중인지 확인해주세요.');
  }
}

function showExercise(d) {
  exercise = d.exercise;
  total = d.total || total;
  $('#count').textContent = `${d.index} / ${total}`;
  $('#progressBar').style.width = `${Math.max(4, d.index / total * 100)}%`;
  $('#pattern').textContent = `연습 구조 · ${exercise.pattern}`;
  $('#prompt').textContent = exercise.prompt_ko;
  $('#answer').value = '';
  $('#answer').disabled = false;
  $('#feedback').innerHTML = '';
  $('#feedback').className = '';
  $('#next').hidden = true;
  $('#submitBtn').hidden = false;
  setTimeout(() => $('#answer').focus(), 120);
}

async function submitAnswer(e) {
  e.preventDefault();
  const input = $('#answer');
  const answer = input.value.trim();
  if (!answer) return;
  $('#submitBtn').disabled = true;
  try {
    const d = await api('/api/attempt', {
      method:'POST',
      headers:{'Content-Type':'application/json'},
      body:JSON.stringify({session_id:sessionId, exercise_id:exercise.id, answer})
    });
    const f = $('#feedback');
    f.textContent = d.teaching.message;
    if (d.teaching.retry_required) {
      f.className = 'feedback retry';
      input.value = '';
      input.focus();
    } else {
      f.className = 'feedback pass';
      input.disabled = true;
      $('#submitBtn').hidden = true;
      $('#next').hidden = false;
    }
  } catch (e) {
    alert('답변 처리 중 오류가 발생했습니다.');
  } finally {
    $('#submitBtn').disabled = false;
  }
}

async function nextExercise() {
  $('#next').disabled = true;
  try {
    const d = await api(`/api/session/${sessionId}/next`, {method:'POST'});
    if (d.done) {
      $('#learn').hidden = true;
      $('#done').hidden = false;
      $('#count').textContent = '완료';
      $('#summary').innerHTML = `
        <div class="summary-row"><span>총 시도</span><b>${d.summary.attempts}회</b></div>
        <div class="summary-row"><span>첫 시도 성공</span><b>${d.summary.first_try_success}개</b></div>
        <div class="summary-row"><span>힌트 후 성공</span><b>${d.summary.hint_recovery}개</b></div>`;
      window.scrollTo({top:0, behavior:'smooth'});
    } else {
      showExercise(d);
    }
  } catch (e) {
    alert('다음 문제를 불러오지 못했습니다.');
  } finally {
    $('#next').disabled = false;
  }
}
