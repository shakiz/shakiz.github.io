// Small progressive enhancements for the portfolio pages. Everything works without JS:
// filter chips start hidden and all items are shown until this script runs, and on
// phones the plain nav links stay visible unless the <html class="js"> flag is set.

// Mobile menu (< 800px): full-screen overlay with a focus trap.
(function () {
	var menu = document.getElementById('site-menu');
	var toggle = document.querySelector('.site-header .menu-toggle');
	if (!menu || !toggle) return;
	var closeButton = menu.querySelector('[data-menu-close]');

	function focusable() {
		return menu.querySelectorAll('a[href], button:not([disabled])');
	}

	function open() {
		menu.hidden = false;
		toggle.setAttribute('aria-expanded', 'true');
		document.body.classList.add('menu-open');
		closeButton.focus();
	}

	function close(restoreFocus) {
		if (menu.hidden) return;
		menu.hidden = true;
		toggle.setAttribute('aria-expanded', 'false');
		document.body.classList.remove('menu-open');
		if (restoreFocus) toggle.focus();
	}

	toggle.addEventListener('click', open);
	closeButton.addEventListener('click', function () { close(true); });

	// Any link closes the menu, including same-page ones like /#career.
	menu.querySelectorAll('a[href]').forEach(function (link) {
		link.addEventListener('click', function () { close(false); });
	});

	menu.addEventListener('keydown', function (event) {
		if (event.key === 'Escape') {
			close(true);
			return;
		}
		if (event.key !== 'Tab') return;
		var items = focusable();
		var first = items[0];
		var last = items[items.length - 1];
		if (event.shiftKey && document.activeElement === first) {
			event.preventDefault();
			last.focus();
		} else if (!event.shiftKey && document.activeElement === last) {
			event.preventDefault();
			first.focus();
		}
	});

	// The overlay only exists below 800px; close it if the window grows past that.
	window.matchMedia('(min-width: 800px)').addEventListener('change', function (mq) {
		if (mq.matches) close(false);
	});
})();

// Filter chips.
// <div data-filter-for="ID" hidden> holds <button data-filter="key" aria-pressed>.
// Items inside #ID carry data-filter-tags="key other-key"; "all" shows everything.
document.querySelectorAll('[data-filter-for]').forEach(function (group) {
	var list = document.getElementById(group.getAttribute('data-filter-for'));
	if (!list) return;
	var buttons = group.querySelectorAll('[data-filter]');
	var items = list.querySelectorAll('[data-filter-tags]');

	function apply(key) {
		buttons.forEach(function (b) {
			b.setAttribute('aria-pressed', String(b.getAttribute('data-filter') === key));
		});
		items.forEach(function (item) {
			var tags = item.getAttribute('data-filter-tags').split(' ');
			item.hidden = key !== 'all' && tags.indexOf(key) === -1;
		});
	}

	buttons.forEach(function (b) {
		b.addEventListener('click', function () { apply(b.getAttribute('data-filter')); });
	});
	group.hidden = false;
});

// Contact form.
// With data-endpoint set (e.g. a Formspree URL) the form posts there and shows the sent panel.
// Without one it opens the visitor's email app with the message filled in, and says so
// honestly instead of claiming the message was sent.
(function () {
	var form = document.getElementById('contact-form');
	var panel = document.getElementById('contact-sent');
	if (!form || !panel) return;

	var endpoint = form.getAttribute('data-endpoint');
	var mailto = form.getAttribute('data-mailto');
	var status = form.querySelector('[data-form-status]');
	var submit = form.querySelector('[type="submit"]');
	var title = panel.querySelector('[data-sent-title]');
	var text = panel.querySelector('[data-sent-text]');
	var sentTitle = title.textContent;
	var sentText = text.textContent;

	function showSent(viaEmailApp) {
		if (viaEmailApp) {
			title.textContent = 'Almost there — check your email app.';
			text.textContent = 'Your message is ready to send there. I’ll reply within two working days.';
		} else {
			title.textContent = sentTitle;
			text.textContent = sentText;
		}
		form.hidden = true;
		panel.hidden = false;
		title.focus();
	}

	form.addEventListener('submit', function (event) {
		event.preventDefault();
		status.textContent = '';
		var data = new FormData(form);

		if (!endpoint) {
			var company = data.get('company');
			var subject = data.get('topic') + ' · ' + data.get('name');
			var body = data.get('message') + '\n\n' + data.get('name') +
				(company ? ' · ' + company : '') + '\n' + data.get('email');
			window.location.href = 'mailto:' + mailto +
				'?subject=' + encodeURIComponent(subject) + '&body=' + encodeURIComponent(body);
			showSent(true);
			return;
		}

		submit.disabled = true;
		submit.textContent = 'Sending…';
		fetch(endpoint, { method: 'POST', body: data, headers: { Accept: 'application/json' } })
			.then(function (response) {
				if (!response.ok) throw new Error('HTTP ' + response.status);
				form.reset();
				showSent(false);
			})
			.catch(function () {
				status.textContent = 'Sorry, that didn’t go through. Please email me at ' + mailto + ' instead.';
			})
			.then(function () {
				submit.disabled = false;
				submit.textContent = 'Send message';
			});
	});

	panel.querySelector('[data-send-another]').addEventListener('click', function () {
		panel.hidden = true;
		form.hidden = false;
		form.querySelector('input:not([type="radio"])').focus();
	});
})();
