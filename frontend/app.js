const API_BASE = '/api';

const topicInput = document.getElementById('topicInput');
const runBtn = document.getElementById('runBtn');
const loader = document.querySelector('.loader');
const btnText = document.querySelector('.btn-text');
const postsContainer = document.getElementById('postsContainer');
const postTemplate = document.getElementById('postTemplate');
const refreshBtn = document.getElementById('refreshBtn');

// State
let posts = [];
let selectedTopic = null;
let showAllHistory = false;

const historyList = document.getElementById('historyList');
const dashboardLink = document.getElementById('dashboardLink');
const progressTemplate = document.getElementById('progressTemplate');

// Init
document.addEventListener('DOMContentLoaded', () => {
    fetchPosts();
    // Auto refresh every 10 seconds
    setInterval(fetchPosts, 10000);
});

refreshBtn.addEventListener('click', fetchPosts);
dashboardLink.addEventListener('click', (e) => {
    e.preventDefault();
    selectedTopic = null;
    document.querySelectorAll('.history-item').forEach(i => i.classList.remove('active'));
    renderPosts(posts);
});

const historyToggleBtn = document.getElementById('historyToggleBtn');
const historyToggleContainer = document.getElementById('historyToggleContainer');

historyToggleBtn.addEventListener('click', () => {
    showAllHistory = !showAllHistory;
    historyToggleBtn.textContent = showAllHistory ? 'Show Less' : 'Show More';
    renderHistory(posts);
});

runBtn.addEventListener('click', async () => {
    const topic = topicInput.value.trim();
    if (!topic) return;

    await runWorkflow({
        topic,
        platform: document.getElementById('platformSelect').value,
        duration: parseInt(document.getElementById('durationSelect').value),
        tone: document.getElementById('toneSelect').value,
        use_captions: document.getElementById('captionToggle').checked
    });
});

async function runWorkflow(config) {
    setLoading(true);

    try {
        const res = await fetch(`${API_BASE}/run-workflow`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(config)
        });

        if (res.ok) {
            topicInput.value = '';
            // Silent start, card will appear via fetchPosts polling
            fetchPosts();
        } else {
            alert('Failed to start workflow');
        }
    } catch (e) {
        console.error(e);
        alert('Error connecting to agent');
    } finally {
        setLoading(false);
    }
}

function setLoading(isLoading) {
    if (isLoading) {
        loader.classList.remove('hidden');
        btnText.textContent = 'Agent Running...';
        runBtn.disabled = true;
    } else {
        loader.classList.add('hidden');
        btnText.textContent = 'Initialize Agent';
        runBtn.disabled = false;
    }
}

let lastPostsJSON = "";

async function fetchPosts() {
    try {
        const res = await fetch(`${API_BASE}/posts`);
        const newPosts = await res.json();

        const currentJSON = JSON.stringify(newPosts);
        if (currentJSON === lastPostsJSON) return;

        lastPostsJSON = currentJSON;
        posts = newPosts;

        renderHistory(posts);
        renderPosts(posts);
    } catch (e) {
        console.error("Failed to fetch posts:", e);
    }
}

function renderHistory(postData) {
    if (!historyList) return;

    // Get unique topics and reverse to show latest first
    let topics = [...new Set(postData.filter(p => p.topic).map(p => p.topic))].reverse();

    // Handle Show More / Show Less logic
    if (topics.length > 2) {
        historyToggleContainer.classList.remove('hidden');
        if (!showAllHistory) {
            topics = topics.slice(0, 2);
        }
    } else {
        historyToggleContainer.classList.add('hidden');
    }

    historyList.innerHTML = '';

    topics.forEach(topic => {
        const item = document.createElement('div');
        item.className = `history-item ${selectedTopic === topic ? 'active' : ''}`;
        item.innerHTML = `
            <div class="topic-info">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h12a2 2 0 0 1 2 2z"></path>
                </svg>
                <span>${topic}</span>
            </div>
            <button class="delete-btn" title="Delete Topic History">
                <i class="fas fa-trash-alt"></i>
            </button>
        `;

        item.addEventListener('click', () => {
            selectedTopic = topic;
            renderHistory(posts);
            renderPosts(posts);
        });

        const delBtn = item.querySelector('.delete-btn');
        delBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            if (confirm(`Delete all missions for "${topic}"?`)) {
                deleteTopicMissions(topic);
            }
        });

        historyList.appendChild(item);
    });
}

function renderPosts(postData) {
    let displayData = postData;
    if (selectedTopic) {
        displayData = postData.filter(p => p.topic === selectedTopic);
    }

    if (!selectedTopic) {
        // Show everything except missions in progress or errors (unless they are relevant)
        // Actually, let's just show everything in the dashboard for a better "Gallery" feel
        displayData = postData;

        if (displayData.length === 0) {
            postsContainer.innerHTML = `<div class="empty-state"><p>Your production gallery is empty. Use the <strong>Content Engineering</strong> suite on the left to start your first mission.</p></div>`;
            return;
        }
    }

    postsContainer.innerHTML = '';

    displayData.forEach(post => {
        if (['INITIALIZING', 'SEARCHING', 'ANALYZING', 'GENERATING', 'ERROR'].includes(post.status)) {
            renderProgressCard(post);
            return;
        }

        const clone = postTemplate.content.cloneNode(true);
        const card = clone.querySelector('.post-card');

        const date = new Date(post.created_at);
        clone.querySelector('.timestamp').textContent = date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

        const title = post.draft && post.draft.title ? post.draft.title : "Processing...";
        clone.querySelector('.post-title').textContent = title;

        if (post.analysis) {
            clone.querySelector('.virality-score').textContent = `${post.analysis.virality_score}/10`;
            clone.querySelector('.hook-type').textContent = post.analysis.hook_technique;
        }

        if (post.draft) {
            // Hide details that are not the main video output by default
            const detailsDiv = document.createElement('div');
            detailsDiv.className = 'post-details-collapsible hidden';

            clone.querySelector('.script-text').textContent = post.draft.script;
            clone.querySelector('.visual-text').textContent = post.draft.visual_prompt.substring(0, 80) + '...';

            const imageUrl = post.image_url || (post.draft && post.draft.image_url);
            const videoUrl = post.video_url || (post.draft && post.draft.video_url);

            if (imageUrl || videoUrl) {
                const img = clone.querySelector('.generated-image');
                const video = clone.querySelector('.generated-video');
                const visualDiv = clone.querySelector('.post-visual');
                const overlay = clone.querySelector('.play-overlay');
                const muteBtn = clone.querySelector('.mute-btn');
                const unmuteIcon = muteBtn.querySelector('.unmute-icon');
                const muteIcon = muteBtn.querySelector('.mute-icon');

                const payoffText = clone.querySelector('.payoff-text');
                const hookList = clone.querySelector('.hook-list');

                if (post.analysis && post.analysis.hook_variations) {
                    post.analysis.hook_variations.forEach(hook => {
                        const li = document.createElement('li');
                        li.textContent = `• ${hook}`;
                        hookList.appendChild(li);
                    });
                }

                if (post.draft && post.draft.emotional_payoff) {
                    payoffText.textContent = post.draft.emotional_payoff;
                }

                visualDiv.classList.remove('hidden');

                if (videoUrl) {
                    video.src = videoUrl;
                    video.classList.remove('hidden');
                    img.classList.add('hidden');
                    overlay.classList.remove('hidden');

                    video.onerror = () => {
                        console.warn(`Video failed to load: ${videoUrl}`);
                        visualDiv.classList.add('hidden');
                    };

                    const captionsDiv = clone.querySelector('.video-captions');
                    let captionInterval;

                    visualDiv.addEventListener('mouseenter', () => {
                        video.muted = true;
                        video.play().catch(e => console.log("Playback block:", e));
                        overlay.classList.add('hidden');
                        muteBtn.classList.remove('hidden');

                        const useCaptions = post.use_captions !== false; // Default to true if not specified
                        if (post.draft && post.draft.script && useCaptions) {
                            captionsDiv.classList.remove('hidden');
                            const words = post.draft.script.split(/\s+/);
                            // Group words into chunks of 3 for TikTok style
                            const chunks = [];
                            for (let i = 0; i < words.length; i += 3) {
                                chunks.push(words.slice(i, i + 3).join(' '));
                            }

                            let currentChunk = 0;
                            const showNextChunk = () => {
                                if (chunks[currentChunk]) {
                                    captionsDiv.innerHTML = `<span class="caption-word">${chunks[currentChunk]}</span>`;
                                }
                                currentChunk = (currentChunk + 1) % chunks.length;
                            };

                            const startCaptions = () => {
                                clearInterval(captionInterval);
                                // Sync interval to video duration
                                const duration = video.duration && video.duration > 0 ? video.duration : 15;
                                const interval = (duration * 1000) / chunks.length;
                                showNextChunk();
                                captionInterval = setInterval(showNextChunk, interval);
                            };

                            if (video.readyState >= 1) {
                                startCaptions();
                            } else {
                                video.addEventListener('loadedmetadata', startCaptions, { once: true });
                            }
                        }
                    });

                    visualDiv.addEventListener('mouseleave', () => {
                        video.pause();
                        overlay.classList.remove('hidden');
                        muteBtn.classList.add('hidden');
                        captionsDiv.classList.add('hidden');
                        clearInterval(captionInterval);
                    });

                    muteBtn.addEventListener('click', (e) => {
                        e.stopPropagation();
                        video.muted = !video.muted;
                        if (video.muted) {
                            unmuteIcon.classList.add('hidden');
                            muteIcon.classList.remove('hidden');
                        } else {
                            unmuteIcon.classList.remove('hidden');
                            muteIcon.classList.add('hidden');
                        }
                    });
                } else if (imageUrl) {
                    img.src = imageUrl;
                    img.classList.remove('hidden');
                }
            }
        }

        // Actions
        const downloadBtn = clone.querySelector('.download-btn');
        downloadBtn.addEventListener('click', () => downloadVideo(post));

        postsContainer.appendChild(clone);
    });
}

function downloadVideo(post) {
    const videoUrl = post.video_url || (post.draft && post.draft.video_url);
    if (videoUrl) {
        const aVideo = document.createElement('a');
        aVideo.href = videoUrl;
        aVideo.download = `video_${post.draft.title.toLowerCase().replace(/\s+/g, '_')}.mp4`;
        aVideo.target = "_blank";
        aVideo.click();
    } else {
        alert('Video not yet available.');
    }
}

async function handleApproval(postId, action) {
    try {
        const res = await fetch(`${API_BASE}/approve/${postId}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ action })
        });

        if (res.ok) {
            fetchPosts(); // Refresh UI to show APPROVED
            if (action === 'APPROVE') {
                // Wait for simulated backend delay and refresh again to show PUBLISHED
                setTimeout(() => fetchPosts(), 2500);
            }
        }
    } catch (e) {
        console.error(e);
        alert("Action failed");
    }
}

function renderProgressCard(post) {
    const clone = progressTemplate.content.cloneNode(true);
    const card = clone.querySelector('.post-card');

    clone.querySelector('.mission-topic').textContent = post.topic;
    clone.querySelector('.status-badge').textContent = post.status.replace('_', ' ');
    clone.querySelector('.status-badge').className = `status-badge ${post.status}`;

    const stepsContainer = clone.querySelector('.production-steps');

    if (post.status === 'ERROR') {
        card.classList.add('error-state');
        clone.querySelector('.status-badge').textContent = 'FAILED';
        clone.querySelector('.progress-footer-text').innerHTML = `<span style="color:var(--danger)">Production halted: An error occurred.</span>`;
        stepsContainer.innerHTML = '<p style="color:var(--danger); font-size:0.8rem;">Workflow failed at current stage.</p>';

        const actionsDiv = clone.querySelector('.progress-actions');
        actionsDiv.classList.remove('hidden');

        const resumeBtn = actionsDiv.querySelector('.resume-btn');
        resumeBtn.addEventListener('click', () => {
            resumeBtn.disabled = true;
            resumeBtn.innerHTML = '<div class="loader" style="width:16px; height:16px;"></div> Resuming...';
            // Re-trigger workflow with same topic
            runWorkflow({
                topic: post.topic,
                tone: post.tone || 'Professional',
                duration: post.duration || 60,
                platform: post.platform || 'TikTok',
                use_captions: post.use_captions !== false
            });
        });

        const discardBtn = actionsDiv.querySelector('.discard-btn');
        discardBtn.addEventListener('click', () => {
            if (confirm('Discard this incomplete production?')) {
                deleteSinglePost(post.id);
            }
        });
    } else {
        renderProgressSteps(stepsContainer, post);
    }

    postsContainer.appendChild(clone);
}

async function deleteTopicMissions(topic) {
    const topicPosts = posts.filter(p => p.topic === topic);
    for (const post of topicPosts) {
        await fetch(`${API_BASE}/posts/${post.id}`, { method: 'DELETE' });
    }
    if (selectedTopic === topic) selectedTopic = null;
    fetchPosts();
}

async function deleteSinglePost(postId) {
    const res = await fetch(`${API_BASE}/posts/${postId}`, { method: 'DELETE' });
    if (res.ok) fetchPosts();
}

/**
 * Renders the staged progress bars for an active mission.
 */
function renderProgressSteps(container, post) {
    const steps = [
        { id: 'scripting', label: 'Creative Scripting', start: 0, end: 20 },
        { id: 'content', label: 'Draft Generation', start: 20, end: 40 },
        { id: 'voiceover', label: 'Voiceover Rendering', start: 40, end: 60 },
        { id: 'animation', label: 'Cinematic Animation', start: 60, end: 90 },
        { id: 'assembly', label: 'Final Assembly', start: 90, end: 100 }
    ];

    container.innerHTML = '';
    const currentProgress = post.progress || 0;

    steps.forEach(step => {
        const isCompleted = currentProgress >= step.end;
        const isActive = currentProgress >= step.start && currentProgress < step.end;

        const stepEl = document.createElement('div');
        stepEl.className = `progress-step-item ${isCompleted ? 'completed' : ''} ${isActive ? 'active' : ''}`;

        let stepPercent = 0;
        if (isCompleted) stepPercent = 100;
        else if (isActive) {
            const range = step.end - step.start;
            const progressInRange = currentProgress - step.start;
            stepPercent = Math.round((progressInRange / range) * 100);
        }

        const percentText = isCompleted ? '100% done' : `${stepPercent}%`;

        stepEl.innerHTML = `
            <div class="progress-label-row">
                <span class="step-label">${step.label}</span>
                <span class="step-percent">${percentText}</span>
            </div>
            <div class="progress-bar-container">
                <div class="progress-fill" style="width: ${stepPercent}%"></div>
            </div>
        `;
        container.appendChild(stepEl);
    });
}

// Initial fetch
fetchPosts();
