# ============================================================
#  messages.py — All bot messages in 4 languages (HTML format)
#  Uses HTML tags: <b>bold</b>  <code>monospace</code>
# ============================================================

from config import CLAIM_DEADLINE, BRAND_NAME

MESSAGES = {
    "en": {
        "language_set": (
            "✅ Language set to <b>English</b>!\n\n"
            "Now send the word <b>invite</b> to get your unique invite link! 🔗"
        ),
        "campaign_ended": (
            f"🏁 <b>The {BRAND_NAME} Invite Challenge has ended.</b>\n\n"
            "Thank you to everyone who participated! 🙏\n\n"
            "Stay tuned for our next campaign — big things are coming! 🚀"
        ),
        "campaign_full": (
            "⏳ <b>The invite spots are full!</b>\n\n"
            f"The {BRAND_NAME} Invite Challenge has reached its maximum number of participants.\n\n"
            "Stay tuned for our next campaign! 🚀"
        ),
        "invite_instruction": (
            "Hello {first_name} 👋\n"
            f"Thank you for participating in the <b>{BRAND_NAME}</b> Invite Challenge 🎉\n\n"
            "🔗 Your unique invite link:\n{link}\n\n"
            "Invite as many people as you can and earn bigger rewards 🚀\n\n"
            "🏆 <b>Reward Tiers:</b>\n"
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
            "Hello {first_name} 👋 You already have an invite link! 🔗\n\n"
            "Your link: {link}\n\n"
            "📊 Check your progress: /status\n"
            "🎁 Claim your reward: /claim"
        ),
        "alt_account_blocked": (
            "⚠️ <b>We could not verify your account.</b>\n\n"
            "To participate in the Invite Challenge, your Telegram account must have a profile photo.\n\n"
            "Please add a profile photo and try again by sending <b>invite</b>."
        ),
        "new_account_blocked": (
            "⚠️ <b>New account detected.</b>\n\n"
            "The user <b>@{username}</b> you invited has a Telegram account that is less than "
            "<b>{hours} hours</b> old and cannot be counted as a valid invite.\n\n"
            "Only invites from established accounts are accepted to prevent fraud. "
            "Keep sharing your link with real users! 🔗"
        ),
        "inactivity_warning": (
            "⚠️ <b>Important</b> ❗\n\n"
            "Hello {first_name}, if you do not invite anyone, "
            "your invite link will be removed in 24 hours.\n\n"
            "Start sharing your link now to keep it active!\n🔗 {link}"
        ),
        "link_removed": (
            "❌ Your invite link has been removed due to inactivity.\n\n"
            "Send <b>invite</b> again to get a new link and start fresh!"
        ),
        "status": (
            "📊 <b>Your Invite Stats</b>\n\n"
            "👥 Total invites: <b>{count}</b>\n"
            "🏆 Current tier: <b>{promo}</b>\n\n"
            "Keep sharing to unlock better rewards!\n"
            f"⏰ Claim deadline: {CLAIM_DEADLINE}"
        ),
        "status_no_link": "You don't have an invite link yet. Send <b>invite</b> to get one!",
        "claim_eligible": (
            "🎁 Congratulations {first_name}! You've unlocked <b>{promo}</b>!\n\n"
            "Your promo code: <code>{code}</code>\n\n"
            f"⏰ Valid until: {CLAIM_DEADLINE}\n\n"
            "Enjoy your reward! 🎊"
        ),
        "claim_not_eligible": (
            "❌ You haven't reached a reward tier yet.\n\n"
            "Keep inviting friends and come back when you hit 1+ invites!\n\n"
            "📊 Check your progress: /status"
        ),
        "claim_already": "✅ You already claimed your reward: <code>{code}</code>",
        "threshold_reached": (
            "🎉 <b>You've unlocked {promo}!</b>\n\n"
            "Use /claim to receive your reward before <b>{deadline}</b>!"
        ),
        "help": (
            "❓ <b>Help</b>\n\n"
            "• Send <b>invite</b> → get your unique invite link\n"
            "• /status → check how many people joined\n"
            "• /claim → claim your reward\n"
            "• /start → change language\n\n"
            f"🏆 Invite challenge ends: <b>{CLAIM_DEADLINE}</b>"
        ),
    },

    "it": {
        "language_set": (
            "✅ Lingua impostata su <b>Italiano</b>!\n\n"
            "Ora invia la parola <b>invite</b> per ottenere il tuo link di invito unico! 🔗"
        ),
        "campaign_ended": (
            f"🏁 <b>La {BRAND_NAME} Invite Challenge è terminata.</b>\n\n"
            "Grazie a tutti i partecipanti! 🙏\n\n"
            "Resta aggiornato per la prossima campagna — grandi cose in arrivo! 🚀"
        ),
        "campaign_full": (
            "⏳ <b>I posti disponibili sono esauriti!</b>\n\n"
            f"La {BRAND_NAME} Invite Challenge ha raggiunto il numero massimo di partecipanti.\n\n"
            "Resta aggiornato per la prossima campagna! 🚀"
        ),
        "invite_instruction": (
            "Ciao {first_name} 👋\n"
            f"Grazie per partecipare alla <b>{BRAND_NAME}</b> Invite Challenge 🎉\n\n"
            "🔗 Il tuo link di invito unico:\n{link}\n\n"
            "Invita più persone possibile e guadagna premi sempre più grandi 🚀\n\n"
            "🏆 <b>Livelli premio:</b>\n"
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
            "Ciao {first_name} 👋 Hai già un link di invito! 🔗\n\n"
            "Il tuo link: {link}\n\n"
            "📊 Controlla i progressi: /status\n"
            "🎁 Riscatta il premio: /claim"
        ),
        "alt_account_blocked": (
            "⚠️ <b>Non è stato possibile verificare il tuo account.</b>\n\n"
            "Per partecipare alla Invite Challenge, il tuo account Telegram deve avere una foto profilo.\n\n"
            "Aggiungi una foto profilo e riprova inviando <b>invite</b>."
        ),
        "new_account_blocked": (
            "⚠️ <b>Account nuovo rilevato.</b>\n\n"
            "L'utente <b>@{username}</b> che hai invitato ha un account Telegram di meno di "
            "<b>{hours} ore</b> e non può essere contato come invito valido.\n\n"
            "Sono accettati solo inviti da account consolidati per prevenire le frodi. "
            "Continua a condividere il tuo link con utenti reali! 🔗"
        ),
        "inactivity_warning": (
            "⚠️ <b>Importante</b> ❗\n\n"
            "Ciao {first_name}, se non inviti nessuno, "
            "il tuo link di invito verrà rimosso tra 24 ore.\n\n"
            "Inizia a condividere il tuo link ora per mantenerlo attivo!\n🔗 {link}"
        ),
        "link_removed": (
            "❌ Il tuo link di invito è stato rimosso per inattività.\n\n"
            "Invia di nuovo <b>invite</b> per ottenere un nuovo link e ricominciare!"
        ),
        "status": (
            "📊 <b>Le Tue Statistiche</b>\n\n"
            "👥 Inviti totali: <b>{count}</b>\n"
            "🏆 Livello attuale: <b>{promo}</b>\n\n"
            "Continua a condividere per sbloccare premi migliori!\n"
            f"⏰ Scadenza: {CLAIM_DEADLINE}"
        ),
        "status_no_link": "Non hai ancora un link di invito. Invia <b>invite</b> per ottenerne uno!",
        "claim_eligible": (
            "🎁 Complimenti {first_name}! Hai sbloccato <b>{promo}</b>!\n\n"
            "Il tuo codice promo: <code>{code}</code>\n\n"
            f"⏰ Valido fino a: {CLAIM_DEADLINE}\n\n"
            "Goditi il tuo premio! 🎊"
        ),
        "claim_not_eligible": (
            "❌ Non hai ancora raggiunto nessun livello.\n\n"
            "Continua a invitare amici e torna quando hai almeno 1 invito!\n\n"
            "📊 Controlla i progressi: /status"
        ),
        "claim_already": "✅ Hai già riscattato il tuo premio: <code>{code}</code>",
        "threshold_reached": (
            "🎉 <b>Hai sbloccato {promo}!</b>\n\n"
            "Usa /claim per ricevere il tuo premio entro <b>{deadline}</b>!"
        ),
        "help": (
            "❓ <b>Aiuto</b>\n\n"
            "• Invia <b>invite</b> → ottieni il tuo link di invito unico\n"
            "• /status → controlla quante persone si sono unite\n"
            "• /claim → riscatta il tuo premio\n"
            "• /start → cambia lingua\n\n"
            f"🏆 La sfida termina: <b>{CLAIM_DEADLINE}</b>"
        ),
    },

    "fr": {
        "language_set": (
            "✅ Langue définie sur <b>Français</b>!\n\n"
            "Envoyez maintenant le mot <b>invite</b> pour obtenir votre lien d'invitation unique! 🔗"
        ),
        "campaign_ended": (
            f"🏁 <b>Le {BRAND_NAME} Invite Challenge est terminé.</b>\n\n"
            "Merci à tous les participants! 🙏\n\n"
            "Restez à l'écoute pour notre prochaine campagne — de grandes choses arrivent! 🚀"
        ),
        "campaign_full": (
            "⏳ <b>Les places sont complètes!</b>\n\n"
            f"Le {BRAND_NAME} Invite Challenge a atteint son nombre maximum de participants.\n\n"
            "Restez à l'écoute pour notre prochaine campagne! 🚀"
        ),
        "invite_instruction": (
            "Bonjour {first_name} 👋\n"
            f"Merci de participer au <b>{BRAND_NAME}</b> Invite Challenge 🎉\n\n"
            "🔗 Votre lien d'invitation unique:\n{link}\n\n"
            "Invitez le plus de personnes possible et gagnez de plus grandes récompenses 🚀\n\n"
            "🏆 <b>Niveaux de récompense:</b>\n"
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
            "Bonjour {first_name} 👋 Vous avez déjà un lien d'invitation! 🔗\n\n"
            "Votre lien: {link}\n\n"
            "📊 Vérifiez vos progrès: /status\n"
            "🎁 Réclamez votre récompense: /claim"
        ),
        "alt_account_blocked": (
            "⚠️ <b>Nous n'avons pas pu vérifier votre compte.</b>\n\n"
            "Pour participer au Invite Challenge, votre compte Telegram doit avoir une photo de profil.\n\n"
            "Veuillez ajouter une photo de profil et réessayer en envoyant <b>invite</b>."
        ),
        "new_account_blocked": (
            "⚠️ <b>Nouveau compte détecté.</b>\n\n"
            "L'utilisateur <b>@{username}</b> que vous avez invité a un compte Telegram de moins de "
            "<b>{hours} heures</b> et ne peut pas être compté comme une invitation valide.\n\n"
            "Seules les invitations de comptes établis sont acceptées pour prévenir la fraude. "
            "Continuez à partager votre lien avec de vrais utilisateurs! 🔗"
        ),
        "inactivity_warning": (
            "⚠️ <b>Important</b> ❗\n\n"
            "Bonjour {first_name}, si vous n'invitez personne, "
            "votre lien d'invitation sera supprimé dans 24 heures.\n\n"
            "Commencez à partager votre lien maintenant pour le garder actif!\n🔗 {link}"
        ),
        "link_removed": (
            "❌ Votre lien d'invitation a été supprimé en raison d'inactivité.\n\n"
            "Envoyez à nouveau <b>invite</b> pour obtenir un nouveau lien et recommencer!"
        ),
        "status": (
            "📊 <b>Vos Statistiques</b>\n\n"
            "👥 Total d'invitations: <b>{count}</b>\n"
            "🏆 Niveau actuel: <b>{promo}</b>\n\n"
            "Continuez à partager pour débloquer de meilleures récompenses!\n"
            f"⏰ Date limite: {CLAIM_DEADLINE}"
        ),
        "status_no_link": "Vous n'avez pas encore de lien d'invitation. Envoyez <b>invite</b> pour en obtenir un!",
        "claim_eligible": (
            "🎁 Félicitations {first_name}! Vous avez débloqué <b>{promo}</b>!\n\n"
            "Votre code promo: <code>{code}</code>\n\n"
            f"⏰ Valable jusqu'au: {CLAIM_DEADLINE}\n\n"
            "Profitez de votre récompense! 🎊"
        ),
        "claim_not_eligible": (
            "❌ Vous n'avez pas encore atteint de niveau.\n\n"
            "Continuez à inviter des amis et revenez quand vous avez au moins 1 invitation!\n\n"
            "📊 Vérifiez vos progrès: /status"
        ),
        "claim_already": "✅ Vous avez déjà réclamé votre récompense: <code>{code}</code>",
        "threshold_reached": (
            "🎉 <b>Vous avez débloqué {promo}!</b>\n\n"
            "Utilisez /claim pour recevoir votre récompense avant le <b>{deadline}</b>!"
        ),
        "help": (
            "❓ <b>Aide</b>\n\n"
            "• Envoyez <b>invite</b> → obtenez votre lien d'invitation unique\n"
            "• /status → vérifiez combien de personnes ont rejoint\n"
            "• /claim → réclamez votre récompense\n"
            "• /start → changer de langue\n\n"
            f"🏆 Le défi se termine: <b>{CLAIM_DEADLINE}</b>"
        ),
    },

    "mx": {
        "language_set": (
            "✅ Idioma configurado a <b>Español</b>!\n\n"
            "Ahora envía la palabra <b>invite</b> para obtener tu enlace de invitación único! 🔗"
        ),
        "campaign_ended": (
            f"🏁 <b>El {BRAND_NAME} Invite Challenge ha terminado.</b>\n\n"
            "Gracias a todos los participantes! 🙏\n\n"
            "Mantente atento para nuestra próxima campaña — grandes cosas están por venir! 🚀"
        ),
        "campaign_full": (
            "⏳ <b>Los cupos están llenos!</b>\n\n"
            f"El {BRAND_NAME} Invite Challenge ha alcanzado el número máximo de participantes.\n\n"
            "Mantente atento para nuestra próxima campaña! 🚀"
        ),
        "invite_instruction": (
            "Hola {first_name} 👋\n"
            f"Gracias por participar en el <b>{BRAND_NAME}</b> Invite Challenge 🎉\n\n"
            "🔗 Tu enlace de invitación único:\n{link}\n\n"
            "Invita a la mayor cantidad de personas posible y gana mayores recompensas 🚀\n\n"
            "🏆 <b>Niveles de recompensa:</b>\n"
            "• 1 a 5 invitaciones → 🎰 15 Giros Gratis\n"
            "• 6 a 10 invitaciones → 🎰 30 Giros Gratis\n"
            "• 11 a 30 invitaciones → 🎰 80 Giros Gratis\n"
            "• 31 a 70 invitaciones → 🎰 120 Giros Gratis\n"
            "• 71 a 100 invitaciones → 🎰 170 Giros Gratis\n"
            "• 100+ invitaciones → 🎰 250 Giros Gratis\n\n"
            "Empieza a invitar ahora y sube la escalera de recompensas 🔥\n\n"
            "📊 Revisa tu progreso: /status\n"
            "🎁 Reclama tu recompensa: /claim\n"
            "❓ Ayuda: /help"
        ),
        "already_has_link": (
            "Hola {first_name} 👋 Ya tienes un enlace de invitación! 🔗\n\n"
            "Tu enlace: {link}\n\n"
            "📊 Revisa tu progreso: /status\n"
            "🎁 Reclama tu recompensa: /claim"
        ),
        "alt_account_blocked": (
            "⚠️ <b>No pudimos verificar tu cuenta.</b>\n\n"
            "Para participar en el Invite Challenge, tu cuenta de Telegram debe tener una foto de perfil.\n\n"
            "Por favor agrega una foto de perfil e intenta de nuevo enviando <b>invite</b>."
        ),
        "new_account_blocked": (
            "⚠️ <b>Cuenta nueva detectada.</b>\n\n"
            "El usuario <b>@{username}</b> que invitaste tiene una cuenta de Telegram de menos de "
            "<b>{hours} horas</b> y no puede contarse como una invitación válida.\n\n"
            "Solo se aceptan invitaciones de cuentas establecidas para prevenir el fraude. "
            "Sigue compartiendo tu enlace con usuarios reales! 🔗"
        ),
        "inactivity_warning": (
            "⚠️ <b>Importante</b> ❗\n\n"
            "Hola {first_name}, si no invitas a nadie, "
            "tu enlace de invitación será eliminado en 24 horas.\n\n"
            "Empieza a compartir tu enlace ahora para mantenerlo activo!\n🔗 {link}"
        ),
        "link_removed": (
            "❌ Tu enlace de invitación ha sido eliminado por inactividad.\n\n"
            "Envía <b>invite</b> de nuevo para obtener un nuevo enlace y empezar de cero!"
        ),
        "status": (
            "📊 <b>Tus Estadísticas</b>\n\n"
            "👥 Total de invitaciones: <b>{count}</b>\n"
            "🏆 Nivel actual: <b>{promo}</b>\n\n"
            "Sigue compartiendo para desbloquear mejores recompensas!\n"
            f"⏰ Fecha límite: {CLAIM_DEADLINE}"
        ),
        "status_no_link": "Todavía no tienes un enlace de invitación. Envía <b>invite</b> para obtener uno!",
        "claim_eligible": (
            "🎁 Felicidades {first_name}! Desbloqueaste <b>{promo}</b>!\n\n"
            "Tu código promo: <code>{code}</code>\n\n"
            f"⏰ Válido hasta: {CLAIM_DEADLINE}\n\n"
            "Disfruta tu recompensa! 🎊"
        ),
        "claim_not_eligible": (
            "❌ Todavía no has alcanzado ningún nivel.\n\n"
            "Sigue invitando amigos y vuelve cuando tengas al menos 1 invitación!\n\n"
            "📊 Revisa tu progreso: /status"
        ),
        "claim_already": "✅ Ya reclamaste tu recompensa: <code>{code}</code>",
        "threshold_reached": (
            "🎉 <b>Desbloqueaste {promo}!</b>\n\n"
            "Usa /claim para recibir tu recompensa antes del <b>{deadline}</b>!"
        ),
        "help": (
            "❓ <b>Ayuda</b>\n\n"
            "• Envía <b>invite</b> → obtén tu enlace de invitación único\n"
            "• /status → revisa cuántas personas se unieron\n"
            "• /claim → reclama tu recompensa\n"
            "• /start → cambiar idioma\n\n"
            f"🏆 El desafío termina: <b>{CLAIM_DEADLINE}</b>"
        ),
    },
}
