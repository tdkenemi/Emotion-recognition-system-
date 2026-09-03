/**
 * EmotionAI - Main App JavaScript
 * Tác giả: Triệu Duy Khang | ĐH Nguyễn Tất Thành - Khoa CNTT
 * GitHub: https://github.com/tdkenemi
 */
(() => {
    'use strict';

    // =========================================================================
    // CONSTANTS
    // =========================================================================
    const EMOTIONS = [
        { key: 'Tức giận',    emoji: '😠', color: '#f87171' },
        { key: 'Ghê tởm',     emoji: '🤢', color: '#a3e635' },
        { key: 'Sợ hãi',      emoji: '😨', color: '#c084fc' },
        { key: 'Vui vẻ',      emoji: '😊', color: '#fbbf24' },
        { key: 'Bình thường', emoji: '😐', color: '#94a3b8' },
        { key: 'Buồn bã',     emoji: '😢', color: '#60a5fa' },
        { key: 'Bất ngờ',     emoji: '😮', color: '#34d399' }
    ];

    // =========================================================================
    // STATE
    // =========================================================================
    const state = {
        currentTab: 'upload',
        selectedFile: null,
        webcamStream: null,
        currentAIResult: null,
        selectedFeedbackEmotion: null,
        token: localStorage.getItem('emotionai_token') || null,
        user: null
    };

    // =========================================================================
    // DOM ELEMENTS
    // =========================================================================
    const $ = id => document.getElementById(id);

    const els = {
        toastContainer:     $('toast-container'),
        authModal:          $('auth-modal'),
        authButtons:        $('auth-buttons'),
        userMenu:           $('user-menu'),
        userDisplayName:    $('user-display-name'),
        navAdmin:           $('nav-admin'),

        tabUploadBtn:       $('tab-upload-btn'),
        tabCameraBtn:       $('tab-camera-btn'),
        tabUpload:          $('tab-upload'),
        tabCamera:          $('tab-camera'),

        dropZone:           $('drop-zone'),
        dropPlaceholder:    $('drop-placeholder'),
        fileInput:          $('file-input'),
        previewImg:         $('preview-img'),
        uploadActions:      $('upload-actions'),
        btnAnalyze:         $('btn-analyze'),
        btnResetUpload:     $('btn-reset-upload'),

        cameraOverlay:      $('camera-overlay'),
        webcam:             $('webcam'),
        canvas:             $('canvas'),
        captureControls:    $('capture-controls'),
        btnStartCam:        $('btn-start-cam'),
        btnCapture:         $('btn-capture'),
        btnStopCam:         $('btn-stop-cam'),

        loading:            $('loading'),
        resultPlaceholder:  $('result-placeholder'),
        resultPanel:        $('result-panel'),

        emotionName:        $('emotion-name'),
        emotionEmoji:       $('emotion-emoji'),
        faceImg:            $('face-img'),
        confidenceBadge:    $('confidence-badge'),
        confidenceIcon:     $('confidence-icon'),
        confidenceText:     $('confidence-text'),
        faceCountText:      $('face-count-text'),
        probBars:           $('prob-bars'),

        annotatedSection:   $('annotated-section'),
        annotatedImg:       $('annotated-img'),

        emotionSelector:    $('emotion-selector'),
        btnSubmitFeedback:  $('btn-submit-feedback'),

        emotionGallery:     $('emotion-gallery'),
    };

    // =========================================================================
    // INIT
    // =========================================================================
    function init() {
        renderEmotionGallery();
        renderEmotionSelector();
        checkAuthStatus();
        bindEvents();
        initAnimations();
    }

    function bindEvents() {
        // Auth Modal
        $('btn-open-login')?.addEventListener('click', () => openAuthModal('login'));
        $('btn-open-register')?.addEventListener('click', () => openAuthModal('register'));
        $('btn-close-auth-modal')?.addEventListener('click', closeAuthModal);
        $('btn-logout')?.addEventListener('click', logout);

        // Auth Tab Switchers (data-tab buttons)
        document.querySelectorAll('#auth-form-container [data-tab]').forEach(btn => {
            btn.addEventListener('click', () => switchAuthTab(btn.dataset.tab));
        });

        // Auth Forms
        $('form-login')?.addEventListener('submit', e => handleAuth(e, 'login'));
        $('form-register')?.addEventListener('submit', e => handleAuth(e, 'register'));

        // Close modal on overlay click
        els.authModal?.addEventListener('click', e => {
            if (e.target === els.authModal) closeAuthModal();
        });

        // Input Tabs
        els.tabUploadBtn?.addEventListener('click', () => switchTab('upload'));
        els.tabCameraBtn?.addEventListener('click', () => switchTab('camera'));

        // File Upload
        els.dropZone?.addEventListener('click', () => els.fileInput.click());
        els.dropZone?.addEventListener('keypress', e => { if (e.key === 'Enter') els.fileInput.click(); });
        els.dropZone?.addEventListener('dragover', e => {
            e.preventDefault();
            els.dropZone.style.borderColor = 'var(--primary)';
            els.dropZone.style.background = 'rgba(124, 58, 237, 0.05)';
        });
        els.dropZone?.addEventListener('dragleave', () => {
            els.dropZone.style.borderColor = '';
            els.dropZone.style.background = '';
        });
        els.dropZone?.addEventListener('drop', handleFileDrop);
        els.fileInput?.addEventListener('change', handleFileSelect);
        els.btnAnalyze?.addEventListener('click', analyzeImage);
        els.btnResetUpload?.addEventListener('click', resetUpload);

        // Camera
        els.btnStartCam?.addEventListener('click', startCamera);
        els.btnCapture?.addEventListener('click', captureAndAnalyze);
        els.btnStopCam?.addEventListener('click', stopCamera);

        // Feedback
        els.btnSubmitFeedback?.addEventListener('click', submitFeedback);

        // Keyboard shortcuts
        document.addEventListener('keydown', e => {
            if (e.key === 'Escape') {
                if (!els.authModal?.classList.contains('hidden')) closeAuthModal();
                else resetUpload();
            }
            if (e.key === 'Enter' && state.currentAIResult && state.selectedFeedbackEmotion) {
                submitFeedback();
            }
        });

        // Offline detection
        window.addEventListener('offline', () => showToast('Mất kết nối mạng!', 'error'));
        window.addEventListener('online',  () => showToast('Đã kết nối mạng trở lại.', 'success'));
    }

    function initAnimations() {
        if (typeof gsap === 'undefined') return;
        gsap.from('.navbar', { y: -20, opacity: 0, duration: 0.8, ease: 'power3.out' });
        gsap.from('.hero', { y: 40, opacity: 0, duration: 1, ease: 'power3.out', delay: 0.2 });
    }

    // =========================================================================
    // EMOTION GALLERY (section on homepage)
    // =========================================================================
    function renderEmotionGallery() {
        if (!els.emotionGallery) return;
        els.emotionGallery.innerHTML = EMOTIONS.map(e => `
            <div class="emo-pill" style="--emo-color:${e.color}">
                <span class="emo-pill-emoji">${e.emoji}</span>
                <span class="emo-pill-name">${e.key}</span>
            </div>
        `).join('');
    }

    // =========================================================================
    // TOAST
    // =========================================================================
    function showToast(message, type = 'success') {
        const icons = { success: '✅', error: '❌', warning: '⚠️', info: 'ℹ️' };
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.innerHTML = `
            <span class="toast-icon-wrap"><span class="toast-icon">${icons[type] || '✅'}</span></span>
            <div class="toast-body"><div class="toast-msg">${message}</div></div>
        `;
        els.toastContainer.appendChild(toast);

        if (typeof gsap !== 'undefined') {
            gsap.fromTo(toast,
                { x: 100, opacity: 0 },
                { x: 0, opacity: 1, duration: 0.35, ease: 'back.out(1.5)' }
            );
            setTimeout(() => {
                gsap.to(toast, {
                    x: 110, opacity: 0, duration: 0.3,
                    onComplete: () => toast.remove()
                });
            }, 3500);
        } else {
            setTimeout(() => toast.remove(), 3500);
        }
    }

    // =========================================================================
    // TAB SWITCHING (input panel)
    // =========================================================================
    function switchTab(tabId) {
        if (state.currentTab === tabId) return;
        if (state.currentTab === 'camera') stopCamera();
        state.currentTab = tabId;

        els.tabUploadBtn.classList.toggle('active', tabId === 'upload');
        els.tabCameraBtn.classList.toggle('active', tabId === 'camera');
        els.tabUpload.classList.toggle('hidden', tabId !== 'upload');
        els.tabCamera.classList.toggle('hidden', tabId !== 'camera');
        hideResult();
    }

    // =========================================================================
    // FILE UPLOAD
    // =========================================================================
    function handleFileDrop(e) {
        e.preventDefault();
        els.dropZone.style.borderColor = '';
        els.dropZone.style.background = '';
        if (e.dataTransfer.files?.length) processFile(e.dataTransfer.files[0]);
    }

    function handleFileSelect(e) {
        if (e.target.files?.length) processFile(e.target.files[0]);
    }

    function processFile(file) {
        if (!file.type.startsWith('image/')) {
            showToast('Vui lòng chọn file ảnh (JPG, PNG, WEBP)!', 'error');
            return;
        }
        if (file.size > 15 * 1024 * 1024) {
            showToast('Ảnh quá lớn! Tối đa 15MB.', 'error');
            return;
        }
        state.selectedFile = file;
        const reader = new FileReader();
        reader.onload = e => {
            els.previewImg.src = e.target.result;
            els.previewImg.style.display = 'block';
            els.dropPlaceholder.style.display = 'none';
            els.uploadActions.classList.remove('hidden');
            hideResult();
        };
        reader.readAsDataURL(file);
    }

    function resetUpload() {
        state.selectedFile = null;
        els.previewImg.src = '';
        els.previewImg.style.display = 'none';
        els.dropPlaceholder.style.display = 'flex';
        els.uploadActions.classList.add('hidden');
        els.fileInput.value = '';
        hideResult();
    }

    // =========================================================================
    // CAMERA
    // =========================================================================
    async function startCamera() {
        try {
            state.webcamStream = await navigator.mediaDevices.getUserMedia({
                video: { width: { ideal: 1280 }, height: { ideal: 720 } }
            });
            els.webcam.srcObject = state.webcamStream;
            els.cameraOverlay.style.display = 'none';
            els.captureControls.classList.remove('hidden');
        } catch (err) {
            const msg = err.name === 'NotAllowedError'
                ? 'Vui lòng cấp quyền truy cập camera trong trình duyệt.'
                : 'Không thể mở camera. Hãy kiểm tra kết nối thiết bị.';
            showToast(msg, 'error');
        }
    }

    function stopCamera() {
        state.webcamStream?.getTracks().forEach(t => t.stop());
        state.webcamStream = null;
        if (els.webcam) els.webcam.srcObject = null;
        if (els.cameraOverlay) els.cameraOverlay.style.display = 'flex';
        els.captureControls?.classList.add('hidden');
    }

    function captureAndAnalyze() {
        if (!state.webcamStream) return;
        els.canvas.width = els.webcam.videoWidth;
        els.canvas.height = els.webcam.videoHeight;
        els.canvas.getContext('2d').drawImage(els.webcam, 0, 0);
        els.canvas.toBlob(blob => {
            state.selectedFile = new File([blob], 'camera_capture.jpg', { type: 'image/jpeg' });
            analyzeImage();
        }, 'image/jpeg', 0.92);
    }

    // =========================================================================
    // API - ANALYZE
    // =========================================================================
    async function analyzeImage(retryCount = 1) {
        if (!state.selectedFile) return;
        if (!navigator.onLine) {
            showToast('Không có kết nối mạng!', 'error');
            return;
        }

        const formData = new FormData();
        formData.append('file', state.selectedFile);

        showLoading(true);
        hideResult();

        try {
            const headers = state.token ? { 'Authorization': `Bearer ${state.token}` } : {};
            const res = await fetch('/api/predict', { method: 'POST', body: formData, headers });
            const data = await res.json();
            showLoading(false);

            if (res.ok && data.success) {
                state.currentAIResult = { ...data, filename: state.selectedFile.name };
                displayResult(data);
                showToast('Phân tích thành công!', 'success');
            } else if (res.status === 429) {
                showToast('Bạn thử quá nhiều. Vui lòng đợi 1 phút.', 'warning');
            } else {
                showToast(data.detail || data.message || 'Không tìm thấy khuôn mặt.', 'error');
            }
        } catch (err) {
            if (retryCount > 0) {
                showToast('Mạng yếu, đang thử lại...', 'warning');
                setTimeout(() => analyzeImage(retryCount - 1), 2000);
            } else {
                showLoading(false);
                showToast('Lỗi kết nối máy chủ.', 'error');
            }
        }
    }

    // =========================================================================
    // RESULT DISPLAY
    // =========================================================================
    function showLoading(show) {
        if (show) {
            els.loading.classList.remove('hidden');
            els.loading.style.display = 'flex';
        } else {
            els.loading.classList.add('hidden');
            els.loading.style.display = 'none';
        }
    }

    function hideResult() {
        els.resultPanel?.classList.add('hidden');
        if (els.resultPlaceholder) els.resultPlaceholder.style.display = 'flex';
        state.currentAIResult = null;
        state.selectedFeedbackEmotion = null;
        document.querySelectorAll('.emotion-chip').forEach(c => c.classList.remove('selected'));
        if (els.btnSubmitFeedback) {
            els.btnSubmitFeedback.disabled = false;
            els.btnSubmitFeedback.innerHTML = '✅ Gửi Feedback';
            els.btnSubmitFeedback.className = 'btn btn-primary btn-full';
        }
    }

    function displayResult(data) {
        els.resultPlaceholder.style.display = 'none';
        els.resultPanel.classList.remove('hidden');

        const emoConfig = EMOTIONS.find(e => e.key === data.predicted_emotion) || EMOTIONS[4];

        // Face image
        els.faceImg.src = `data:image/jpeg;base64,${data.face_image_base64}`;

        // Emotion info
        els.emotionName.innerText = data.predicted_emotion;
        els.emotionName.style.color = emoConfig.color;
        els.emotionEmoji.innerText = emoConfig.emoji;

        // Face count
        if (els.faceCountText) {
            els.faceCountText.innerText = data.face_count > 1
                ? `Phát hiện ${data.face_count} khuôn mặt, phân tích khuôn mặt lớn nhất.`
                : 'Phát hiện 1 khuôn mặt.';
        }

        // Confidence badge
        els.confidenceText.innerText = `${data.confidence_label} (${data.confidence}%)`;
        els.confidenceBadge.className = 'confidence-badge ' + (
            data.confidence >= 75 ? 'high' : data.confidence >= 50 ? 'medium' : 'low'
        );

        // Annotated image (ảnh đã khoanh mặt)
        if (data.annotated_image_base64 && els.annotatedSection && els.annotatedImg) {
            els.annotatedImg.src = `data:image/jpeg;base64,${data.annotated_image_base64}`;
            els.annotatedSection.style.display = 'block';
        }

        // Probability bars
        els.probBars.innerHTML = '';
        const sorted = Object.entries(data.probabilities).sort((a, b) => b[1] - a[1]);
        sorted.forEach(([key, prob]) => {
            const cfg = EMOTIONS.find(e => e.key === key) || {};
            els.probBars.insertAdjacentHTML('beforeend', `
                <div class="prob-row" style="opacity:0;">
                    <div class="prob-label">${cfg.emoji || ''} ${key}</div>
                    <div class="prob-track">
                        <div class="prob-fill" data-width="${prob}" style="width:0%;background:${cfg.color}"></div>
                    </div>
                    <div class="prob-percent">${prob.toFixed(1)}%</div>
                </div>
            `);
        });

        // Animations
        if (typeof gsap !== 'undefined') {
            gsap.fromTo('.prob-row', { opacity: 0, y: 8 }, { opacity: 1, y: 0, duration: 0.35, stagger: 0.07 });
            document.querySelectorAll('.prob-fill').forEach(fill => {
                gsap.to(fill, { width: `${fill.dataset.width}%`, duration: 0.9, ease: 'power3.out', delay: 0.1 });
            });
            gsap.fromTo(els.emotionEmoji, { scale: 0, rotation: -30 }, { scale: 1, rotation: 0, duration: 0.5, ease: 'back.out(1.7)' });
        } else {
            document.querySelectorAll('.prob-fill').forEach(fill => {
                fill.style.width = `${fill.dataset.width}%`;
            });
            document.querySelectorAll('.prob-row').forEach(r => r.style.opacity = 1);
        }

        selectFeedbackEmotion(data.predicted_emotion);
    }

    // =========================================================================
    // FEEDBACK
    // =========================================================================
    function renderEmotionSelector() {
        if (!els.emotionSelector) return;
        els.emotionSelector.innerHTML = EMOTIONS.map(e => `
            <div class="emotion-chip" data-key="${e.key}" title="${e.key}">
                ${e.emoji} ${e.key}
            </div>
        `).join('');
        els.emotionSelector.querySelectorAll('.emotion-chip').forEach(chip => {
            chip.addEventListener('click', () => selectFeedbackEmotion(chip.dataset.key));
        });
    }

    function selectFeedbackEmotion(key) {
        state.selectedFeedbackEmotion = key;
        document.querySelectorAll('.emotion-chip').forEach(c => {
            c.classList.toggle('selected', c.dataset.key === key);
        });
    }

    async function submitFeedback() {
        if (!state.currentAIResult || !state.selectedFeedbackEmotion) {
            showToast('Vui lòng chọn cảm xúc đúng trước!', 'warning');
            return;
        }

        const btn = els.btnSubmitFeedback;
        btn.disabled = true;
        btn.innerHTML = 'Đang gửi...';

        const formData = new FormData();
        formData.append('filename', state.currentAIResult.filename || 'unknown');
        formData.append('ai_prediction', state.currentAIResult.predicted_emotion);
        formData.append('correct_emotion', state.selectedFeedbackEmotion);

        const headers = state.token ? { 'Authorization': `Bearer ${state.token}` } : {};

        try {
            const res = await fetch('/api/feedback', { method: 'POST', body: formData, headers });
            const data = await res.json();
            if (res.ok && data.success) {
                showToast('Đã ghi nhận! Cảm ơn bạn đã giúp AI cải thiện.', 'success');
                btn.innerHTML = '✅ Đã gửi thành công';
                btn.className = 'btn btn-accent btn-full';
            } else {
                showToast('Lỗi gửi feedback.', 'error');
                btn.disabled = false;
                btn.innerHTML = '✅ Gửi Feedback';
            }
        } catch {
            showToast('Lỗi mạng.', 'error');
            btn.disabled = false;
            btn.innerHTML = '✅ Gửi Feedback';
        }
    }

    // =========================================================================
    // AUTHENTICATION
    // =========================================================================
    async function checkAuthStatus() {
        if (!state.token) return;
        try {
            const res = await fetch('/api/me', { headers: { 'Authorization': `Bearer ${state.token}` } });
            if (res.ok) {
                state.user = await res.json();
                updateNavForUser(state.user);
            } else {
                doLogout(false);
            }
        } catch {
            // Offline — keep state
        }
    }

    function updateNavForUser(user) {
        els.authButtons?.classList.add('hidden');
        els.userMenu?.classList.remove('hidden');
        if (els.userDisplayName) els.userDisplayName.innerText = `👋 ${user.username}`;
        if (els.navAdmin) {
            els.navAdmin.style.display = user.role === 'admin' ? '' : 'none';
        }
    }

    function openAuthModal(tab = 'login') {
        els.authModal?.classList.remove('hidden');
        switchAuthTab(tab);
    }

    function closeAuthModal() {
        els.authModal?.classList.add('hidden');
    }

    function switchAuthTab(tab) {
        document.querySelectorAll('#auth-form-container [data-tab]').forEach(btn => {
            btn.classList.toggle('active', btn.dataset.tab === tab);
        });
        $('form-login').classList.toggle('hidden', tab !== 'login');
        $('form-register').classList.toggle('hidden', tab !== 'register');
    }

    async function handleAuth(e, action) {
        e.preventDefault();
        const username = $(`${action}-username`).value.trim();
        const password = $(`${action}-password`).value;
        const btn = $(`btn-submit-${action}`);

        if (!username || !password) return;
        btn.disabled = true;
        btn.innerText = 'Đang xử lý...';

        const formData = new FormData();
        formData.append('username', username);
        formData.append('password', password);

        try {
            const res = await fetch(`/api/${action}`, { method: 'POST', body: formData });
            const data = await res.json();

            if (res.ok) {
                if (action === 'register') {
                    showToast('Đăng ký thành công! Đang đăng nhập...', 'success');
                    // Auto-fill login form
                    $('login-username').value = username;
                    $('login-password').value = password;
                    switchAuthTab('login');
                    // Auto login after 800ms
                    setTimeout(() => $('form-login').dispatchEvent(new Event('submit')), 800);
                } else {
                    localStorage.setItem('emotionai_token', data.access_token);
                    state.token = data.access_token;
                    state.user = { username: data.username, role: data.role };
                    updateNavForUser(state.user);
                    closeAuthModal();
                    showToast(`Chào mừng, ${data.username}!`, 'success');
                }
            } else {
                showToast(data.detail || 'Có lỗi xảy ra', 'error');
            }
        } catch {
            showToast('Lỗi kết nối mạng', 'error');
        }
        btn.disabled = false;
        btn.innerText = action === 'login' ? 'Đăng Nhập' : 'Tạo tài khoản';
    }

    function logout() { doLogout(true); }

    function doLogout(showMsg = true) {
        localStorage.removeItem('emotionai_token');
        state.token = null;
        state.user = null;
        els.authButtons?.classList.remove('hidden');
        els.userMenu?.classList.add('hidden');
        if (els.navAdmin) els.navAdmin.style.display = 'none';
        if (showMsg) showToast('Đã đăng xuất thành công.', 'info');
    }

    // =========================================================================
    // START
    // =========================================================================
    document.addEventListener('DOMContentLoaded', init);
    if (document.readyState !== 'loading') init();
})();
