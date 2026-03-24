# ============================================================
#  messages.py — All bot messages in 4 languages
#  Edit the text here to update what the bot says
# ============================================================

from config import CLAIM_DEADLINE, BRAND_NAME

# Channel labels used in invite instructions
CHANNEL_NAMES = {
    "en": "English",
    "it": "Italian",
    "fr": "French",
    "mx": "Spanish",
}

MESSAGES = {
    "en": {
        "language_set": (
            "✅ Language set to *English*!\n\n"
            "Now send the word *invite* to get your unique invite link! 🔗"
        ),
        "invite_instruction": (
            "Hello {{first_name}} 👋\n"
            f"Thank you for participating in the *{BRAND_NAME}* Invite Challenge 🎉\n\n"
            "🔗 Your unique invite link:\n{{link}}\n\n"
            "Invite as many people as you can and earn bigger rewards 🚀\n\n"
            "🏆 *Reward Tiers:*\n"
            "• 1 to 5 invites → 🎰 15 Free Spins\n"
            "• 6 to 10 invites → 🎰 30 Free Spins\n"
            "• 11 to 30 invites → 🎰 80 Free Spins\n"
            "• 31 to 70 invites → 🎰 120 Free Spins\n"
            "• 71 to 100 invites → 🎰 170 Free Spins\n"
            "• 100+ invites → 🎰 250 Free Spins\n\n"
            "Start inviting now and climb the rewards ladder 🔥\n\n"
            "📊 Check your progress: /status\n"
            "🎁 Claim your reward: /claim\n"
            "❓ Need help: /help"
        ),
        "already_has_link": (
            "Hello {{first_name}} 👋 You already have an invite link! 🔗\n\n"
            "Your link: {{link}}\n\n"
            "📊 Check your progress: /status\n"
            "🎁 Claim your reward: /claim"
        ),
        "inactivity_warning": (
            "⚠️ *Important* ❗\n\n"
            "Hello {{first_name}}, if you do not invite anyone, "
            "your invite link will be removed in 24 hours.\n\n"
            "Start sharing your link now to keep it active! 🔗 {{link}}"
        ),
        "link_removed": (
            "❌ Your invite link has been removed due to inactivity.\n\n"
            "Send *invite* again to get a new link and start fresh!"
        ),
        "status": (
            "📊 *Your Invite Stats*\n\n"
            "👥 Total invites: *{{count}}*\n"
            "🏆 Current tier: *{{promo}}*\n\n"
            "Keep sharing to unlock better rewards!\n"
            f"⏰ Claim deadline: {CLAIM_DEADLINE}"
        ),
        "status_no_link": "You don't have an invite link yet. Send *invite* to get one!",
        "claim_eligible": (
            "🎁 Congratulations {{first_name}}! You've unlocked *{{promo}}*!\n\n"
            "Your promo code: `{{code}}`\n\n"
            f"⏰ Valid until: {CLAIM_DEADLINE}\n\n"
            "Enjoy your reward! 🎊"
        ),
        "claim_not_eligible": (
            "❌ You haven't reached a reward tier yet.\n\n"
            "Keep inviting friends and come back when you hit 1+ invites!\n\n"
            "📊 Check your progress: /status"
        ),
        "claim_already": "✅ You already claimed your reward: `{{code}}`",
        "threshold_reached": (
            "🎉 *{{first_name}}, you've unlocked {{promo}}!*\n\n"
            "Use /claim to receive your reward before *{{deadline}}*!"
        ),
        "no_link_yet": "You don't have an invite link yet. Send the word *invite* to get one!",
        "select_language_first": "👋 Please select your language first using /start",
        "help": (
            "❓ *Help*\n\n"
            "• Send *invite* → get your unique invite link\n"
            "• /status → check how many people joined\n"
            "• /claim → claim your reward\n"
            "• /start → change language\n\n"
            f"🏆 Invite challenge ends: *{CLAIM_DEADLINE}*"
        ),
    },

    "it": {
        "language_set": (
            "✅ Lingua impostata su *Italiano*!\n\n"
            "Ora invia la parola *invite* per ottenere il tuo link di invito unico! 🔗"
        ),
        "invite_instruction": (
            "Ciao {{first_name}} 👋\n"
            f"Grazie per partecipare alla *{BRAND_NAME}* Invite Challenge 🎉\n\n"
            "🔗 Il tuo link di invito unico:\n{{link}}\n\n"
            "Invita più persone possibile e guadagna premi sempre più grandi 🚀\n\n"
            "🏆 *Livelli premio:*\n"
            "• Da 1 a 5 inviti → 🎰 15 Free Spin\n"
            "• Da 6 a 10 inviti → 🎰 30 Free Spin\n"
            "• Da 11 a 30 inviti → 🎰 80 Free Spin\n"
            "• Da 31 a 70 inviti → 🎰 120 Free Spin\n"
            "• Da 71 a 100 inviti → 🎰 170 Free Spin\n"
            "• 100+ inviti → 🎰 250 Free Spin\n\n"
            "Inizia ora a invitare e scala la classifica dei premi 🔥\n\n"
            "📊 Controlla i progressi: /status\n"
            "🎁 Riscatta il premio: /claim\n"
            "❓ Aiuto: /help"
        ),
        "already_has_link": (
            "Ciao {{first_name}} 👋 Hai già un link di invito! 🔗\n\n"
            "Il tuo link: {{link}}\n\n"
            "📊 Controlla i progressi: /status\n"
            "🎁 Riscatta il premio: /claim"
        ),
        "inactivity_warning": (
            "⚠️ *Importante* ❗\n\n"
            "Ciao {{first_name}}, se non inviti nessuno, "
            "il tuo link di invito verrà rimosso tra 24 ore.\n\n"
            "Inizia a condividere il tuo link ora per mantenerlo attivo! 🔗 {{link}}"
        ),
        "link_removed": (
            "❌ Il tuo link di invito è stato rimosso per inattività.\n\n"
            "Invia di nuovo *invite* per ottenere un nuovo link e ricominciare!"
        ),
        "status": (
            "📊 *Le Tue Statistiche*\n\n"
            "👥 Inviti totali: *{{count}}*\n"
            "🏆 Livello attuale: *{{promo}}*\n\n"
            "Continua a condividere per sbloccare premi migliori!\n"
            f"⏰ Scadenza: {CLAIM_DEADLINE}"
        ),
        "status_no_link": "Non hai ancora un link di invito. Invia *invite* per ottenerne uno!",
        "claim_eligible": (
            "🎁 Complimenti {{first_name}}! Hai sbloccato *{{promo}}*!\n\n"
            "Il tuo codice promo: `{{code}}`\n\n"
            f"⏰ Valido fino a: {CLAIM_DEADLINE}\n\n"
            "Goditi il tuo premio! 🎊"
        ),
        "claim_not_eligible": (
            "❌ Non hai ancora raggiunto nessun livello.\n\n"
            "Continua a invitare amici e torna quando hai almeno 1 invito!\n\n"
            "📊 Controlla i progressi: /status"
        ),
        "claim_already": "✅ Hai già riscattato il tuo premio: `{{code}}`",
        "threshold_reached": (
            "🎉 *{{first_name}}, hai sbloccato {{promo}}!*\n\n"
            "Usa /claim per ricevere il tuo premio entro *{{deadline}}*!"
        ),
        "no_link_yet": "Non hai ancora un link di invito. Invia la parola *invite* per ottenerne uno!",
        "select_language_first": "👋 Seleziona prima la tua lingua con /start",
        "help": (
            "❓ *Aiuto*\n\n"
            "• Invia *invite* → ottieni il tuo link di invito unico\n"
            "• /status → controlla quante persone si sono unite\n"
            "• /claim → riscatta il tuo premio\n"
            "• /start → cambia lingua\n\n"
            f"🏆 La sfida termina: *{CLAIM_DEADLINE}*"
        ),
    },

    "fr": {
        "language_set": (
            "✅ Langue définie sur *Français*!\n\n"
            "Envoyez maintenant le mot *invite* pour obtenir votre lien d'invitation unique! 🔗"
        ),
        "invite_instruction": (
            "Bonjour {{first_name}} 👋\n"
            f"Merci de participer au *{BRAND_NAME}* Invite Challenge 🎉\n\n"
            "🔗 Votre lien d'invitation unique:\n{{link}}\n\n"
            "Invitez le plus de personnes possible et gagnez de plus grandes récompenses 🚀\n\n"
            "🏆 *Niveaux de récompense:*\n"
            "• 1 à 5 invitations → 🎰 15 Tours Gratuits\n"
            "• 6 à 10 invitations → 🎰 30 Tours Gratuits\n"
            "• 11 à 30 invitations → 🎰 80 Tours Gratuits\n"
            "• 31 à 70 invitations → 🎰 120 Tours Gratuits\n"
            "• 71 à 100 invitations → 🎰 170 Tours Gratuits\n"
            "• 100+ invitations → 🎰 250 Tours Gratuits\n\n"
            "Commencez à inviter maintenant et grimpez l'échelle des récompenses 🔥\n\n"
            "📊 Vérifiez vos progrès: /status\n"
            "🎁 Réclamez votre récompense: /claim\n"
            "❓ Aide: /help"
        ),
        "already_has_link": (
            "Bonjour {{first_name}} 👋 Vous avez déjà un lien d'invitation! 🔗\n\n"
            "Votre lien: {{link}}\n\n"
            "📊 Vérifiez vos progrès: /status\n"
            "🎁 Réclamez votre récompense: /claim"
        ),
        "inactivity_warning": (
            "⚠️ *Important* ❗\n\n"
            "Bonjour {{first_name}}, si vous n'invitez personne, "
            "votre lien d'invitation sera supprimé dans 24 heures.\n\n"
            "Commencez à partager votre lien maintenant pour le garder actif! 🔗 {{link}}"
        ),
        "link_removed": (
            "❌ Votre lien d'invitation a été supprimé en raison d'inactivité.\n\n"
            "Envoyez à nouveau *invite* pour obtenir un nouveau lien et recommencer!"
        ),
        "status": (
            "📊 *Vos Statistiques*\n\n"
            "👥 Total d'invitations: *{{count}}*\n"
            "🏆 Niveau actuel: *{{promo}}*\n\n"
            "Continuez à partager pour débloquer de meilleures récompenses!\n"
            f"⏰ Date limite: {CLAIM_DEADLINE}"
        ),
        "status_no_link": "Vous n'avez pas encore de lien d'invitation. Envoyez *invite* pour en obtenir un!",
        "claim_eligible": (
            "🎁 Félicitations {{first_name}}! Vous avez débloqué *{{promo}}*!\n\n"
            "Votre code promo: `{{code}}`\n\n"
            f"⏰ Valable jusqu'au: {CLAIM_DEADLINE}\n\n"
            "Profitez de votre récompense! 🎊"
        ),
        "claim_not_eligible": (
            "❌ Vous n'avez pas encore atteint de niveau.\n\n"
            "Continuez à inviter des amis et revenez quand vous avez au moins 1 invitation!\n\n"
            "📊 Vérifiez vos progrès: /status"
        ),
        "claim_already": "✅ Vous avez déjà réclamé votre récompense: `{{code}}`",
        "threshold_reached": (
            "🎉 *{{first_name}}, vous avez débloqué {{promo}}!*\n\n"
            "Utilisez /claim pour recevoir votre récompense avant le *{{deadline}}*!"
        ),
        "no_link_yet": "Vous n'avez pas encore de lien d'invitation. Envoyez le mot *invite* pour en obtenir un!",
        "select_language_first": "👋 Veuillez d'abord sélectionner votre langue avec /start",
        "help": (
            "❓ *Aide*\n\n"
            "• Envoyez *invite* → obtenez votre lien d'invitation unique\n"
            "• /status → vérifiez combien de personnes ont rejoint\n"
            "• /claim → réclamez votre récompense\n"
            "• /start → changer de langue\n\n"
            f"🏆 Le défi se termine: *{CLAIM_DEADLINE}*"
        ),
    },

    "mx": {
        "language_set": (
            "✅ ¡Idioma configurado a *Español*!\n\n"
            "¡Ahora envía la palabra *invite* para obtener tu enlace de invitación único! 🔗"
        ),
        "invite_instruction": (
            "¡Hola {{first_name}} 👋\n"
            f"Gracias por participar en el *{BRAND_NAME}* Invite Challenge 🎉\n\n"
            "🔗 Tu enlace de invitación único:\n{{link}}\n\n"
            "¡Invita a la mayor cantidad de personas posible y gana mayores recompensas 🚀\n\n"
            "🏆 *Niveles de recompensa:*\n"
            "• 1 a 5 invitaciones → 🎰 15 Giros Gratis\n"
            "• 6 a 10 invitaciones → 🎰 30 Giros Gratis\n"
            "• 11 a 30 invitaciones → 🎰 80 Giros Gratis\n"
            "• 31 a 70 invitaciones → 🎰 120 Giros Gratis\n"
            "• 71 a 100 invitaciones → 🎰 170 Giros Gratis\n"
            "• 100+ invitaciones → 🎰 250 Giros Gratis\n\n"
            "¡Empieza a invitar ahora y sube la escalera de recompensas 🔥\n\n"
            "📊 Revisa tu progreso: /status\n"
            "🎁 Reclama tu recompensa: /claim\n"
            "❓ Ayuda: /help"
        ),
        "already_has_link": (
            "¡Hola {{first_name}} 👋 Ya tienes un enlace de invitación! 🔗\n\n"
            "Tu enlace: {{link}}\n\n"
            "📊 Revisa tu progreso: /status\n"
            "🎁 Reclama tu recompensa: /claim"
        ),
        "inactivity_warning": (
            "⚠️ *Importante* ❗\n\n"
            "Hola {{first_name}}, si no invitas a nadie, "
            "tu enlace de invitación será eliminado en 24 horas.\n\n"
            "¡Empieza a compartir tu enlace ahora para mantenerlo activo! 🔗 {{link}}"
        ),
        "link_removed": (
            "❌ Tu enlace de invitación ha sido eliminado por inactividad.\n\n"
            "¡Envía *invite* de nuevo para obtener un nuevo enlace y empezar de cero!"
        ),
        "status": (
            "📊 *Tus Estadísticas*\n\n"
            "👥 Total de invitaciones: *{{count}}*\n"
            "🏆 Nivel actual: *{{promo}}*\n\n"
            "¡Sigue compartiendo para desbloquear mejores recompensas!\n"
            f"⏰ Fecha límite: {CLAIM_DEADLINE}"
        ),
        "status_no_link": "Todavía no tienes un enlace de invitación. ¡Envía *invite* para obtener uno!",
        "claim_eligible": (
            "🎁 ¡Felicidades {{first_name}}! ¡Desbloqueaste *{{promo}}*!\n\n"
            "Tu código promo: `{{code}}`\n\n"
            f"⏰ Válido hasta: {CLAIM_DEADLINE}\n\n"
            "¡Disfruta tu recompensa! 🎊"
        ),
        "claim_not_eligible": (
            "❌ Todavía no has alcanzado ningún nivel.\n\n"
            "¡Sigue invitando amigos y vuelve cuando tengas al menos 1 invitación!\n\n"
            "📊 Revisa tu progreso: /status"
        ),
        "claim_already": "✅ Ya reclamaste tu recompensa: `{{code}}`",
        "threshold_reached": (
            "🎉 *¡{{first_name}}, desbloqueaste {{promo}}!*\n\n"
            "¡Usa /claim para recibir tu recompensa antes del *{{deadline}}*!"
        ),
        "no_link_yet": "Todavía no tienes un enlace de invitación. ¡Envía la palabra *invite* para obtener uno!",
        "select_language_first": "👋 Por favor selecciona tu idioma primero con /start",
        "help": (
            "❓ *Ayuda*\n\n"
            "• Envía *invite* → obtén tu enlace de invitación único\n"
            "• /status → revisa cuántas personas se unieron\n"
            "• /claim → reclama tu recompensa\n"
            "• /start → cambiar idioma\n\n"
            f"🏆 El desafío termina: *{CLAIM_DEADLINE}*"
        ),
    },
}
