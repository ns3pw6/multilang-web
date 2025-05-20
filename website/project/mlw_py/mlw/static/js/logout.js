let sessionTimeout;
let countdownInterval;
const TIMEOUT_DURATION = 20 * 60 * 1000; // 20 mins
base_url = get_base_url();

function resetSessionTimeout() {
    clearTimeout(sessionTimeout);
    clearInterval(countdownInterval); // 清除之前的倒數計時

    sessionTimeout = setTimeout(() => {
        let remainingSeconds = 60;
        generateModalContent('alert', `閒置超過20分鐘，系統將在 ${remainingSeconds} 秒後自動登出...`);
        
        countdownInterval = setInterval(() => {
            remainingSeconds--;
            if (remainingSeconds > 0) {
                document.getElementsByClassName('modal-body')[0].innerHTML = 
                    `閒置超過20分鐘，系統將在 ${remainingSeconds} 秒後自動登出...`;
            } else {
                clearInterval(countdownInterval);
                window.location.href = `/${base_url}/logout`;
            }
        }, 1000);
    }, TIMEOUT_DURATION);
}

// ...existing code...

document.addEventListener('click', resetSessionTimeout);
document.addEventListener('DOMContentLoaded', resetSessionTimeout);