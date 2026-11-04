// Turns HTML-special characters into entities, the way Django's template
// auto-escaping does, for values a page injects through innerHTML itself.
function escapeHtml(value) {
    return String(value ?? '')
        .replaceAll('&', '&amp;')
        .replaceAll('<', '&lt;')
        .replaceAll('>', '&gt;')
        .replaceAll('"', '&quot;')
        .replaceAll("'", '&#39;');
}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function projectEndpoint(pattern, id) {
    return pattern.replace('/0/', `/${encodeURIComponent(id)}/`);
}

function apiErrorMessage(data, status) {
    if (!data || typeof data !== 'object') return `Permintaan gagal (HTTP ${status}).`;
    return Object.entries(data).map(([field, errors]) => {
        const message = Array.isArray(errors) ? errors.join(' ') : String(errors);
        return field === 'detail' ? message : `${field}: ${message}`;
    }).join(' ') || `Permintaan gagal (HTTP ${status}).`;
}

async function writeProject(url, method, payload) {
    const response = await fetch(url, {
        method,
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken') || '',
        },
        body: payload === undefined ? undefined : JSON.stringify(payload),
    });
    if (response.status === 204) return null;
    const data = await response.json().catch(() => null);
    if (!response.ok) throw new Error(apiErrorMessage(data, response.status));
    return data;
}
