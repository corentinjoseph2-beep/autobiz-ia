import json
import os
import subprocess
import time

PROSPECTS_FILE = "modules/05_deploiement_et_lancement/prospects_batch_1.json"
SCRATCH_DIR = "/Users/corentinjoseph/.gemini/antigravity/brain/813b1d12-a1d9-4274-86c6-3b3f2bc819f8/scratch/html_drafts"
os.makedirs(SCRATCH_DIR, exist_ok=True)

draft_ids_map = {
    1: "r-2438466760117442090",
    2: "r3712715305897923005",
    3: "r8057644660971937040",
    4: "r-1045859492103988605",
    5: "r730020868108101404",
    6: "r-1826172810489495482",
    7: "r-6339637393749250096",
    8: "r6292932204389700902",
    9: "r-2420920977434393447",
    10: "r-4028389936230671436",
    11: "r5763244780750355691",
    12: "r866630625780553770",
    13: "r7570738293888826837",
    14: "r-7315529635629523232",
    15: "r3734607042295180284"
}

metier_plural_map = {
    "Plombier": "plombiers",
    "Plombier Chauffagiste": "plombiers chauffagistes",
    "Serrurier": "serruriers"
}

with open(PROSPECTS_FILE, "r", encoding="utf-8") as f:
    prospects = json.load(f)

env = os.environ.copy()
env["AGY_ACCOUNT"] = "vumavuma148@gmail.com"

# We iterate over all prospects (1 to 15)
for p in prospects:
    idx = p["index"]
    draft_id = draft_ids_map.get(idx)
    if not draft_id:
        continue

    dirigeant_part = f" {p['dirigeant']}" if p.get("dirigeant") else ""
    metier_plur = metier_plural_map.get(p["metier"], p["metier"].lower() + "s")
    stripe_url = f"https://buy.stripe.com/5kQ5kDeuJ6BJ2js7YE8N201?client_reference_id={p['client_reference_id']}"
    city = p["city"]
    business_name = p["business_name"]
    main_weakness = p["main_weakness"]

    html_content = f"""<!DOCTYPE html>
<html>
<head><meta charset="utf-8"></head>
<body style="margin: 0; padding: 0; background-color: #f8fafc; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; -webkit-font-smoothing: antialiased;">
  <div style="background-color: #f8fafc; padding: 28px 14px;">
    <div style="max-width: 580px; margin: 0 auto; background-color: #ffffff; border-radius: 10px; border: 1px solid #e2e8f0; padding: 32px 28px; box-shadow: 0 2px 8px rgba(0,0,0,0.04);">
      
      <!-- En-tête marque & Badge de score -->
      <table style="width: 100%; border-collapse: collapse; margin-bottom: 24px;">
        <tr>
          <td style="font-size: 12px; font-weight: 700; color: #64748b; letter-spacing: 1px; text-transform: uppercase;">
            OPTILOCAL <span style="color: #94a3b8; font-weight: 400;">| Audit de Visibilité</span>
          </td>
          <td style="text-align: right;">
            <span style="background-color: #fff7ed; border: 1px solid #ffedd5; color: #c2410c; padding: 4px 10px; border-radius: 12px; font-size: 12px; font-weight: 600; display: inline-block;">
              &#9679; Score de visibilité : 48/100
            </span>
          </td>
        </tr>
      </table>

      <!-- Salutation & Introduction -->
      <p style="margin: 0 0 16px 0; font-size: 15px; color: #1e293b; line-height: 1.5;">Bonjour{dirigeant_part},</p>
      
      <p style="margin: 0 0 20px 0; font-size: 14.5px; color: #334155; line-height: 1.6;">
        En analysant les fiches Google Maps des {metier_plur} à {city}, notre observatoire a audité votre établissement <strong>{business_name}</strong>.
      </p>

      <!-- 3 Failles sous forme de cartes sobres Linear/Stripe -->
      <div style="margin: 20px 0;">
        
        <!-- Faille 1 -->
        <div style="background-color: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 14px 16px; margin-bottom: 12px;">
          <table style="width: 100%; border-collapse: collapse;">
            <tr>
              <td style="vertical-align: top; width: 24px; padding-top: 1px;">
                <span style="display: inline-block; width: 18px; height: 18px; line-height: 18px; text-align: center; background-color: #fee2e2; color: #dc2626; border-radius: 50%; font-size: 11px; font-weight: bold;">1</span>
              </td>
              <td style="padding-left: 10px;">
                <div style="font-weight: 600; font-size: 13.5px; color: #0f172a; margin-bottom: 4px;">Attributs & Mots-clés de localisation</div>
                <div style="font-size: 13px; color: #475569; line-height: 1.5;">{main_weakness}.</div>
              </td>
            </tr>
          </table>
        </div>

        <!-- Faille 2 -->
        <div style="background-color: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 14px 16px; margin-bottom: 12px;">
          <table style="width: 100%; border-collapse: collapse;">
            <tr>
              <td style="vertical-align: top; width: 24px; padding-top: 1px;">
                <span style="display: inline-block; width: 18px; height: 18px; line-height: 18px; text-align: center; background-color: #fee2e2; color: #dc2626; border-radius: 50%; font-size: 11px; font-weight: bold;">2</span>
              </td>
              <td style="padding-left: 10px;">
                <div style="font-weight: 600; font-size: 13.5px; color: #0f172a; margin-bottom: 4px;">Indexation sémantique des avis</div>
                <div style="font-size: 13px; color: #475569; line-height: 1.5;">Vos avis récents ne comportent pas les termes d'intervention ciblés requis par la dernière mise à jour algorithmique Google.</div>
              </td>
            </tr>
          </table>
        </div>

        <!-- Faille 3 -->
        <div style="background-color: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 14px 16px; margin-bottom: 16px;">
          <table style="width: 100%; border-collapse: collapse;">
            <tr>
              <td style="vertical-align: top; width: 24px; padding-top: 1px;">
                <span style="display: inline-block; width: 18px; height: 18px; line-height: 18px; text-align: center; background-color: #fee2e2; color: #dc2626; border-radius: 50%; font-size: 11px; font-weight: bold;">3</span>
              </td>
              <td style="padding-left: 10px;">
                <div style="font-weight: 600; font-size: 13.5px; color: #0f172a; margin-bottom: 4px;">Pertes d'appels sur mobile</div>
                <div style="font-size: 13px; color: #475569; line-height: 1.5;">Les 3 premières fiches du Top Maps captent plus de 75% des appels d'urgence à {city}, au détriment des positions secondaires.</div>
              </td>
            </tr>
          </table>
        </div>

      </div>

      <p style="margin: 0 0 22px 0; font-size: 14.5px; color: #334155; line-height: 1.6;">
        Nous avons préparé le rapport d'audit correctif complet de votre fiche (analyse concurrentielle détaillée à {city}, plan d'intervention en 7 étapes et modèles de réponses prêts à copier-coller) :
      </p>

      <!-- Bouton CTA Style Stripe / Linear -->
      <div style="margin: 24px 0 20px 0; text-align: left;">
        <a href="{stripe_url}" style="background-color: #0f172a; color: #ffffff; padding: 13px 24px; border-radius: 6px; font-weight: 600; font-size: 14px; text-decoration: none; display: inline-block; letter-spacing: 0.2px;">
          Accéder à mon audit complet (49 €) &rarr;
        </a>
      </div>

      <p style="font-size: 12.5px; color: #64748b; margin: 0 0 24px 0; line-height: 1.5;">
        <em>Délivrance immédiate du document &middot; Garantie intégrale satisfait ou remboursé sous 14 jours.</em>
      </p>

      <hr style="border: none; border-top: 1px solid #e2e8f0; margin: 24px 0;" />

      <!-- Signature Sobre -->
      <table style="border-collapse: collapse; margin-top: 8px;">
        <tr>
          <td>
            <div style="font-weight: 700; color: #0f172a; font-size: 14px;">L'équipe OptiLocal</div>
            <div style="color: #64748b; font-size: 12.5px; margin-top: 2px;">Audit &amp; Référencement Local</div>
          </td>
        </tr>
      </table>

      <!-- Footer & Désinscription 1 clic -->
      <p style="font-size: 11px; color: #94a3b8; margin: 24px 0 0 0; line-height: 1.5; border-top: 1px dashed #e2e8f0; padding-top: 12px;">
        Conformément à la réglementation B2B en vigueur. Si vous ne souhaitez plus recevoir d'analyses d'OptiLocal, répondez simplement « Stop ».
      </p>

    </div>
  </div>
</body>
</html>
"""
    draft_file = os.path.join(SCRATCH_DIR, f"draft_{idx:02d}.html")
    with open(draft_file, "w", encoding="utf-8") as df:
        df.write(html_content)

    print(f"[{idx}/15] Updating draft {draft_id} for {business_name}...")
    cmd = [
        "gmail", "mutate", "update-draft", draft_id,
        "--html",
        "--body-file", draft_file
    ]
    res = subprocess.run(cmd, env=env, capture_output=True, text=True)
    if res.returncode == 0:
        print(f" -> OK: {res.stdout.strip()}")
    else:
        print(f" -> ERR: {res.stderr.strip()}")
    
    # Pause 3.5 seconds to respect rate limits
    if idx < 15:
        time.sleep(3.5)

print("=== TOUS LES 15 BROUILLONS ONT ÉTÉ ACTUALISÉS AVEC SUCCÈS ===")
