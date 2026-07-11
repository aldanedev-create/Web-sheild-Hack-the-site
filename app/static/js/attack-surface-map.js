/**
 * WebShield Scanner - Attack Surface Map JavaScript
 * Handles attack surface visualization and data display.
 */

(function() {
    'use strict';

    const EMPTY_SURFACE = {
        target_url: '',
        total_pages: 0,
        endpoints: [],
        forms: [],
        login_pages: [],
        api_endpoints: [],
        admin_pages: [],
        technologies: [],
        file_types: {},
        directories: []
    };

    /**
     * Load attack surface data.
     */
    window.loadAttackSurface = function(scanId) {
        const normalizedScanId = Number(scanId);
        if (!Number.isInteger(normalizedScanId) || normalizedScanId <= 0) {
            showNoData('Invalid scan id');
            return;
        }

        if (!window.api || !window.api.isAuthenticated()) {
            window.location.href = '/login';
            return;
        }

        setText('surface-url', 'Loading...');

        window.api.report.get(normalizedScanId)
        .then(data => {
            if (!data.success || !data.report || !data.report.scan) {
                WebShield.showToast(data.message || 'Failed to load attack surface data.', 'danger');
                showNoData();
                return;
            }

            const scan = data.report.scan;
            const surfaceData = normalizeSurfaceData(scan.attack_surface_data, scan.target_url);

            if (!hasSurfaceData(surfaceData)) {
                showNoData('No attack surface data available for this scan');
                return;
            }

            renderAttackSurface(surfaceData);
            renderNetwork(surfaceData);
        })
        .catch(error => {
            console.error('Error loading attack surface:', error);
            WebShield.showToast(error.message || 'An error occurred. Please try again.', 'danger');
            showNoData();
        });
    };

    function normalizeSurfaceData(data, targetUrl) {
        const source = data && typeof data === 'object' ? data : {};
        return {
            ...EMPTY_SURFACE,
            ...source,
            target_url: source.target_url || targetUrl || '',
            total_pages: Number(source.total_pages || 0),
            endpoints: asArray(source.endpoints),
            forms: asArray(source.forms),
            login_pages: asArray(source.login_pages),
            api_endpoints: asArray(source.api_endpoints),
            admin_pages: asArray(source.admin_pages),
            technologies: asArray(source.technologies),
            file_types: source.file_types && typeof source.file_types === 'object' ? source.file_types : {},
            directories: asArray(source.directories)
        };
    }

    function hasSurfaceData(data) {
        return Boolean(
            data.total_pages ||
            data.endpoints.length ||
            data.forms.length ||
            data.login_pages.length ||
            data.api_endpoints.length ||
            data.admin_pages.length ||
            data.technologies.length ||
            Object.keys(data.file_types).length ||
            data.directories.length
        );
    }

    function renderNetwork(surfaceData) {
        const canvas = document.getElementById('surface-map-canvas');
        if (!canvas) return;

        if (typeof window.destroyNetworkMap === 'function') {
            window.destroyNetworkMap();
        }

        if (typeof window.initNetworkMap !== 'function') {
            canvas.innerHTML = '<div class="no-data">Network map renderer is unavailable</div>';
            return;
        }

        window.initNetworkMap('surface-map-canvas', surfaceData);
    }

    /**
     * Render attack surface data.
     */
    function renderAttackSurface(data) {
        setText('surface-url', data.target_url || 'Unknown target');
        setText('stat-pages', data.total_pages || 0);
        setText('stat-endpoints', data.endpoints.length);
        setText('stat-forms', data.forms.length);
        setText('stat-login', data.login_pages.length);
        setText('stat-api', data.api_endpoints.length);
        setText('stat-admin', data.admin_pages.length);

        renderTechnologies(data.technologies);
        renderFileTypes(data.file_types);
        renderList('directories-list', data.directories, 'No directories detected');
        renderList('login-list', data.login_pages, 'No login pages detected');
        renderList('api-list', data.api_endpoints, 'No API endpoints detected');
        renderList('admin-list', data.admin_pages, 'No admin pages detected');
    }

    function renderTechnologies(technologies) {
        const container = document.getElementById('tech-list');
        if (!container) return;

        if (!technologies.length) {
            container.innerHTML = '<div class="no-data">No technologies detected</div>';
            return;
        }

        container.innerHTML = technologies
            .slice(0, 60)
            .map(tech => `<span class="tech-tag">${escapeHtml(tech)}</span>`)
            .join('');
    }

    function renderFileTypes(fileTypes) {
        const container = document.getElementById('file-types-list');
        if (!container) return;

        const entries = Object.entries(fileTypes)
            .filter(([ext]) => ext)
            .sort((a, b) => Number(b[1] || 0) - Number(a[1] || 0));

        if (!entries.length) {
            container.innerHTML = '<div class="no-data">No files detected</div>';
            return;
        }

        container.innerHTML = entries.slice(0, 50).map(([ext, count]) => `
            <div class="item">
                <span>.<strong>${escapeHtml(ext)}</strong></span>
                <span class="badge-count">${Number(count || 0)}</span>
            </div>
        `).join('');
    }

    function renderList(containerId, items, emptyMessage) {
        const container = document.getElementById(containerId);
        if (!container) return;

        if (!items.length) {
            container.innerHTML = `<div class="no-data">${escapeHtml(emptyMessage || 'None detected')}</div>`;
            return;
        }

        const displayItems = items.slice(0, 50);
        const hasMore = items.length > 50;

        container.innerHTML = displayItems.map(item => {
            const text = typeof item === 'string' ? item : JSON.stringify(item);
            return `<div class="item">${safeUrlOrText(text)}</div>`;
        }).join('');

        if (hasMore) {
            container.innerHTML += `<div class="item" style="color:var(--text-dim);font-style:italic;">+ ${items.length - 50} more...</div>`;
        }
    }

    function showNoData(message) {
        setText('surface-url', message || 'No attack surface data available');
        ['tech-list', 'file-types-list', 'directories-list', 'login-list', 'api-list', 'admin-list'].forEach(id => {
            const el = document.getElementById(id);
            if (el) el.innerHTML = '<div class="no-data">No data available</div>';
        });

        ['stat-pages', 'stat-endpoints', 'stat-forms', 'stat-login', 'stat-api', 'stat-admin'].forEach(id => {
            setText(id, '0');
        });

        const canvas = document.getElementById('surface-map-canvas');
        if (canvas) {
            canvas.innerHTML = `<div class="no-data">${escapeHtml(message || 'No map data available')}</div>`;
        }
    }

    function asArray(value) {
        return Array.isArray(value) ? value.filter(item => item !== null && item !== undefined) : [];
    }

    function setText(id, value) {
        const element = document.getElementById(id);
        if (element) element.textContent = String(value);
    }

    function safeUrlOrText(value) {
        const text = String(value || '');
        if (!/^https?:\/\//i.test(text)) {
            return escapeHtml(text);
        }

        try {
            const parsed = new URL(text);
            if (parsed.protocol === 'http:' || parsed.protocol === 'https:') {
                return `<a href="${escapeAttribute(parsed.href)}" target="_blank" rel="noopener noreferrer">${escapeHtml(text)}</a>`;
            }
        } catch (err) {
            // Fall through to plain text.
        }
        return escapeHtml(text);
    }

    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text === null || text === undefined ? '' : String(text);
        return div.innerHTML;
    }

    function escapeAttribute(text) {
        return escapeHtml(text).replace(/"/g, '&quot;');
    }
})();
