<!-- Settings.svelte -->
<script lang="ts">
	import { getContext, onMount } from 'svelte';
	import type { Writable } from 'svelte/store';
	import { user } from '$lib/stores';
	import { TUTOR_API_BASE_URL } from '$lib/constants';
	import { toast } from 'svelte-sonner';

	const i18n = getContext<Writable<any>>('i18n');

	// ── Profile state ────────────────────────────────────────────────
	let name = '';
	let email = '';
	let bio = '';
	let avatarUrl = '';
	let saving = false;

	// ── Preferences ──────────────────────────────────────────────────
	let language = 'fr';
	let theme = 'light';
	let fontSize = 'medium';

	// ── Notifications ────────────────────────────────────────────────
	let notifAssignments = true;
	let notifGrades = true;
	let notifAnnouncements = true;
	let notifChat = false;

	// ── Section tabs ─────────────────────────────────────────────────
	type Section = 'profile' | 'preferences' | 'notifications' | 'privacy';
	let activeSection: Section = 'profile';

	onMount(() => {
		if ($user) {
			name  = $user.name  || '';
			email = $user.email || '';
		}
		// Load saved preferences
		const saved = localStorage.getItem('studentPrefs');
		if (saved) {
			const p = JSON.parse(saved);
			language          = p.language          ?? 'fr';
			theme             = p.theme             ?? 'light';
			fontSize          = p.fontSize          ?? 'medium';
			notifAssignments  = p.notifAssignments  ?? true;
			notifGrades       = p.notifGrades       ?? true;
			notifAnnouncements = p.notifAnnouncements ?? true;
			notifChat         = p.notifChat         ?? false;
			bio               = p.bio               ?? '';
		}
	});

	async function saveProfile() {
		saving = true;
		try {
			// Save preferences locally (profile API update if available)
			localStorage.setItem('studentPrefs', JSON.stringify({
				language, theme, fontSize,
				notifAssignments, notifGrades, notifAnnouncements, notifChat,
				bio
			}));
			toast.success('Paramètres sauvegardés !');
		} catch (e) {
			toast.error('Erreur lors de la sauvegarde');
		} finally {
			saving = false;
		}
	}

	const sections: { id: Section; label: string; icon: string }[] = [
		{ id: 'profile',       label: 'Profil',         icon: '👤' },
		{ id: 'preferences',   label: 'Préférences',    icon: '🎨' },
		{ id: 'notifications', label: 'Notifications',  icon: '🔔' },
		{ id: 'privacy',       label: 'Confidentialité',icon: '🔒' },
	];
</script>

<div class="settings-root">
	<!-- Header -->
	<div class="settings-header">
		<div class="settings-header-icon">⚙️</div>
		<div>
			<h1 class="settings-title">Paramètres</h1>
			<p class="settings-subtitle">Gérez votre profil et vos préférences</p>
		</div>
	</div>

	<div class="settings-layout">
		<!-- Sidebar nav -->
		<nav class="settings-nav">
			{#each sections as s}
				<button
					class="nav-item {activeSection === s.id ? 'active' : ''}"
					on:click={() => (activeSection = s.id)}
				>
					<span class="nav-icon">{s.icon}</span>
					<span>{s.label}</span>
				</button>
			{/each}
		</nav>

		<!-- Content -->
		<div class="settings-content">

			<!-- ── PROFILE ─────────────────────────────────────────── -->
			{#if activeSection === 'profile'}
				<section class="settings-section">
					<h2 class="section-title">Informations du profil</h2>

					<!-- Avatar -->
					<div class="avatar-block">
						<div class="avatar-circle">
							{#if avatarUrl}
								<img src={avatarUrl} alt="avatar" class="avatar-img" />
							{:else}
								<span class="avatar-letter">{name ? name[0].toUpperCase() : '?'}</span>
							{/if}
						</div>
						<div>
							<p class="avatar-name">{name || 'Étudiant'}</p>
							<p class="avatar-email">{email}</p>
							<span class="badge-role">🎓 Étudiant</span>
						</div>
					</div>

					<div class="form-grid">
						<div class="form-group">
							<label class="form-label">Nom complet</label>
							<input class="form-input" type="text" bind:value={name} placeholder="Votre nom" />
						</div>
						<div class="form-group">
							<label class="form-label">Email</label>
							<input class="form-input" type="email" bind:value={email} placeholder="votre@email.com" disabled />
							<span class="form-hint">L'email ne peut pas être modifié</span>
						</div>
						<div class="form-group full-width">
							<label class="form-label">Biographie</label>
							<textarea
								class="form-textarea"
								bind:value={bio}
								placeholder="Parlez de vous en quelques mots..."
								rows="3"
							></textarea>
						</div>
					</div>

					<button class="btn-save" on:click={saveProfile} disabled={saving}>
						{#if saving}
							<span class="spinner"></span> Sauvegarde...
						{:else}
							💾 Sauvegarder les modifications
						{/if}
					</button>
				</section>
			{/if}

			<!-- ── PREFERENCES ─────────────────────────────────────── -->
			{#if activeSection === 'preferences'}
				<section class="settings-section">
					<h2 class="section-title">Préférences d'affichage</h2>

					<div class="pref-cards">
						<!-- Theme -->
						<div class="pref-card">
							<div class="pref-card-icon">🌙</div>
							<div class="pref-info">
								<label class="pref-label">Thème</label>
								<p class="pref-desc">Choisissez l'apparence de l'interface</p>
							</div>
							<select class="form-select" bind:value={theme}>
								<option value="light">☀️ Clair</option>
								<option value="dark">🌙 Sombre</option>
								<option value="system">🖥️ Système</option>
							</select>
						</div>

						<!-- Language -->
						<div class="pref-card">
							<div class="pref-card-icon">🌍</div>
							<div class="pref-info">
								<label class="pref-label">Langue</label>
								<p class="pref-desc">Langue de l'interface</p>
							</div>
							<select class="form-select" bind:value={language}>
								<option value="fr">🇫🇷 Français</option>
								<option value="en">🇬🇧 English</option>
								<option value="ar">🇲🇦 العربية</option>
							</select>
						</div>

						<!-- Font size -->
						<div class="pref-card">
							<div class="pref-card-icon">🔡</div>
							<div class="pref-info">
								<label class="pref-label">Taille du texte</label>
								<p class="pref-desc">Ajustez la taille de la police</p>
							</div>
							<select class="form-select" bind:value={fontSize}>
								<option value="small">Petit</option>
								<option value="medium">Normal</option>
								<option value="large">Grand</option>
							</select>
						</div>
					</div>

					<button class="btn-save" on:click={saveProfile} disabled={saving}>
						💾 Sauvegarder les préférences
					</button>
				</section>
			{/if}

			<!-- ── NOTIFICATIONS ───────────────────────────────────── -->
			{#if activeSection === 'notifications'}
				<section class="settings-section">
					<h2 class="section-title">Préférences de notifications</h2>

					<div class="notif-list">
						<div class="notif-item">
							<div class="notif-left">
								<span class="notif-icon">📝</span>
								<div>
									<p class="notif-title">Nouveaux devoirs</p>
									<p class="notif-desc">Soyez alerté quand un enseignant publie un nouveau devoir</p>
								</div>
							</div>
							<label class="toggle">
								<input type="checkbox" bind:checked={notifAssignments} />
								<span class="toggle-slider"></span>
							</label>
						</div>

						<div class="notif-item">
							<div class="notif-left">
								<span class="notif-icon">⭐</span>
								<div>
									<p class="notif-title">Notes et résultats</p>
									<p class="notif-desc">Notification quand votre devoir est corrigé et noté</p>
								</div>
							</div>
							<label class="toggle">
								<input type="checkbox" bind:checked={notifGrades} />
								<span class="toggle-slider"></span>
							</label>
						</div>

						<div class="notif-item">
							<div class="notif-left">
								<span class="notif-icon">📢</span>
								<div>
									<p class="notif-title">Annonces</p>
									<p class="notif-desc">Messages et annonces de vos enseignants</p>
								</div>
							</div>
							<label class="toggle">
								<input type="checkbox" bind:checked={notifAnnouncements} />
								<span class="toggle-slider"></span>
							</label>
						</div>

						<div class="notif-item">
							<div class="notif-left">
								<span class="notif-icon">💬</span>
								<div>
									<p class="notif-title">Chat IA</p>
									<p class="notif-desc">Réponses de l'assistant pédagogique</p>
								</div>
							</div>
							<label class="toggle">
								<input type="checkbox" bind:checked={notifChat} />
								<span class="toggle-slider"></span>
							</label>
						</div>
					</div>

					<button class="btn-save" on:click={saveProfile} disabled={saving}>
						💾 Sauvegarder les notifications
					</button>
				</section>
			{/if}

			<!-- ── PRIVACY ─────────────────────────────────────────── -->
			{#if activeSection === 'privacy'}
				<section class="settings-section">
					<h2 class="section-title">Confidentialité & Sécurité</h2>

					<div class="privacy-cards">
						<div class="privacy-card info">
							<div class="privacy-card-icon">🔐</div>
							<div>
								<h3>Mot de passe</h3>
								<p>La modification du mot de passe se fait via la page de connexion OpenWebUI.</p>
								<a href="http://localhost:8080/auth" target="_blank" rel="noopener" class="privacy-link">
									Modifier le mot de passe →
								</a>
							</div>
						</div>

						<div class="privacy-card info">
							<div class="privacy-card-icon">📊</div>
							<div>
								<h3>Données d'apprentissage</h3>
								<p>Vos conversations avec l'IA sont utilisées pour améliorer votre expérience pédagogique. Elles ne sont pas partagées avec d'autres étudiants.</p>
							</div>
						</div>

						<div class="privacy-card warning">
							<div class="privacy-card-icon">⚠️</div>
							<div>
								<h3>Session active</h3>
								<p>Vous êtes connecté(e) depuis cet appareil. Pour se déconnecter de toutes les sessions, contactez votre enseignant.</p>
							</div>
						</div>

						<div class="privacy-stats">
							<h3 class="privacy-stats-title">Votre activité</h3>
							<div class="stats-grid">
								<div class="stat-box">
									<div class="stat-value">🔒</div>
									<div class="stat-label">Données chiffrées</div>
								</div>
								<div class="stat-box">
									<div class="stat-value">🛡️</div>
									<div class="stat-label">Accès sécurisé</div>
								</div>
								<div class="stat-box">
									<div class="stat-value">🏫</div>
									<div class="stat-label">Usage académique</div>
								</div>
							</div>
						</div>
					</div>
				</section>
			{/if}

		</div>
	</div>
</div>

<style>
	.settings-root {
		max-width: 900px;
		margin: 0 auto;
		padding: 2rem 1rem;
		font-family: 'Inter', system-ui, sans-serif;
	}

	/* Header */
	.settings-header {
		display: flex;
		align-items: center;
		gap: 1rem;
		margin-bottom: 2rem;
		padding: 1.5rem;
		background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
		border-radius: 16px;
		color: white;
	}
	.settings-header-icon { font-size: 2.5rem; }
	.settings-title { font-size: 1.6rem; font-weight: 700; margin: 0; }
	.settings-subtitle { margin: 0; opacity: 0.85; font-size: 0.9rem; }

	/* Layout */
	.settings-layout {
		display: grid;
		grid-template-columns: 200px 1fr;
		gap: 1.5rem;
	}
	@media (max-width: 640px) {
		.settings-layout { grid-template-columns: 1fr; }
	}

	/* Nav */
	.settings-nav {
		display: flex;
		flex-direction: column;
		gap: 0.4rem;
		background: var(--bg-card, #fff);
		border-radius: 14px;
		padding: 0.75rem;
		border: 1px solid var(--border, #e5e7eb);
		height: fit-content;
		box-shadow: 0 2px 8px rgba(0,0,0,0.04);
	}
	.nav-item {
		display: flex;
		align-items: center;
		gap: 0.6rem;
		padding: 0.6rem 0.9rem;
		border-radius: 10px;
		font-size: 0.88rem;
		font-weight: 500;
		cursor: pointer;
		background: none;
		border: none;
		color: var(--text-secondary, #6b7280);
		transition: all 0.2s;
		text-align: left;
		width: 100%;
	}
	.nav-item:hover { background: #f3f4f6; color: #374151; }
	.nav-item.active {
		background: linear-gradient(135deg, #667eea22, #764ba222);
		color: #667eea;
		font-weight: 600;
	}
	.nav-icon { font-size: 1.1rem; }

	/* Content */
	.settings-content {
		background: var(--bg-card, #fff);
		border-radius: 14px;
		border: 1px solid var(--border, #e5e7eb);
		box-shadow: 0 2px 8px rgba(0,0,0,0.04);
		overflow: hidden;
	}
	.settings-section { padding: 1.75rem; }
	.section-title {
		font-size: 1.15rem;
		font-weight: 700;
		color: var(--text-primary, #111827);
		margin: 0 0 1.5rem;
		padding-bottom: 0.75rem;
		border-bottom: 2px solid #f3f4f6;
	}

	/* Avatar */
	.avatar-block {
		display: flex;
		align-items: center;
		gap: 1.2rem;
		margin-bottom: 1.75rem;
		padding: 1rem;
		background: #f9fafb;
		border-radius: 12px;
	}
	.avatar-circle {
		width: 64px; height: 64px;
		border-radius: 50%;
		background: linear-gradient(135deg, #667eea, #764ba2);
		display: flex; align-items: center; justify-content: center;
		flex-shrink: 0;
	}
	.avatar-img { width: 100%; height: 100%; border-radius: 50%; object-fit: cover; }
	.avatar-letter { color: white; font-size: 1.5rem; font-weight: 700; }
	.avatar-name { font-weight: 600; font-size: 1rem; margin: 0 0 0.2rem; }
	.avatar-email { color: #6b7280; font-size: 0.85rem; margin: 0 0 0.4rem; }
	.badge-role {
		background: #ede9fe; color: #7c3aed;
		font-size: 0.75rem; padding: 0.2rem 0.6rem;
		border-radius: 20px; font-weight: 600;
	}

	/* Form */
	.form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-bottom: 1.5rem; }
	.full-width { grid-column: 1 / -1; }
	.form-group { display: flex; flex-direction: column; gap: 0.4rem; }
	.form-label { font-size: 0.85rem; font-weight: 600; color: #374151; }
	.form-input, .form-select, .form-textarea {
		padding: 0.6rem 0.9rem;
		border: 1.5px solid #e5e7eb;
		border-radius: 10px;
		font-size: 0.9rem;
		color: #111827;
		background: #fff;
		transition: border-color 0.2s;
		outline: none;
	}
	.form-input:focus, .form-select:focus, .form-textarea:focus { border-color: #667eea; }
	.form-input:disabled { background: #f9fafb; color: #9ca3af; cursor: not-allowed; }
	.form-textarea { resize: vertical; font-family: inherit; }
	.form-hint { font-size: 0.76rem; color: #9ca3af; }

	/* Preferences */
	.pref-cards { display: flex; flex-direction: column; gap: 0.8rem; margin-bottom: 1.5rem; }
	.pref-card {
		display: flex; align-items: center; gap: 1rem;
		padding: 1rem 1.2rem;
		background: #f9fafb; border-radius: 12px;
		border: 1px solid #f3f4f6;
	}
	.pref-card-icon { font-size: 1.5rem; }
	.pref-info { flex: 1; }
	.pref-label { font-weight: 600; font-size: 0.9rem; display: block; margin-bottom: 0.2rem; }
	.pref-desc { font-size: 0.8rem; color: #6b7280; margin: 0; }

	/* Notifications */
	.notif-list { display: flex; flex-direction: column; gap: 0; margin-bottom: 1.5rem; }
	.notif-item {
		display: flex; align-items: center; justify-content: space-between;
		padding: 1rem 0; border-bottom: 1px solid #f3f4f6;
	}
	.notif-item:last-child { border-bottom: none; }
	.notif-left { display: flex; align-items: center; gap: 1rem; }
	.notif-icon { font-size: 1.4rem; }
	.notif-title { font-weight: 600; font-size: 0.9rem; margin: 0 0 0.2rem; }
	.notif-desc { font-size: 0.8rem; color: #6b7280; margin: 0; }

	/* Toggle switch */
	.toggle { position: relative; display: inline-block; width: 48px; height: 26px; flex-shrink: 0; }
	.toggle input { opacity: 0; width: 0; height: 0; }
	.toggle-slider {
		position: absolute; inset: 0;
		background: #d1d5db; border-radius: 26px;
		cursor: pointer; transition: 0.3s;
	}
	.toggle-slider::before {
		content: ''; position: absolute;
		width: 20px; height: 20px; left: 3px; bottom: 3px;
		background: white; border-radius: 50%; transition: 0.3s;
	}
	.toggle input:checked + .toggle-slider { background: #667eea; }
	.toggle input:checked + .toggle-slider::before { transform: translateX(22px); }

	/* Privacy */
	.privacy-cards { display: flex; flex-direction: column; gap: 1rem; }
	.privacy-card {
		display: flex; gap: 1rem; padding: 1.2rem;
		border-radius: 12px; border: 1.5px solid;
	}
	.privacy-card.info { border-color: #bfdbfe; background: #eff6ff; }
	.privacy-card.warning { border-color: #fde68a; background: #fffbeb; }
	.privacy-card-icon { font-size: 1.5rem; flex-shrink: 0; margin-top: 2px; }
	.privacy-card h3 { font-size: 0.95rem; font-weight: 600; margin: 0 0 0.4rem; }
	.privacy-card p { font-size: 0.85rem; color: #374151; margin: 0; line-height: 1.5; }
	.privacy-link {
		display: inline-block; margin-top: 0.5rem;
		font-size: 0.85rem; color: #2563eb; font-weight: 600;
		text-decoration: none;
	}
	.privacy-link:hover { text-decoration: underline; }
	.privacy-stats {
		padding: 1.2rem; background: #f9fafb;
		border-radius: 12px; border: 1px solid #f3f4f6;
	}
	.privacy-stats-title { font-weight: 700; font-size: 0.95rem; margin: 0 0 1rem; }
	.stats-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 0.8rem; }
	.stat-box {
		text-align: center; padding: 0.8rem;
		background: white; border-radius: 10px;
		border: 1px solid #e5e7eb;
	}
	.stat-value { font-size: 1.5rem; margin-bottom: 0.3rem; }
	.stat-label { font-size: 0.75rem; color: #6b7280; font-weight: 500; }

	/* Save button */
	.btn-save {
		display: inline-flex; align-items: center; gap: 0.5rem;
		padding: 0.7rem 1.5rem;
		background: linear-gradient(135deg, #667eea, #764ba2);
		color: white; border: none; border-radius: 10px;
		font-size: 0.9rem; font-weight: 600; cursor: pointer;
		transition: opacity 0.2s, transform 0.1s;
	}
	.btn-save:hover:not(:disabled) { opacity: 0.92; transform: translateY(-1px); }
	.btn-save:disabled { opacity: 0.6; cursor: not-allowed; }
	.spinner {
		width: 14px; height: 14px;
		border: 2px solid rgba(255,255,255,0.4);
		border-top-color: white;
		border-radius: 50%;
		animation: spin 0.7s linear infinite;
		display: inline-block;
	}
	@keyframes spin { to { transform: rotate(360deg); } }
</style>
