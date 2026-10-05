# 🗺️ Mapeo y Control de Calidad de Subtítulos (Fase 2 - Edición Blindada)

**Proyecto:** DramiaStream (Catálogo DramaTube & Subtítulos en Español)  
**Fecha de Actualización:** Octubre 2026  
**Estándar de Calidad:** WebVTT Inteligente (Saltos automáticos a 52 caracteres), HLS/MP4 dinámico y cero duplicados.

---

## 🛡️ Lecciones Aprendidas y Protocolo de Prevención de Errores

Para garantizar que el proceso de extracción y traducción sea 100% limpio, rápido y no rompa la plataforma, se aplican las siguientes reglas obligatorias:

| # | Problema Detectado Anteriormente | Causa Raíz Identificada | Regla Preventiva Aplicada (V2) |
| :-: | :--- | :--- | :--- |
| **1** | **Tarjetas Duplicadas en el Inicio** | Las categorías de la barra de navegación del sitio de origen se asignaban a cada drama, clonando las filas. | Las categorías se filtran y desduplican estrictamente con `dict.fromkeys()` y la portada solo muestra carruseles de catálogos únicos. |
| **2** | **Videos con Error 502 (Bad Gateway)** | Servidores como `videotv.vividshort.com` entregan MP4 directos, pero el sistema intentaba forzarlos como HLS manifest. | Detección dinámica de stream (`is_hls` vs `is_mp4`): Si es `.m3u8` usa HLS.js; si es MP4 usa streaming directo HTTP 206. |
| **3** | **Pósters caídos o bloqueados** | CDNs como `chartdrama` y `toonshort` bloquean peticiones directas desde el navegador por falta de Referer. | Todo póster externo se enruta por `/proxy/img` con caché persistente en disco (`_segcache/`). |
| **4** | **Lentitud en la Cuadrícula** | Se insertaban cientos de elementos al DOM de golpe, saturando la red. | Paginación virtualizada / scroll infinito por bloques de 48 elementos (`GridClient.js`). |
| **5** | **Errores de URL relativa (`nd1/...`)** | NetShort devolvía URLs de subtítulos sin prefijo `https://`. | Auto-completado de esquema y dominio en `resolve_url()`. |
| **6** | **Títulos basura en catálogo** | Se guardaban dramas con streams caídos o tokens caducados. | **Filtro de validación en tiempo real:** Solo se guarda si el episodio 1 responde 200/206 y tiene póster válido. |

---

## 📊 Métricas Globales del Sistema

```mermaid
pie title Distribución del Catálogo Consolidado (2,046 Dramas)
    "DramaTube (Subtitulados y Verificados)" : 987
    "Dramas (Doblados / En Español)" : 979
    "DramaShorts (Narto)" : 45
    "HotDrama (ShortMax)" : 42
    "FreeReels" : 36
```

| Métrica | Cantidad Actual | Estado |
| :--- | :--- | :--- |
| **Dramas con Subtítulos en Español en Disco** | **1,072 títulos** | Carpetas generadas en `data/subtitles/` |
| **Episodios traducidos (`.vtt`)** | **6,344 archivos** | Con saltos de línea optimizados |
| **Dramas en DramaTube (`data/dramatube.json`)** | **987 títulos** | 100% verificados y reproducibles |
| **Catálogo Total Consolidado** | **2,046 títulos** | En `/api/catalog` |
| **Catálogo DramaVibe (Extendido)** | **40,706 títulos** | En `/seccion/dramavibe` |
| **Universo de Slugs en la Biblioteca Origen** | **7,742 slugs** | Disponibles en la fuente original |
| **Slugs Pendientes por Procesar** | **~6,540 títulos** | Listos para procesar en próximas tandas |

---

## 📑 Registro de Dramas Validados y Traducidos (Muestra Destacada)

| # | Título del Drama | Slug | Episodios | Subtítulos ES | Tipo Stream | Estado |
| :-: | :--- | :--- | :-: | :-: | :-: | :-: |
| **01** | Craving the Wrong Brother | `dt-craving-the-wrong-brother-2` | 54 / 54 | 54 eps | HLS | ✅ Verificado |
| **02** | Pregnant by the Wrong Twin | `dt-pregnant-by-the-wrong-twin` | 44 / 44 | 44 eps | HLS | ✅ Verificado |
| **03** | Shadow King and His Princess | `dt-shadow-king-and-his-princess` | 60 / 60 | 60 eps | HLS | ✅ Verificado |
| **04** | After Breakup, My System Made Me Rise | `dt-after-breakup-my-system-made-me-rise` | 40 / 40 | 40 eps | MP4 Nativo | ✅ Verificado |
| **05** | Claimed by My Ex's Alpha Father | `dt-claimed-by-my-exs-alpha-father-4` | 25 / 25 | 25 eps | MP4 Nativo | ✅ Verificado |
| **06** | Revenge Vow at the Wedding | `dv-27984-revenge-vow-at-the-wedding` | 20 / 20 | 20 eps | HLS | ✅ Verificado |
| **07** | A Contract With The Billionaire | `dt-a-contract-with-the-billionaire` | 100 / 100 | 100 eps | HLS | ✅ Verificado |
| **08** | Cutting Ties, Rising High | `dt-cutting-ties-rising-high` | 70 / 70 | 70 eps | HLS | ✅ Verificado |
| **09** | My Memories on National Trial: CEO Breaks Down | `dt-my-memories-on-national-trial-ceo-breaks-down` | 15 / 15 | 15 eps | HLS | ✅ Verificado |
| **10** | Five Years of Secret Love, He Married My Best Friend | `dt-five-years-of-secret-love-he-married-my-best-friend` | 27 / 27 | 27 eps | HLS | ✅ Verificado |
| **$100 Battle-Scarred Husband** | `dt-100-battle-scarred-husband` | 35 / 35 | 35 eps | HLS/MP4 | ✅ Verificado |
| **100%Compatibility** | `dt-100-compatibility` | 75 / 75 | 75 eps | HLS/MP4 | ✅ Verificado |
| **100 Pounds Later, He Regretted It** | `dt-100-pounds-later-he-regretted-it` | 87 / 87 | 87 eps | HLS/MP4 | ✅ Verificado |
| **100 Rules for Love** | `dt-100-rules-for-love` | 54 / 54 | 54 eps | HLS/MP4 | ✅ Verificado |
| **17 Heartbreaks: Silent Echoes of Love** | `dt-17-heartbreaks-silent-echoes-of-love` | 30 / 30 | 30 eps | HLS/MP4 | ✅ Verificado |
| **1Yesterday’s Snow: A Stand-In’s Revenge** | `dt-1yesterday-s-snow-a-stand-in-s-revenge` | 64 / 64 | 64 eps | HLS/MP4 | ✅ Verificado |
| **24-Hour Superpower** | `dt-24-hour-superpower` | 17 / 17 | 17 eps | HLS/MP4 | ✅ Verificado |
| **30.000Feet Letting Go of You** | `dt-30-000feet-letting-go-of-you-3` | 70 / 70 | 70 eps | HLS/MP4 | ✅ Verificado |
| **30.000Feet Letting Go of You** | `dt-30-000feet-letting-go-of-you-4` | 16 / 16 | 16 eps | HLS/MP4 | ✅ Verificado |
| **30.000Feet Letting Go of You** | `dt-30-000feet-letting-go-of-you-6` | 69 / 69 | 69 eps | HLS/MP4 | ✅ Verificado |
| **30.000Feet Letting Go of You** | `dt-30-000feet-letting-go-of-you-7` | 70 / 70 | 70 eps | HLS/MP4 | ✅ Verificado |
| **30 Years Frozen, Emergency Rescue** | `dt-30-years-frozen-emergency-rescue` | 44 / 44 | 44 eps | HLS/MP4 | ✅ Verificado |
| **30 Years Frozen,3 Brothers Regret** | `dt-30-years-frozen3-brothers-regret` | 18 / 18 | 18 eps | HLS/MP4 | ✅ Verificado |
| **300 pound Saintess** | `dt-300-pound-saintess` | 13 / 13 | 13 eps | HLS/MP4 | ✅ Verificado |
| **360,000 hard-earned dollars** | `dt-360-000-hard-earned-dollars` | 30 / 30 | 30 eps | HLS/MP4 | ✅ Verificado |
| **Who's Laughing Now?** | `dt-365-day-s-revenge` | 74 / 74 | 74 eps | HLS/MP4 | ✅ Verificado |
| **62 Times the Alpha Rejected Me** | `dt-62-times-the-alpha-rejected-me` | 12 / 12 | 12 eps | HLS/MP4 | ✅ Verificado |
| **7000 dollars destroyed 30 years friendship** | `dt-7000-dollars-destroyed-30-years-friendship-2` | 31 / 31 | 31 eps | HLS/MP4 | ✅ Verificado |
| **72 Hours of Passionate Kisses** | `dt-72-hours-of-passionate-kisses-2` | 90 / 90 | 90 eps | HLS/MP4 | ✅ Verificado |
| **72 Hours of Passionate Kisses** | `dt-72-hours-of-passionate-kisses-3` | 90 / 90 | 90 eps | HLS/MP4 | ✅ Verificado |
| **(Dubbed)A Baby, a Billionaire, And Me** | `dt-a-baby-a-billionaire-and-me` | 36 / 36 | 36 eps | HLS/MP4 | ✅ Verificado |
| **A Baby's Adventure and A Wife's Awakening** | `dt-a-babys-adventure-and-a-wifes-awakening` | 53 / 53 | 53 eps | HLS/MP4 | ✅ Verificado |
| **A belated apology She has long severed all affection and renounced love.** | `dt-a-belated-apology-she-has-long-severed-all-affection-and-renounced-love-3` | 15 / 15 | 15 eps | HLS/MP4 | ✅ Verificado |
| **A Billionaire Father’s Wrath** | `dt-a-billionaire-fathers-wrath-4` | 60 / 60 | 60 eps | HLS/MP4 | ✅ Verificado |
| **A Billionaire's Double Life** | `dt-a-billionaires-double-life-2` | 50 / 50 | 50 eps | HLS/MP4 | ✅ Verificado |
| **A Billionaire’s Revenge For His Loyal Dog** | `dt-a-billionaires-revenge-for-his-loyal-dog` | 51 / 51 | 51 eps | HLS/MP4 | ✅ Verificado |
| **(Dubbed)A Broken Blade Still Kills** | `dt-a-broken-blade-still-kills` | 62 / 62 | 62 eps | HLS/MP4 | ✅ Verificado |
| **A Chilling Reunion** | `dt-a-chilling-reunion` | 34 / 34 | 34 eps | HLS/MP4 | ✅ Verificado |
| **A Cinderella for Wolf King** | `dt-a-cinderella-for-wolf-king` | 17 / 17 | 17 eps | HLS/MP4 | ✅ Verificado |
| **A Crown of Thorns** | `dt-a-crown-of-thorns` | 75 / 75 | 75 eps | HLS/MP4 | ✅ Verificado |
| **A Decade as a Replacement, I End It Here** | `dt-a-decade-as-a-replacement-i-end-it-here-2` | 21 / 21 | 21 eps | HLS/MP4 | ✅ Verificado |
| **A Desperate Housewife's Revenge** | `dt-a-desperate-housewifes-revenge-5` | 27 / 27 | 27 eps | HLS/MP4 | ✅ Verificado |
| **A Destiny Rewritten** | `dt-a-destiny-rewritten` | 30 / 30 | 30 eps | HLS/MP4 | ✅ Verificado |
| **A Divorced Mom and Her Fabulous Six** | `dt-a-divorced-mom-and-her-fabulous-six` | 99 / 99 | 99 eps | HLS/MP4 | ✅ Verificado |
| **A Divorced Mom and Her Fabulous Six (Dubbed)** | `dt-a-divorced-mom-and-her-fabulous-six-2` | 97 / 97 | 97 eps | HLS/MP4 | ✅ Verificado |
| **A Fake Marriage Made In Heaven** | `dt-a-fake-marriage-made-in-heaven` | 89 / 89 | 89 eps | HLS/MP4 | ✅ Verificado |
| **A Father’s Cure** | `dt-a-fathers-cure` | 86 / 86 | 86 eps | HLS/MP4 | ✅ Verificado |
| **A Father’s Fury** | `dt-a-fathers-fury-3` | 14 / 14 | 14 eps | HLS/MP4 | ✅ Verificado |
| **A Father’s Fury** | `dt-a-fathers-fury-4` | 13 / 13 | 13 eps | HLS/MP4 | ✅ Verificado |
| **A Father’s Fury** | `dt-a-fathers-fury-5` | 7 / 7 | 7 eps | HLS/MP4 | ✅ Verificado |
| **A FATHER'S REDEMPTION** | `dt-a-fathers-redemption-3` | 70 / 70 | 70 eps | HLS/MP4 | ✅ Verificado |
| **A Fênix Retorna Heroicamente** | `dt-a-fenix-retorna-heroicamente` | 102 / 102 | 102 eps | HLS/MP4 | ✅ Verificado |
| **NetShort 1952907090033750018** | `dt-a-fiery-night-with-mr-ice` | 82 / 82 | 82 eps | HLS/MP4 | ✅ Verificado |
| **A Glimmer in the Cold World** | `dt-a-glimmer-in-the-cold-world` | 10 / 10 | 10 eps | HLS/MP4 | ✅ Verificado |
| **A Heroine's Return: Long Live the Dragonland** | `dt-a-heroines-return-long-live-the-dragonland` | 81 / 81 | 81 eps | HLS/MP4 | ✅ Verificado |
| **A Journey for Revenge** | `dt-a-journey-for-revenge` | 30 / 30 | 30 eps | HLS/MP4 | ✅ Verificado |
| **A Kindness Worth Millions** | `dt-a-kindness-worth-millions` | 50 / 50 | 50 eps | HLS/MP4 | ✅ Verificado |
| **A Kingdom's Price** | `dt-a-kingdom-s-price` | 65 / 65 | 65 eps | HLS/MP4 | ✅ Verificado |
| **A Kiss Worth Dying For** | `dt-a-kiss-worth-dying-for` | 65 / 65 | 65 eps | HLS/MP4 | ✅ Verificado |
| **A Lady’s Treachery** | `dt-a-lady-s-treachery` | 79 / 79 | 79 eps | HLS/MP4 | ✅ Verificado |
| **A Love Across Decades** | `dt-a-love-across-decades` | 59 / 59 | 59 eps | HLS/MP4 | ✅ Verificado |
| **A Love Across Time** | `dt-a-love-across-time` | 60 / 60 | 60 eps | HLS/MP4 | ✅ Verificado |
| **A Love Forged in War** | `dt-a-love-forged-in-war` | 28 / 28 | 28 eps | HLS/MP4 | ✅ Verificado |
| **A Love Not Mine (Dubbed)** | `dt-a-love-not-mine` | 36 / 36 | 36 eps | HLS/MP4 | ✅ Verificado |
| **A Love Prescription of Mr.Devil** | `dt-a-love-prescription-of-mr-devil-2` | 52 / 52 | 52 eps | HLS/MP4 | ✅ Verificado |
| **A Marriage of Luxury… and Lies** | `dt-a-marriage-of-luxury-and-lies` | 17 / 17 | 17 eps | HLS/MP4 | ✅ Verificado |
| **A Misplaced love A Fated Return (Dubbed)** | `dt-a-misplaced-love-a-fated-return` | 33 / 33 | 33 eps | HLS/MP4 | ✅ Verificado |
| **A Mistaken Marriage, Two Lifetimes** | `dt-a-mistaken-marriage-two-lifetimes` | 7 / 7 | 7 eps | HLS/MP4 | ✅ Verificado |
| **A Mother’s Mercy Ends Here** | `dt-a-mother-s-mercy-ends-here` | 50 / 50 | 50 eps | HLS/MP4 | ✅ Verificado |
| **A Mother's Revenge** | `dt-a-mother-s-revenge` | 62 / 62 | 62 eps | HLS/MP4 | ✅ Verificado |
| **A Mother‘s Reckoning** | `dt-a-mothers-reckoning-4` | 11 / 11 | 11 eps | HLS/MP4 | ✅ Verificado |
| **A MOTHER'S VENGEANCE:MAKING THE SCUMBAG PAY** | `dt-a-mothers-vengeance-making-the-scumbag-pay-3` | 30 / 30 | 30 eps | HLS/MP4 | ✅ Verificado |
| **A MOTHER'S VENGEANCE:MAKING THE SCUMBAG PAY** | `dt-a-mothers-vengeance-making-the-scumbag-pay-4` | 21 / 21 | 21 eps | HLS/MP4 | ✅ Verificado |
| **A MOTHER'S VENGEANCE:MAKING THE SCUMBAG PAY** | `dt-a-mothers-vengeance-making-the-scumbag-pay-5` | 30 / 30 | 30 eps | HLS/MP4 | ✅ Verificado |
| **A MOTHER'S VENGEANCE:MAKING THE SCUMBAG PAY** | `dt-a-mothers-vengeance-making-the-scumbag-pay-6` | 30 / 30 | 30 eps | HLS/MP4 | ✅ Verificado |
| **A MOTHER'S VENGEANCE:MAKING THE SCUMBAG PAY** | `dt-a-mothers-vengeance-making-the-scumbag-pay-7` | 30 / 30 | 30 eps | HLS/MP4 | ✅ Verificado |
| **A New Mate: Rise of the Silvermoon** | `dt-a-new-mate-rise-of-the-silvermoon` | 45 / 45 | 45 eps | HLS/MP4 | ✅ Verificado |
| **A Nobody? No, I'm Rich Baby!** | `dt-a-nobody-no-im-rich-baby` | 45 / 45 | 45 eps | HLS/MP4 | ✅ Verificado |
| **A one hundred million marriage** | `dt-a-one-hundred-million-marriage` | 20 / 20 | 20 eps | HLS/MP4 | ✅ Verificado |
| **A Pact Beneath the Moon** | `dt-a-pact-beneath-the-moon` | 10 / 10 | 10 eps | HLS/MP4 | ✅ Verificado |
| **A Perfect Elderly Love** | `dt-a-perfect-elderly-love` | 55 / 55 | 55 eps | HLS/MP4 | ✅ Verificado |
| **A Pilot's Betrayal, My Rebirth** | `dt-a-pilots-betrayal-my-rebirth` | 16 / 16 | 16 eps | HLS/MP4 | ✅ Verificado |
| **A Pilot's Betrayal, My Rebirth** | `dt-a-pilots-betrayal-my-rebirth-2` | 16 / 16 | 16 eps | HLS/MP4 | ✅ Verificado |
| **A Price to Pay** | `dt-a-price-to-pay` | 42 / 42 | 42 eps | HLS/MP4 | ✅ Verificado |
| **If Leaving Me Was Your Wish** | `dt-a-prince-consorts-atonement` | 57 / 57 | 57 eps | HLS/MP4 | ✅ Verificado |
| **A Promise That Made Us (Dubbed)** | `dt-a-promise-that-made-us` | 181 / 181 | 181 eps | HLS/MP4 | ✅ Verificado |
| **A Queen's Ascension (Dubbed)** | `dt-a-queens-ascension` | 60 / 60 | 60 eps | HLS/MP4 | ✅ Verificado |
| **A Revenge Journey of Reborn Jenny** | `dt-a-revenge-journey-of-reborn-jenny` | 65 / 65 | 65 eps | HLS/MP4 | ✅ Verificado |
| **A Second Chance, Living for My Own Self** | `dt-a-second-chance-living-for-my-own-self` | 60 / 60 | 60 eps | HLS/MP4 | ✅ Verificado |
| **A Secret Heir? He Regrets!** | `dt-a-secret-heir-he-regrets` | 78 / 78 | 78 eps | HLS/MP4 | ✅ Verificado |
| **A Sweet Contract with the Mafia Boss** | `dt-a-sweet-contract-with-the-mafia-boss-5` | 53 / 53 | 53 eps | HLS/MP4 | ✅ Verificado |
| **A Tale of Twin Serpents (Dubbed)** | `dt-a-tale-of-twin-serpents` | 32 / 32 | 32 eps | HLS/MP4 | ✅ Verificado |
| **A Tentaçã Mortal do Amor** | `dt-a-tentaca-mortal-do-amor` | 38 / 38 | 38 eps | HLS/MP4 | ✅ Verificado |
| **A Terminally Ill Woman's Payback** | `dt-a-terminally-ill-womans-payback-3` | 13 / 13 | 13 eps | HLS/MP4 | ✅ Verificado |
| **A Terminally Ill Woman's Payback** | `dt-a-terminally-ill-womans-payback-4` | 10 / 10 | 10 eps | HLS/MP4 | ✅ Verificado |
| **A Vengeful Ghost and Her Captor** | `dt-a-vengeful-ghost-and-her-captor` | 82 / 82 | 82 eps | HLS/MP4 | ✅ Verificado |
| **A Web of Power** | `dt-a-web-of-power` | 48 / 48 | 48 eps | HLS/MP4 | ✅ Verificado |
| **A Werewolf Song of Fire and Frost** | `dt-a-werewolf-song-of-fire-and-frost` | 33 / 33 | 33 eps | HLS/MP4 | ✅ Verificado |
| **A Wife's Sacrifice** | `dt-a-wifes-sacrifice` | 61 / 61 | 61 eps | HLS/MP4 | ✅ Verificado |
| **A Woman’s Choice** | `dt-a-womans-choice-2` | 118 / 118 | 118 eps | HLS/MP4 | ✅ Verificado |
| **Abandon Me Tenderly** | `dt-abandon-me-tenderly-3` | 60 / 60 | 60 eps | HLS/MP4 | ✅ Verificado |
| **Abandon Me Tenderly** | `dt-abandon-me-tenderly-4` | 45 / 45 | 45 eps | HLS/MP4 | ✅ Verificado |
| **Abandon Me Tenderly** | `dt-abandon-me-tenderly-5` | 49 / 49 | 49 eps | HLS/MP4 | ✅ Verificado |
| **Abandon Me Tenderly** | `dt-abandon-me-tenderly-6` | 39 / 39 | 39 eps | HLS/MP4 | ✅ Verificado |
| **Abandon Me Tenderly** | `dt-abandon-me-tenderly-7` | 56 / 56 | 56 eps | HLS/MP4 | ✅ Verificado |
| **Abandon Me Tenderly** | `dt-abandon-me-tenderly-8` | 60 / 60 | 60 eps | HLS/MP4 | ✅ Verificado |
| **Abandon Me Tenderly** | `dt-abandon-me-tenderly-9` | 60 / 60 | 60 eps | HLS/MP4 | ✅ Verificado |
| **Abandoned at 45 Adored by a Financial Giant** | `dt-abandoned-at-45-adored-by-a-financial-giant` | 22 / 22 | 22 eps | HLS/MP4 | ✅ Verificado |
| **Abandoned at the Altar I Married a Billionaire Tycoon** | `dt-abandoned-at-the-altar-i-married-a-billionaire-tycoon` | 72 / 72 | 72 eps | HLS/MP4 | ✅ Verificado |
| **Abandoned by My Husband, Two Brothers "Make Me a Billionaire"** | `dt-abandoned-by-my-husband-two-brothers-make-me-a-billionaire-3` | 60 / 60 | 60 eps | HLS/MP4 | ✅ Verificado |
| **Abandoned by My Husband, Two Brothers "Make Me a Billionaire"** | `dt-abandoned-by-my-husband-two-brothers-make-me-a-billionaire-8` | 43 / 43 | 43 eps | HLS/MP4 | ✅ Verificado |
| **Abandoned Empress of Jinghua** | `dt-abandoned-empress-of-jinghua` | 52 / 52 | 52 eps | HLS/MP4 | ✅ Verificado |
| **Abandoned Pawn, Unrivaled Dragon King** | `dt-abandoned-pawn-unrivaled-dragon-king` | 40 / 40 | 40 eps | HLS/MP4 | ✅ Verificado |
| **Abstinent CEO's Pregnant Sweetheart** | `dt-abstinent-ceos-pregnant-sweetheart-3` | 55 / 55 | 55 eps | HLS/MP4 | ✅ Verificado |
| **Abusive Family Begs Me on Their Knees** | `dt-abusive-family-begs-me-on-their-knees` | 61 / 61 | 61 eps | HLS/MP4 | ✅ Verificado |
| **Academy of Lies** | `dt-academy-of-lies` | 34 / 34 | 34 eps | HLS/MP4 | ✅ Verificado |
| **Accidentally Married My Boss** | `dt-accidentally-married-my-boss` | 70 / 70 | 70 eps | HLS/MP4 | ✅ Verificado |
| **Ace Pilot Forced to Abandon His Pregnant Lover** | `dt-ace-pilot-forced-to-abandon-his-pregnant-lover` | 11 / 11 | 11 eps | HLS/MP4 | ✅ Verificado |
| **Ace Pilot Forced to Abandon His Pregnant Lover** | `dt-ace-pilot-forced-to-abandon-his-pregnant-lover-2` | 11 / 11 | 11 eps | HLS/MP4 | ✅ Verificado |
| **Ace Pilot Forced to Abandon His Pregnant Lover** | `dt-ace-pilot-forced-to-abandon-his-pregnant-lover-3` | 15 / 15 | 15 eps | HLS/MP4 | ✅ Verificado |
| **Ace Pilot Forced to Abandon His Pregnant Lover** | `dt-ace-pilot-forced-to-abandon-his-pregnant-lover-4` | 15 / 15 | 15 eps | HLS/MP4 | ✅ Verificado |
| **Ace! The Golf King's Reconquest** | `dt-ace-the-golf-kings-reconquest` | 61 / 61 | 61 eps | HLS/MP4 | ✅ Verificado |
| **ADDICTED TO CROSSING THE LINE** | `dt-addicted-to-crossing-the-line-3` | 113 / 113 | 113 eps | HLS/MP4 | ✅ Verificado |
| **ADDICTED TO CROSSING THE LINE** | `dt-addicted-to-crossing-the-line-4` | 99 / 99 | 99 eps | HLS/MP4 | ✅ Verificado |
| **ADDICTED TO CROSSING THE LINE** | `dt-addicted-to-crossing-the-line-5` | 103 / 103 | 103 eps | HLS/MP4 | ✅ Verificado |
| **ADDICTED TO CROSSING THE LINE** | `dt-addicted-to-crossing-the-line-6` | 120 / 120 | 120 eps | HLS/MP4 | ✅ Verificado |
| **Addicted to Her as Night Falls** | `dt-addicted-to-her-as-night-falls` | 52 / 52 | 52 eps | HLS/MP4 | ✅ Verificado |
| **Addicted to Her Divine Beauty** | `dt-addicted-to-her-divine-beauty` | 83 / 83 | 83 eps | HLS/MP4 | ✅ Verificado |
| **Addicted to the Wrong Love** | `dt-addicted-to-the-wrong-love` | 100 / 100 | 100 eps | HLS/MP4 | ✅ Verificado |
| **Addicted to You, Bound by Sin** | `dt-addicted-to-you-bound-by-sin` | 111 / 111 | 111 eps | HLS/MP4 | ✅ Verificado |
| **Addictive Love** | `dt-addictive-love` | 89 / 89 | 89 eps | HLS/MP4 | ✅ Verificado |
| **Adorable Quinn** | `dt-adorable-quinn-2` | 60 / 60 | 60 eps | HLS/MP4 | ✅ Verificado |
| **Adrift in Space: Her Bitter Regret Over Her Ex** | `dt-adrift-in-space-her-bitter-regret-over-her-ex-3` | 40 / 40 | 40 eps | HLS/MP4 | ✅ Verificado |
| **Adventure Speed in the Arctic Desert** | `dt-adventure-speed-in-the-arctic-desert` | 100 / 100 | 100 eps | HLS/MP4 | ✅ Verificado |
| **Affection That Eats Into The Bones** | `dt-affection-that-eats-into-the-bones` | 70 / 70 | 70 eps | HLS/MP4 | ✅ Verificado |
| **After 9 No-Shows, I Married My Fiancé's Nemesis** | `dt-after-9-no-shows-i-married-my-fiances-nemesis` | 14 / 14 | 14 eps | HLS/MP4 | ✅ Verificado |
| **After a narrow escape, the scapegoat female president went crazy** | `dt-after-a-narrow-escape-the-scapegoat-female-president-went-crazy-3` | 15 / 15 | 15 eps | HLS/MP4 | ✅ Verificado |
| **After a Wild Night, Pretty CEO and Child at My Door** | `dt-after-a-wild-night-pretty-ceo-and-child-at-my-door` | 58 / 58 | 58 eps | HLS/MP4 | ✅ Verificado |
| **After accidentally entering the boss'sroom** | `dt-after-accidentally-entering-the-bosssroom` | 60 / 60 | 60 eps | HLS/MP4 | ✅ Verificado |
| **After accidentally entering the boss'sroom** | `dt-after-accidentally-entering-the-bosssroom-2` | 60 / 60 | 60 eps | HLS/MP4 | ✅ Verificado |
| **After Amnesia,I Married My Crush** | `dt-after-amnesia-i-married-my-crush-3` | 78 / 78 | 78 eps | HLS/MP4 | ✅ Verificado |
| **After Amnesia,I Married My Crush** | `dt-after-amnesia-i-married-my-crush-4` | 68 / 68 | 68 eps | HLS/MP4 | ✅ Verificado |
| **After Amnesia,I Married My Crush** | `dt-after-amnesia-i-married-my-crush-5` | 15 / 15 | 15 eps | HLS/MP4 | ✅ Verificado |
| **After amnesia: I no longer serve as a cash cow for men** | `dt-after-amnesia-i-no-longer-serve-as-a-cash-cow-for-men-2` | 15 / 15 | 15 eps | HLS/MP4 | ✅ Verificado |
| **After amnesia: I no longer serve as a cash cow for men** | `dt-after-amnesia-i-no-longer-serve-as-a-cash-cow-for-men-3` | 15 / 15 | 15 eps | HLS/MP4 | ✅ Verificado |
| **After amnesia: I no longer serve as a cash cow for men** | `dt-after-amnesia-i-no-longer-serve-as-a-cash-cow-for-men-4` | 15 / 15 | 15 eps | HLS/MP4 | ✅ Verificado |
| **After Amnesia, No More Tolerance** | `dt-after-amnesia-no-more-tolerance` | 61 / 61 | 61 eps | HLS/MP4 | ✅ Verificado |
| **After an Influencer Insulted a National Hero** | `dt-after-an-influencer-insulted-a-national-hero` | 30 / 30 | 30 eps | HLS/MP4 | ✅ Verificado |
| **After Bearing His Divine Heir, I Was Spoiled Rotten Lord Hades** | `dt-after-bearing-his-divine-heir-i-was-spoiled-rotten-lord-hades` | 64 / 64 | 64 eps | HLS/MP4 | ✅ Verificado |
| **After Bearing His Divine Heir, I Was Spoiled Rotten Lord Hades** | `dt-after-bearing-his-divine-heir-i-was-spoiled-rotten-lord-hades-2` | 64 / 64 | 64 eps | HLS/MP4 | ✅ Verificado |
| **After Becoming the Villainess, I Saved the Demon King** | `dt-after-becoming-the-villainess-i-saved-the-demon-king` | 37 / 37 | 37 eps | HLS/MP4 | ✅ Verificado |
| **After Being Abandoned by the Alpha, I Took Away His Heir** | `dt-after-being-abandoned-by-the-alpha-i-took-away-his-heir` | 8 / 8 | 8 eps | HLS/MP4 | ✅ Verificado |
| **After Being Betrayed, Superpower Girl Returns To Her Eighteen** | `dt-after-being-betrayed-superpower-girl-returns-to-her-eighteen` | 60 / 60 | 60 eps | HLS/MP4 | ✅ Verificado |
| **After Being Betrayed, Superpower Girl Returns To Her Eighteen** | `dt-after-being-betrayed-superpower-girl-returns-to-her-eighteen-2` | 60 / 60 | 60 eps | HLS/MP4 | ✅ Verificado |
| **After being killed by my mother, I finally stopped loving her.** | `dt-after-being-killed-by-my-mother-i-finally-stopped-loving-her-3` | 60 / 60 | 60 eps | HLS/MP4 | ✅ Verificado |
| **After big brother's death, sister-in-law went on a rampage** | `dt-after-big-brothers-death-sister-in-law-went-on-a-rampage` | 80 / 80 | 80 eps | HLS/MP4 | ✅ Verificado |
| **After breaking the contract, that genius husband went mad** | `dt-after-breaking-the-contract-that-genius-husband-went-mad` | 30 / 30 | 30 eps | HLS/MP4 | ✅ Verificado |
| **After Death,The Tyrant Begs Me to Return** | `dt-after-death-the-tyrant-begs-me-to-return` | 111 / 111 | 111 eps | HLS/MP4 | ✅ Verificado |
| **After Death,The Tyrant Begs Me to Return** | `dt-after-death-the-tyrant-begs-me-to-return-2` | 120 / 120 | 120 eps | HLS/MP4 | ✅ Verificado |
| **After Death,The Tyrant Begs Me to Return** | `dt-after-death-the-tyrant-begs-me-to-return-3` | 65 / 65 | 65 eps | HLS/MP4 | ✅ Verificado |
| **After Death,The Tyrant Begs Me to Return** | `dt-after-death-the-tyrant-begs-me-to-return-4` | 55 / 55 | 55 eps | HLS/MP4 | ✅ Verificado |
| **After Death,The Tyrant Begs Me to Return** | `dt-after-death-the-tyrant-begs-me-to-return-5` | 120 / 120 | 120 eps | HLS/MP4 | ✅ Verificado |
| **AFTER DIVORCE,HE LEARNEDE** | `dt-after-divorce-he-learnede` | 46 / 46 | 46 eps | HLS/MP4 | ✅ Verificado |
| **AFTER DIVORCE,HE LEARNEDE** | `dt-after-divorce-he-learnede-2` | 60 / 60 | 60 eps | HLS/MP4 | ✅ Verificado |
| **AFTER DIVORCE,HE LEARNEDE** | `dt-after-divorce-he-learnede-4` | 49 / 49 | 49 eps | HLS/MP4 | ✅ Verificado |
| **After Divorce, He Panicked** | `dt-after-divorce-he-panicked-5` | 57 / 57 | 57 eps | HLS/MP4 | ✅ Verificado |
| **After Divorce, I Became a Silicon Valley Legend** | `dt-after-divorce-i-became-a-silicon-valley-legend-10` | 60 / 60 | 60 eps | HLS/MP4 | ✅ Verificado |
| **After Divorce, I Became a Silicon Valley Legend** | `dt-after-divorce-i-became-a-silicon-valley-legend-2` | 60 / 60 | 60 eps | HLS/MP4 | ✅ Verificado |
| **After Divorce, I Became a Silicon Valley Legend** | `dt-after-divorce-i-became-a-silicon-valley-legend-5` | 60 / 60 | 60 eps | HLS/MP4 | ✅ Verificado |
| **After Divorce, I Became a Silicon Valley Legend** | `dt-after-divorce-i-became-a-silicon-valley-legend-6` | 60 / 60 | 60 eps | HLS/MP4 | ✅ Verificado |
| **After Divorce, I Became a Silicon Valley Legend** | `dt-after-divorce-i-became-a-silicon-valley-legend-8` | 60 / 60 | 60 eps | HLS/MP4 | ✅ Verificado |
| **After Divorce, I Became a Silicon Valley Legend** | `dt-after-divorce-i-became-a-silicon-valley-legend-9` | 60 / 60 | 60 eps | HLS/MP4 | ✅ Verificado |
| **After Divorce,I Became His Stepmother's Bride** | `dt-after-divorce-i-became-his-stepmothers-bride-3` | 54 / 54 | 54 eps | HLS/MP4 | ✅ Verificado |
| **After Divorce,I Became His Stepmother's Bride** | `dt-after-divorce-i-became-his-stepmothers-bride-4` | 42 / 42 | 42 eps | HLS/MP4 | ✅ Verificado |
| **After Divorce,I Became His Stepmother's Bride** | `dt-after-divorce-i-became-his-stepmothers-bride-5` | 53 / 53 | 53 eps | HLS/MP4 | ✅ Verificado |
| **After Divorce, I Became My Ex-Husband's Stepmother** | `dt-after-divorce-i-became-my-ex-husbands-stepmother` | 60 / 60 | 60 eps | HLS/MP4 | ✅ Verificado |
| **After Divorce, I Became the Mafia Queen** | `dt-after-divorce-i-became-the-mafia-queen-3` | 58 / 58 | 58 eps | HLS/MP4 | ✅ Verificado |
| **After Divorce, I Became the Mafia Queen** | `dt-after-divorce-i-became-the-mafia-queen-4` | 56 / 56 | 56 eps | HLS/MP4 | ✅ Verificado |
| **After Divorce I Become Hybrid Alpha's Luna** | `dt-after-divorce-i-become-hybrid-alphas-luna-2` | 53 / 53 | 53 eps | HLS/MP4 | ✅ Verificado |
| **After Divorce, I Found Out I'm the First Love of Alpha** | `dt-after-divorce-i-found-out-im-the-first-love-of-alpha-3` | 60 / 60 | 60 eps | HLS/MP4 | ✅ Verificado |
| **After Divorce, I Found Out I'm the First Love of Alpha** | `dt-after-divorce-i-found-out-im-the-first-love-of-alpha-4` | 60 / 60 | 60 eps | HLS/MP4 | ✅ Verificado |
| **After Divorce, I Owned Three Billionaires** | `dt-after-divorce-i-owned-three-billionaires-2` | 69 / 69 | 69 eps | HLS/MP4 | ✅ Verificado |
| **After Divorce,I Thrived-My ExWent Crazy Chasing me** | `dt-after-divorce-i-thrived-my-exwent-crazy-chasing-me-3` | 13 / 13 | 13 eps | HLS/MP4 | ✅ Verificado |
| **After Divorce,I Thrived-My ExWent Crazy Chasing me** | `dt-after-divorce-i-thrived-my-exwent-crazy-chasing-me-4` | 11 / 11 | 11 eps | HLS/MP4 | ✅ Verificado |
| **After Divorce,I Thrived-My ExWent Crazy Chasing me** | `dt-after-divorce-i-thrived-my-exwent-crazy-chasing-me-5` | 14 / 14 | 14 eps | HLS/MP4 | ✅ Verificado |
| **After Divorce,I Thrived-My ExWent Crazy Chasing me** | `dt-after-divorce-i-thrived-my-exwent-crazy-chasing-me-6` | 15 / 15 | 15 eps | HLS/MP4 | ✅ Verificado |
| **After Divorce,I Thrived-My ExWent Crazy Chasing me** | `dt-after-divorce-i-thrived-my-exwent-crazy-chasing-me-7` | 15 / 15 | 15 eps | HLS/MP4 | ✅ Verificado |
| **After Divorce,I Thrived-My ExWent Crazy Chasing me** | `dt-after-divorce-i-thrived-my-exwent-crazy-chasing-me-8` | 15 / 15 | 15 eps | HLS/MP4 | ✅ Verificado |
| **After Divorce,I Thrived-My ExWent Crazy Chasing me** | `dt-after-divorce-i-thrived-my-exwent-crazy-chasing-me-9` | 15 / 15 | 15 eps | HLS/MP4 | ✅ Verificado |
| **After Divorce, My Cheating CEO Ex Begged** | `dt-after-divorce-my-cheating-ceo-ex-begged-subtitled` | 27 / 27 | 27 eps | HLS/MP4 | ✅ Verificado |
| **After Divorce, She Stuns the World** | `dt-after-divorce-she-stuns-the-world-3` | 80 / 80 | 80 eps | HLS/MP4 | ✅ Verificado |
| **After Divorce, She Stuns the World** | `dt-after-divorce-she-stuns-the-world-5` | 80 / 80 | 80 eps | HLS/MP4 | ✅ Verificado |
| **After Divorce, She Stuns the World** | `dt-after-divorce-she-stuns-the-world-6` | 65 / 65 | 65 eps | HLS/MP4 | ✅ Verificado |
| **After Divorce, She Stuns the World** | `dt-after-divorce-she-stuns-the-world-7` | 45 / 45 | 45 eps | HLS/MP4 | ✅ Verificado |
| **After Divorce, She Stuns the World** | `dt-after-divorce-she-stuns-the-world-8` | 72 / 72 | 72 eps | HLS/MP4 | ✅ Verificado |
| **After Divorce, Spoiled by the Cold CEO (DUBBED)** | `dt-after-divorce-spoiled-by-the-cold-ceo` | 77 / 77 | 77 eps | HLS/MP4 | ✅ Verificado |
| **After Divorce, Stripper CEO and I Dominate Hollywood** | `dt-after-divorce-stripper-ceo-and-i-dominate-hollywood-2` | 44 / 44 | 44 eps | HLS/MP4 | ✅ Verificado |
| **After Divorce Three Aces Beg To Marry Me** | `dt-after-divorce-three-aces-beg-to-marry-me-3` | 45 / 45 | 45 eps | HLS/MP4 | ✅ Verificado |
| **After Divorce, Three Fiancés Chase Me Wildly** | `dt-after-divorce-three-fiances-chase-me-wildly-4` | 55 / 55 | 55 eps | HLS/MP4 | ✅ Verificado |
| **After Divorce, Three Fiancés Chase Me Wildly** | `dt-after-divorce-three-fiances-chase-me-wildly-5` | 60 / 60 | 60 eps | HLS/MP4 | ✅ Verificado |
| **After Divorce, Wall Street's Moguls Crave Me** | `dt-after-divorce-wall-streets-moguls-crave-me` | 70 / 70 | 70 eps | HLS/MP4 | ✅ Verificado |
| **After Divorce, Wall Street's Moguls Crave Me** | `dt-after-divorce-wall-streets-moguls-crave-me-3` | 70 / 70 | 70 eps | HLS/MP4 | ✅ Verificado |
| **After Divorce, Wall Street's Moguls Crave Me** | `dt-after-divorce-wall-streets-moguls-crave-me-4` | 62 / 62 | 62 eps | HLS/MP4 | ✅ Verificado |
| **After Divorce, Wall Street's Moguls Crave Me** | `dt-after-divorce-wall-streets-moguls-crave-me-5` | 52 / 52 | 52 eps | HLS/MP4 | ✅ Verificado |
| **After Divorcing My Husband, I Became Out of His League** | `dt-after-divorcing-my-husband-i-became-out-of-his-league-2` | 32 / 32 | 32 eps | HLS/MP4 | ✅ Verificado |
| **After Driving Me Off, He's Unworthy** | `dt-after-driving-me-off-hes-unworthy-3` | 9 / 9 | 9 eps | HLS/MP4 | ✅ Verificado |
| **After Driving Me Off, He's Unworthy** | `dt-after-driving-me-off-hes-unworthy-4` | 8 / 8 | 8 eps | HLS/MP4 | ✅ Verificado |
| **After Escaping My Crazy Stepbrother, I Became the Queen of the European Racecourse** | `dt-after-escaping-my-crazy-stepbrother-i-became-the-queen-of-the-european-racecourse-4` | 73 / 73 | 73 eps | HLS/MP4 | ✅ Verificado |
| **After Finding a Stand-In, the CEO Regretted It** | `dt-after-finding-a-stand-in-the-ceo-regretted-it` | 14 / 14 | 14 eps | HLS/MP4 | ✅ Verificado |
| **After Flash Marriage: The Mature Guy Dotes on Me Obediently (Dubbed)** | `dt-after-flash-marriage-the-mature-guy-dotes-on-me-obediently` | 75 / 75 | 75 eps | HLS/MP4 | ✅ Verificado |
| **After Forcing Me to Take the Blame and Miscarry,My Chaebol Ex Is Destroyed by Regret** | `dt-after-forcing-me-to-take-the-blame-and-miscarry-my-chaebol-ex-is-destroyed-by-regret` | 41 / 41 | 41 eps | HLS/MP4 | ✅ Verificado |
| **After Forcing Me to Take the Blame and Miscarry,My Chaebol Ex Is Destroyed by Regret** | `dt-after-forcing-me-to-take-the-blame-and-miscarry-my-chaebol-ex-is-destroyed-by-regret-3` | 56 / 56 | 56 eps | HLS/MP4 | ✅ Verificado |
| **After Forcing Me to Take the Blame and Miscarry,My Chaebol Ex Is Destroyed by Regret** | `dt-after-forcing-me-to-take-the-blame-and-miscarry-my-chaebol-ex-is-destroyed-by-regret-4` | 78 / 78 | 78 eps | HLS/MP4 | ✅ Verificado |
| **After Forcing Me to Take the Blame and Miscarry,My Chaebol Ex Is Destroyed by Regret** | `dt-after-forcing-me-to-take-the-blame-and-miscarry-my-chaebol-ex-is-destroyed-by-regret-5` | 80 / 80 | 80 eps | HLS/MP4 | ✅ Verificado |
| **After Forcing Me to Take the Blame and Miscarry,My Chaebol Ex Is Destroyed by Regret** | `dt-after-forcing-me-to-take-the-blame-and-miscarry-my-chaebol-ex-is-destroyed-by-regret-6` | 57 / 57 | 57 eps | HLS/MP4 | ✅ Verificado |
| **AFTER HEARTBREAK I RISE TO THE TOP** | `dt-after-heartbreak-i-rise-to-the-top-3` | 15 / 15 | 15 eps | HLS/MP4 | ✅ Verificado |
| **AFTER HEARTBREAK I RISE TO THE TOP** | `dt-after-heartbreak-i-rise-to-the-top-4` | 14 / 14 | 14 eps | HLS/MP4 | ✅ Verificado |
| **AFTER HEARTBREAK I RISE TO THE TOP** | `dt-after-heartbreak-i-rise-to-the-top-5` | 14 / 14 | 14 eps | HLS/MP4 | ✅ Verificado |
| **AFTER HEARTBREAK I RISE TO THE TOP** | `dt-after-heartbreak-i-rise-to-the-top-6` | 15 / 15 | 15 eps | HLS/MP4 | ✅ Verificado |
| **AFTER HEARTBREAK I RISE TO THE TOP** | `dt-after-heartbreak-i-rise-to-the-top-7` | 13 / 13 | 13 eps | HLS/MP4 | ✅ Verificado |
| **After Heartbreak, I Unleash My Edge** | `dt-after-heartbreak-i-unleash-my-edge-3` | 57 / 57 | 57 eps | HLS/MP4 | ✅ Verificado |
| **After Heartbreak, I Unleash My Edge** | `dt-after-heartbreak-i-unleash-my-edge-4` | 60 / 60 | 60 eps | HLS/MP4 | ✅ Verificado |
| **After Her Goodbye** | `dt-after-her-goodbye` | 70 / 70 | 70 eps | HLS/MP4 | ✅ Verificado |
| **After Her Goodbye** | `dt-after-her-goodbye-2` | 64 / 64 | 64 eps | HLS/MP4 | ✅ Verificado |
| **After Her Goodbye** | `dt-after-her-goodbye-3` | 36 / 36 | 36 eps | HLS/MP4 | ✅ Verificado |
| **After Her Goodbye** | `dt-after-her-goodbye-4` | 70 / 70 | 70 eps | HLS/MP4 | ✅ Verificado |
| **After Her Goodbye** | `dt-after-her-goodbye-5` | 67 / 67 | 67 eps | HLS/MP4 | ✅ Verificado |
| **After Her Goodbye** | `dt-after-her-goodbye-6` | 70 / 70 | 70 eps | HLS/MP4 | ✅ Verificado |
| **After Her Goodbye** | `dt-after-her-goodbye-7` | 70 / 70 | 70 eps | HLS/MP4 | ✅ Verificado |
| **After His 100th Betrayal, I Severed Our Fated Bond** | `dt-after-his-100th-betrayal-i-severed-our-fated-bond` | 12 / 12 | 12 eps | HLS/MP4 | ✅ Verificado |
| **After I Became the Doomed Sect Master** | `dt-after-i-became-the-doomed-sect-master` | 59 / 59 | 59 eps | HLS/MP4 | ✅ Verificado |
| **After I Broke Our Bond, My Ex KneIt and Begged for My Blood Aurora Thorn False Saint Corruption's Origin** | `dt-after-i-broke-our-bond-my-ex-kneit-and-begged-for-my-blood-aurora-thorn-false-saint-corruptions-origin-4` | 60 / 60 | 60 eps | HLS/MP4 | ✅ Verificado |
| **After I Broke Our Bond, My Ex KneIt and Begged for My Blood Aurora Thorn False Saint Corruption's Origin** | `dt-after-i-broke-our-bond-my-ex-kneit-and-begged-for-my-blood-aurora-thorn-false-saint-corruptions-origin-5` | 19 / 19 | 19 eps | HLS/MP4 | ✅ Verificado |
| **After I Died, He Chased Me South** | `dt-after-i-died-he-chased-me-south` | 39 / 39 | 39 eps | HLS/MP4 | ✅ Verificado |
| **After I Died, He Went Mad** | `dt-after-i-died-he-went-mad-2` | 27 / 27 | 27 eps | HLS/MP4 | ✅ Verificado |
| **After I Kissed The Bully, He Thought He Was Gay** | `dt-after-i-kissed-the-bully-he-thought-he-was-gay-4` | 61 / 61 | 61 eps | HLS/MP4 | ✅ Verificado |
| **After I left,The CEO Begged** | `dt-after-i-left-the-ceo-begged` | 10 / 10 | 10 eps | HLS/MP4 | ✅ Verificado |
| **After I married a vampire, he regret** | `dt-after-i-married-a-vampire-he-regret` | 45 / 45 | 45 eps | HLS/MP4 | ✅ Verificado |
| **After I Pretended to Die, the CEO Went Completely Mad** | `dt-after-i-pretended-to-die-the-ceo-went-completely-mad-3` | 64 / 64 | 64 eps | HLS/MP4 | ✅ Verificado |
| **After I Pretended to Die, the CEO Went Completely Mad** | `dt-after-i-pretended-to-die-the-ceo-went-completely-mad-4` | 53 / 53 | 53 eps | HLS/MP4 | ✅ Verificado |
| **After I Pretended to Die, the CEO Went Completely Mad** | `dt-after-i-pretended-to-die-the-ceo-went-completely-mad-5` | 80 / 80 | 80 eps | HLS/MP4 | ✅ Verificado |
| **After I Pretended to Die, the CEO Went Completely Mad** | `dt-after-i-pretended-to-die-the-ceo-went-completely-mad-6` | 80 / 80 | 80 eps | HLS/MP4 | ✅ Verificado |
| **After I Remarried, My Wolf Men Brothers Went Mad** | `dt-after-i-remarried-my-wolf-men-brothers-went-mad-2` | 50 / 50 | 50 eps | HLS/MP4 | ✅ Verificado |
| **After I Shattered the Mark, the Alpha Knelt at My Feet** | `dt-after-i-shattered-the-mark-the-alpha-knelt-at-my-feet` | 14 / 14 | 14 eps | HLS/MP4 | ✅ Verificado |
| **After I Sold My Special Service to a Billionaire** | `dt-after-i-sold-my-special-service-to-a-billionaire-2` | 48 / 48 | 48 eps | HLS/MP4 | ✅ Verificado |
| **After I WAS RELEASED FROM PRISON, THE WHOLE FAMILY KNEEL DOWN BEGGING ME FOR Forgiveness** | `dt-after-i-was-released-from-prison-the-whole-family-kneel-down-begging-me-for-forgiveness` | 38 / 38 | 38 eps | HLS/MP4 | ✅ Verificado |
| **After I WAS RELEASED FROM PRISON, THE WHOLE FAMILY KNEEL DOWN BEGGING ME FOR Forgiveness** | `dt-after-i-was-released-from-prison-the-whole-family-kneel-down-begging-me-for-forgiveness-2` | 62 / 62 | 62 eps | HLS/MP4 | ✅ Verificado |
| **After I WAS RELEASED FROM PRISON, THE WHOLE FAMILY KNEEL DOWN BEGGING ME FOR Forgiveness** | `dt-after-i-was-released-from-prison-the-whole-family-kneel-down-begging-me-for-forgiveness-4` | 62 / 62 | 62 eps | HLS/MP4 | ✅ Verificado |
| **After I Went Mad,He Said He Loved Me** | `dt-after-i-went-mad-he-said-he-loved-me-5` | 60 / 60 | 60 eps | HLS/MP4 | ✅ Verificado |
| **AFTER IDIED, MY PILOT HUSBAND WENT MAD WITH REGRET** | `dt-after-idied-my-pilot-husband-went-mad-with-regret-3` | 62 / 62 | 62 eps | HLS/MP4 | ✅ Verificado |
| **AFTER IDIED, MY PILOT HUSBAND WENT MAD WITH REGRET** | `dt-after-idied-my-pilot-husband-went-mad-with-regret-4` | 62 / 62 | 62 eps | HLS/MP4 | ✅ Verificado |
| **AFTER I’M GONE,MOM STOPS Playing Favorites** | `dt-after-im-gone-mom-stops-playing-favorites-3` | 60 / 60 | 60 eps | HLS/MP4 | ✅ Verificado |
| **After leaving with our child, the CEO knelt before me begging for a reconciliation.** | `dt-after-leaving-with-our-child-the-ceo-knelt-before-me-begging-for-a-reconciliation` | 62 / 62 | 62 eps | HLS/MP4 | ✅ Verificado |
| **After leaving with our child, the CEO knelt before me begging for a reconciliation.** | `dt-after-leaving-with-our-child-the-ceo-knelt-before-me-begging-for-a-reconciliation-2` | 62 / 62 | 62 eps | HLS/MP4 | ✅ Verificado |
| **After leaving with our child, the CEO knelt before me begging for a reconciliation.** | `dt-after-leaving-with-our-child-the-ceo-knelt-before-me-begging-for-a-reconciliation-3` | 62 / 62 | 62 eps | HLS/MP4 | ✅ Verificado |
| **After leaving with our child, the CEO knelt before me begging for a reconciliation.** | `dt-after-leaving-with-our-child-the-ceo-knelt-before-me-begging-for-a-reconciliation-4` | 57 / 57 | 57 eps | HLS/MP4 | ✅ Verificado |
| **After leaving with our child, the CEO knelt before me begging for a reconciliation.** | `dt-after-leaving-with-our-child-the-ceo-knelt-before-me-begging-for-a-reconciliation-5` | 46 / 46 | 46 eps | HLS/MP4 | ✅ Verificado |
| **After Miscarriage, I Slaughtered Them All** | `dt-after-miscarriage-i-slaughtered-them-all-4` | 52 / 52 | 52 eps | HLS/MP4 | ✅ Verificado |
| **After My Daughter Died, I Became His Executioner** | `dt-after-my-daughter-died-i-became-his-executioner` | 23 / 23 | 23 eps | HLS/MP4 | ✅ Verificado |
| **After My Death, My Brothers Help Me Revenge** | `dt-after-my-death-my-brothers-help-me-revenge-2` | 27 / 27 | 27 eps | HLS/MP4 | ✅ Verificado |
| **After my divorce, I became the god of medicine that my ex husband begged on his knees** | `dt-after-my-divorce-i-became-the-god-of-medicine-that-my-ex-husband-begged-on-his-knees-3` | 15 / 15 | 15 eps | HLS/MP4 | ✅ Verificado |
| **After My Husband Cheated, I Became the Vengeful Queen** | `dt-after-my-husband-cheated-i-became-the-vengeful-queen-3` | 48 / 48 | 48 eps | HLS/MP4 | ✅ Verificado |
| **After My Husband Cheated, I Became the Vengeful Queen** | `dt-after-my-husband-cheated-i-became-the-vengeful-queen-4` | 23 / 23 | 23 eps | HLS/MP4 | ✅ Verificado |
| **After My Husband Cheated, I Became the Vengeful Queen** | `dt-after-my-husband-cheated-i-became-the-vengeful-queen-5` | 35 / 35 | 35 eps | HLS/MP4 | ✅ Verificado |
| **After My Husband Cheated, I Became the Vengeful Queen** | `dt-after-my-husband-cheated-i-became-the-vengeful-queen-6` | 60 / 60 | 60 eps | HLS/MP4 | ✅ Verificado |
| **After My Husband Cheated, I Inherited a Fortun** | `dt-after-my-husband-cheated-i-inherited-a-fortun` | 14 / 14 | 14 eps | HLS/MP4 | ✅ Verificado |
| **After My Husband Cheated, I Inherited a Fortune** | `dt-after-my-husband-cheated-i-inherited-a-fortune` | 14 / 14 | 14 eps | HLS/MP4 | ✅ Verificado |
| **After My Husband Cheated, I sleep with the Mistress's Son** | `dt-after-my-husband-cheated-i-sleep-with-the-mistresss-son` | 60 / 60 | 60 eps | HLS/MP4 | ✅ Verificado |
| **After My Husband Cheated, I sleep with the Mistress's Son** | `dt-after-my-husband-cheated-i-sleep-with-the-mistresss-son-2` | 47 / 47 | 47 eps | HLS/MP4 | ✅ Verificado |
| **After my husband tattooed a succubus mark on me** | `dt-after-my-husband-tattooed-a-succubus-mark-on-me` | 27 / 27 | 27 eps | HLS/MP4 | ✅ Verificado |
| **After My Mother-in-law Was Killed by My Husband, I Went on a Rampage!** | `dt-after-my-mother-in-law-was-killed-by-my-husband-i-went-on-a-rampage` | 30 / 30 | 30 eps | HLS/MP4 | ✅ Verificado |
| **After My Release,The Whole Family Regretted It** | `dt-after-my-release-the-whole-family-regretted-it-4` | 60 / 60 | 60 eps | HLS/MP4 | ✅ Verificado |
| **After my resignation, the CEO's partner knelt before me begging for a reconciliation.** | `dt-after-my-resignation-the-ceos-partner-knelt-before-me-begging-for-a-reconciliation-3` | 50 / 50 | 50 eps | HLS/MP4 | ✅ Verificado |
| **After my resignation, the CEO's partner knelt before me begging for a reconciliation.** | `dt-after-my-resignation-the-ceos-partner-knelt-before-me-begging-for-a-reconciliation-4` | 15 / 15 | 15 eps | HLS/MP4 | ✅ Verificado |
| **After my resignation, the CEO's partner knelt before me begging for a reconciliation.** | `dt-after-my-resignation-the-ceos-partner-knelt-before-me-begging-for-a-reconciliation-7` | 60 / 60 | 60 eps | HLS/MP4 | ✅ Verificado |
| **After my resignation, the CEO's partner knelt before me begging for a reconciliation.** | `dt-after-my-resignation-the-ceos-partner-knelt-before-me-begging-for-a-reconciliation-8` | 60 / 60 | 60 eps | HLS/MP4 | ✅ Verificado |
| **After ONE NIGHT,I MARRIED A BILLIONAIRE** | `dt-after-one-night-i-married-a-billionaire-2` | 63 / 63 | 63 eps | HLS/MP4 | ✅ Verificado |
| **After One Night with the Dragon King** | `dt-after-one-night-with-the-dragon-king-3` | 70 / 70 | 70 eps | HLS/MP4 | ✅ Verificado |
| **After Pregnancy,I Became My Ex's Widowed Sister-in-Law** | `dt-after-pregnancy-i-became-my-exs-widowed-sister-in-law-3` | 15 / 15 | 15 eps | HLS/MP4 | ✅ Verificado |
| **After Pregnancy,I Became My Ex's Widowed Sister-in-Law** | `dt-after-pregnancy-i-became-my-exs-widowed-sister-in-law-4` | 15 / 15 | 15 eps | HLS/MP4 | ✅ Verificado |
| **After Pregnancy,I Became My Ex's Widowed Sister-in-Law** | `dt-after-pregnancy-i-became-my-exs-widowed-sister-in-law-5` | 15 / 15 | 15 eps | HLS/MP4 | ✅ Verificado |
| **After Pregnancy,I Became My Ex's Widowed Sister-in-Law** | `dt-after-pregnancy-i-became-my-exs-widowed-sister-in-law-6` | 15 / 15 | 15 eps | HLS/MP4 | ✅ Verificado |
| **After Pregnancy,I Became My Ex's Widowed Sister-in-Law** | `dt-after-pregnancy-i-became-my-exs-widowed-sister-in-law-7` | 15 / 15 | 15 eps | HLS/MP4 | ✅ Verificado |
| **After Pregnancy,I Became My Ex's Widowed Sister-in-Law** | `dt-after-pregnancy-i-became-my-exs-widowed-sister-in-law-8` | 15 / 15 | 15 eps | HLS/MP4 | ✅ Verificado |
| **After prison,I became the antidote for the Sadism mafia** | `dt-after-prison-i-became-the-antidote-for-the-sadism-mafia-3` | 81 / 81 | 81 eps | HLS/MP4 | ✅ Verificado |
| **After prison,I became the antidote for the Sadism mafia** | `dt-after-prison-i-became-the-antidote-for-the-sadism-mafia-4` | 71 / 71 | 71 eps | HLS/MP4 | ✅ Verificado |
| **After prison,I became the antidote for the Sadism mafia** | `dt-after-prison-i-became-the-antidote-for-the-sadism-mafia-5` | 71 / 71 | 71 eps | HLS/MP4 | ✅ Verificado |
| **After Quitting as a Stand‑in, I Dazzle the Whole Venue** | `dt-after-quitting-as-a-standin-i-dazzle-the-whole-venue-2` | 50 / 50 | 50 eps | HLS/MP4 | ✅ Verificado |
| **AFTER READING HIS MIND I COMPLETELY DESTROYED HIM** | `dt-after-reading-his-mind-i-completely-destroyed-him` | 15 / 15 | 15 eps | HLS/MP4 | ✅ Verificado |
| **AFTER READING HIS MIND I COMPLETELY DESTROYED HIM** | `dt-after-reading-his-mind-i-completely-destroyed-him-2` | 15 / 15 | 15 eps | HLS/MP4 | ✅ Verificado |
| **AFTER READING HIS MIND I COMPLETELY DESTROYED HIM** | `dt-after-reading-his-mind-i-completely-destroyed-him-3` | 15 / 15 | 15 eps | HLS/MP4 | ✅ Verificado |
| **AFTER READING HIS MIND I COMPLETELY DESTROYED HIM** | `dt-after-reading-his-mind-i-completely-destroyed-him-4` | 15 / 15 | 15 eps | HLS/MP4 | ✅ Verificado |
| **AFTER READING HIS MIND I COMPLETELY DESTROYED HIM** | `dt-after-reading-his-mind-i-completely-destroyed-him-5` | 15 / 15 | 15 eps | HLS/MP4 | ✅ Verificado |
| **AFTER READING HIS MIND I COMPLETELY DESTROYED HIM** | `dt-after-reading-his-mind-i-completely-destroyed-him-6` | 15 / 15 | 15 eps | HLS/MP4 | ✅ Verificado |
| **AFTER READING HIS MIND I COMPLETELY DESTROYED HIM** | `dt-after-reading-his-mind-i-completely-destroyed-him-7` | 15 / 15 | 15 eps | HLS/MP4 | ✅ Verificado |
| **AFTER REBIRETH I FED THE SCUMBG MAN AND HIS VILE MISTRESS TO THE ZOMBIES** | `dt-after-rebireth-i-fed-the-scumbg-man-and-his-vile-mistress-to-the-zombies-2` | 60 / 60 | 60 eps | HLS/MP4 | ✅ Verificado |
| **After Rebirth,i am prisoner in my l enemy's palm** | `dt-after-rebirth-i-am-prisoner-in-my-l-enemys-palm` | 62 / 62 | 62 eps | HLS/MP4 | ✅ Verificado |
| **After Rebirth, I Destroyed My Own Family** | `dt-after-rebirth-i-destroyed-my-own-family-3` | 15 / 15 | 15 eps | HLS/MP4 | ✅ Verificado |
| **After Rebirth, I Destroyed My Own Family** | `dt-after-rebirth-i-destroyed-my-own-family-4` | 15 / 15 | 15 eps | HLS/MP4 | ✅ Verificado |
| **After Rebirth, I Destroyed My Own Family** | `dt-after-rebirth-i-destroyed-my-own-family-5` | 15 / 15 | 15 eps | HLS/MP4 | ✅ Verificado |
| **After Rebirth, I Destroyed My Own Family** | `dt-after-rebirth-i-destroyed-my-own-family-6` | 15 / 15 | 15 eps | HLS/MP4 | ✅ Verificado |
| **After Rebirth, My Sister Stole My Wedding** | `dt-after-rebirth-my-sister-stole-my-wedding-3` | 70 / 70 | 70 eps | HLS/MP4 | ✅ Verificado |
| **After Rebirth, We Both Remember** | `dt-after-rebirth-we-both-remember-3` | 70 / 70 | 70 eps | HLS/MP4 | ✅ Verificado |
| **After Rebirth, We Both Remember** | `dt-after-rebirth-we-both-remember-4` | 70 / 70 | 70 eps | HLS/MP4 | ✅ Verificado |
| **After returning from cosmetic surgery, I snatched her life in return** | `dt-after-returning-from-cosmetic-surgery-i-snatched-her-life-in-return-4` | 72 / 72 | 72 eps | HLS/MP4 | ✅ Verificado |
| **After returning from cosmetic surgery, I snatched her life in return** | `dt-after-returning-from-cosmetic-surgery-i-snatched-her-life-in-return-5` | 72 / 72 | 72 eps | HLS/MP4 | ✅ Verificado |
| **After She Walked Away** | `dt-after-she-walked-away` | 100 / 100 | 100 eps | HLS/MP4 | ✅ Verificado |
| **After Smashing My Con-Artist Ex, I Married a Billionaire Tycoon** | `dt-after-smashing-my-con-artist-ex-i-married-a-billionaire-tycoon-4` | 60 / 60 | 60 eps | HLS/MP4 | ✅ Verificado |
| **After Storming the Imperial City, She Told Me to Retreat** | `dt-after-storming-the-imperial-city-she-told-me-to-retreat` | 70 / 70 | 70 eps | HLS/MP4 | ✅ Verificado |
| **After successfully chasing his wife, he showed his trum card** | `dt-after-successfully-chasing-his-wife-he-showed-his-trum-card` | 80 / 80 | 80 eps | HLS/MP4 | ✅ Verificado |
| **After successfully chasing his wife, he showed his trum card** | `dt-after-successfully-chasing-his-wife-he-showed-his-trum-card-2` | 80 / 80 | 80 eps | HLS/MP4 | ✅ Verificado |
| **After successfully chasing his wife, he showed his trum card** | `dt-after-successfully-chasing-his-wife-he-showed-his-trum-card-3` | 80 / 80 | 80 eps | HLS/MP4 | ✅ Verificado |
| **After successfully chasing his wife, he showed his trum card** | `dt-after-successfully-chasing-his-wife-he-showed-his-trum-card-4` | 51 / 51 | 51 eps | HLS/MP4 | ✅ Verificado |
| **After successfully chasing his wife, he showed his trum card** | `dt-after-successfully-chasing-his-wife-he-showed-his-trum-card-5` | 76 / 76 | 76 eps | HLS/MP4 | ✅ Verificado |
| **After successfully chasing his wife, he showed his trum card** | `dt-after-successfully-chasing-his-wife-he-showed-his-trum-card-6` | 75 / 75 | 75 eps | HLS/MP4 | ✅ Verificado |
| **After successfully chasing his wife, he showed his trum card** | `dt-after-successfully-chasing-his-wife-he-showed-his-trum-card-7` | 46 / 46 | 46 eps | HLS/MP4 | ✅ Verificado |
| **After successfully chasing his wife, he showed his trum card** | `dt-after-successfully-chasing-his-wife-he-showed-his-trum-card-8` | 39 / 39 | 39 eps | HLS/MP4 | ✅ Verificado |
| **After surviving a crash landing,an astronant return home to catch her husband cheating with his mistress.** | `dt-after-surviving-a-crash-landing-an-astronant-return-home-to-catch-her-husband-cheating-with-his-mistress-2` | 8 / 8 | 8 eps | HLS/MP4 | ✅ Verificado |
| **After Switched Fiancé, I Married a Mafia Boss** | `dt-after-switched-fiance-i-married-a-mafia-boss` | 56 / 56 | 56 eps | HLS/MP4 | ✅ Verificado |
| **After Switching Husbands, I Become A Junkyard Billionaire's Wife** | `dt-after-switching-husbands-i-become-a-junkyard-billionaires-wife` | 41 / 41 | 41 eps | HLS/MP4 | ✅ Verificado |
| **After Taking My Sister’s Place, I Destroy The Wealthy Clan** | `dt-after-taking-my-sisters-place-i-destroy-the-wealthy-clan-2` | 53 / 53 | 53 eps | HLS/MP4 | ✅ Verificado |
| **After Tearing Up the Blood Contract, the Arrogant Alpha Lost His Mind** | `dt-after-tearing-up-the-blood-contract-the-arrogant-alpha-lost-his-mind-3` | 69 / 69 | 69 eps | HLS/MP4 | ✅ Verificado |
| **After Tearing Up the Blood Contract, the Arrogant Alpha Lost His Mind** | `dt-after-tearing-up-the-blood-contract-the-arrogant-alpha-lost-his-mind-4` | 11 / 11 | 11 eps | HLS/MP4 | ✅ Verificado |
| **After tearing up the marriage contract, the former partner from the past life went mad with regret** | `dt-after-tearing-up-the-marriage-contract-the-former-partner-from-the-past-life-went-mad-with-regret-3` | 32 / 32 | 32 eps | HLS/MP4 | ✅ Verificado |
| **After the Brink: My Comeback as a Top Lawyer** | `dt-after-the-brink-my-comeback-as-a-top-lawyer-3` | 46 / 46 | 46 eps | HLS/MP4 | ✅ Verificado |
| **After the disabled and abandoned girl was released from prison,I overturned the powerful family** | `dt-after-the-disabled-and-abandoned-girl-was-released-from-prison-i-overturned-the-powerful-family-2` | 60 / 60 | 60 eps | HLS/MP4 | ✅ Verificado |
| **After the Divorce** | `dt-after-the-divorce` | 70 / 70 | 70 eps | HLS/MP4 | ✅ Verificado |
| **After the divorce, I became a top rich man** | `dt-after-the-divorce-i-became-a-top-rich-man` | 44 / 44 | 44 eps | HLS/MP4 | ✅ Verificado |
| **After the Divorce, My Three Sons Treat Me Like Royalty** | `dt-after-the-divorce-my-three-sons-treat-me-like-royalty` | 17 / 17 | 17 eps | HLS/MP4 | ✅ Verificado |
| **After the Divorce,The Heiress Strikes Back** | `dt-after-the-divorce-the-heiress-strikes-back` | 50 / 50 | 50 eps | HLS/MP4 | ✅ Verificado |
| **After the divorce, the mafia boss stopped pretending** | `dt-after-the-divorce-the-mafia-boss-stopped-pretending-3` | 15 / 15 | 15 eps | HLS/MP4 | ✅ Verificado |
| **After the heart exchange, the captain knelt and begged me to remarry** | `dt-after-the-heart-exchange-the-captain-knelt-and-begged-me-to-remarry-3` | 60 / 60 | 60 eps | HLS/MP4 | ✅ Verificado |
| **After the heart exchange, the captain knelt and begged me to remarry** | `dt-after-the-heart-exchange-the-captain-knelt-and-begged-me-to-remarry-4` | 60 / 60 | 60 eps | HLS/MP4 | ✅ Verificado |
| **After the Hospital,Into Their Regret** | `dt-after-the-hospital-into-their-regret` | 61 / 61 | 61 eps | HLS/MP4 | ✅ Verificado |
| **After the Hospital,Into Their Regret** | `dt-after-the-hospital-into-their-regret-2` | 58 / 58 | 58 eps | HLS/MP4 | ✅ Verificado |
| **After the Hospital,Into Their Regret** | `dt-after-the-hospital-into-their-regret-3` | 81 / 81 | 81 eps | HLS/MP4 | ✅ Verificado |
| **After the Hospital,Into Their Regret** | `dt-after-the-hospital-into-their-regret-4` | 79 / 79 | 79 eps | HLS/MP4 | ✅ Verificado |
| **After the Hospital,Into Their Regret** | `dt-after-the-hospital-into-their-regret-5` | 81 / 81 | 81 eps | HLS/MP4 | ✅ Verificado |
| **After the Prince Fell for My Cousin, I Married the Crown Prince of a Neighboring Kingdom** | `dt-after-the-prince-fell-for-my-cousin-i-married-the-crown-prince-of-a-neighboring-kingdom` | 40 / 40 | 40 eps | HLS/MP4 | ✅ Verificado |
| **AFTER THE RETURN OF THE REAL DAUGHTER** | `dt-after-the-return-of-the-real-daughter` | 84 / 84 | 84 eps | HLS/MP4 | ✅ Verificado |
| **After The Substitute:Mr.Shen's Descent into Madness (Dubbed)** | `dt-after-the-substitute-mr-shen-s-descent-into-madness` | 100 / 100 | 100 eps | HLS/MP4 | ✅ Verificado |
| **After They Broke My Sister** | `dt-after-they-broke-my-sister` | 10 / 10 | 10 eps | HLS/MP4 | ✅ Verificado |
| **AFTER YEARS TOGETHER, MERE STRANGERS** | `dt-after-years-together-mere-strangers-3` | 56 / 56 | 56 eps | HLS/MP4 | ✅ Verificado |
| **AFTER YEARS TOGETHER, MERE STRANGERS** | `dt-after-years-together-mere-strangers-4` | 41 / 41 | 41 eps | HLS/MP4 | ✅ Verificado |
| **AFTER YEARS TOGETHER, MERE STRANGERS** | `dt-after-years-together-mere-strangers-5` | 50 / 50 | 50 eps | HLS/MP4 | ✅ Verificado |
| **AFTER YEARS TOGETHER, MERE STRANGERS** | `dt-after-years-together-mere-strangers-6` | 60 / 60 | 60 eps | HLS/MP4 | ✅ Verificado |
| **AFTER YEARS TOGETHER, MERE STRANGERS** | `dt-after-years-together-mere-strangers-7` | 46 / 46 | 46 eps | HLS/MP4 | ✅ Verificado |
| **AFTER YEARS TOGETHER, MERE STRANGERS** | `dt-after-years-together-mere-strangers-8` | 29 / 29 | 29 eps | HLS/MP4 | ✅ Verificado |
| **AFTEREXPOSING MYIDENTITY,MYEX-HUSBAND REGRETS IT ROYALLY** | `dt-afterexposing-myidentity-myex-husband-regrets-it-royally` | 23 / 23 | 23 eps | HLS/MP4 | ✅ Verificado |
| **AFTEREXPOSING MYIDENTITY,MYEX-HUSBAND REGRETS IT ROYALLY** | `dt-afterexposing-myidentity-myex-husband-regrets-it-royally-2` | 17 / 17 | 17 eps | HLS/MP4 | ✅ Verificado |
| **AFTEREXPOSING MYIDENTITY,MYEX-HUSBAND REGRETS IT ROYALLY** | `dt-afterexposing-myidentity-myex-husband-regrets-it-royally-3` | 52 / 52 | 52 eps | HLS/MP4 | ✅ Verificado |
| **AFTEREXPOSING MYIDENTITY,MYEX-HUSBAND REGRETS IT ROYALLY** | `dt-afterexposing-myidentity-myex-husband-regrets-it-royally-4` | 52 / 52 | 52 eps | HLS/MP4 | ✅ Verificado |
| **AFTEREXPOSING MYIDENTITY,MYEX-HUSBAND REGRETS IT ROYALLY** | `dt-afterexposing-myidentity-myex-husband-regrets-it-royally-5` | 51 / 51 | 51 eps | HLS/MP4 | ✅ Verificado |
| **AFTEREXPOSING MYIDENTITY,MYEX-HUSBAND REGRETS IT ROYALLY** | `dt-afterexposing-myidentity-myex-husband-regrets-it-royally-6` | 41 / 41 | 41 eps | HLS/MP4 | ✅ Verificado |
| **AFTEREXPOSING MYIDENTITY,MYEX-HUSBAND REGRETS IT ROYALLY** | `dt-afterexposing-myidentity-myex-husband-regrets-it-royally-7` | 27 / 27 | 27 eps | HLS/MP4 | ✅ Verificado |
| **AFTEREXPOSING MYIDENTITY,MYEX-HUSBAND REGRETS IT ROYALLY** | `dt-afterexposing-myidentity-myex-husband-regrets-it-royally-8` | 17 / 17 | 17 eps | HLS/MP4 | ✅ Verificado |
| **AFTEREXPOSING MYIDENTITY,MYEX-HUSBAND REGRETS IT ROYALLY** | `dt-afterexposing-myidentity-myex-husband-regrets-it-royally-9` | 52 / 52 | 52 eps | HLS/MP4 | ✅ Verificado |
| **Aftershock: Fall of Civilization** | `dt-aftershock-fall-of-civilization` | 6 / 6 | 6 eps | HLS/MP4 | ✅ Verificado |
| **Against All Odds** | `dt-against-all-odds` | 59 / 59 | 59 eps | HLS/MP4 | ✅ Verificado |
| **Against His Sky** | `dt-against-his-sky-3` | 15 / 15 | 15 eps | HLS/MP4 | ✅ Verificado |
| **Against His Sky** | `dt-against-his-sky-4` | 15 / 15 | 15 eps | HLS/MP4 | ✅ Verificado |
| **Against His Sky** | `dt-against-his-sky-5` | 15 / 15 | 15 eps | HLS/MP4 | ✅ Verificado |
| **Against the Crown: A Widow's Retribution** | `dt-against-the-crown-a-widow-s-retribution` | 59 / 59 | 59 eps | HLS/MP4 | ✅ Verificado |
| **Against the Light, Together** | `dt-against-the-light-together-3` | 59 / 59 | 59 eps | HLS/MP4 | ✅ Verificado |
| **Against the Light, Together** | `dt-against-the-light-together-4` | 59 / 59 | 59 eps | HLS/MP4 | ✅ Verificado |
| **Against the Light, Together** | `dt-against-the-light-together-5` | 57 / 57 | 57 eps | HLS/MP4 | ✅ Verificado |
| **Against the Light, Together** | `dt-against-the-light-together-6` | 59 / 59 | 59 eps | HLS/MP4 | ✅ Verificado |
| **Against the Light, Together** | `dt-against-the-light-together-7` | 59 / 59 | 59 eps | HLS/MP4 | ✅ Verificado |
| **Agents' Undercovered Love** | `dt-agents-undercovered-love-2` | 53 / 53 | 53 eps | HLS/MP4 | ✅ Verificado |
| **Agreement No. 11** | `dt-agreement-no-11` | 16 / 16 | 16 eps | HLS/MP4 | ✅ Verificado |
| **Alert! Mrs. Jackson Dating Someone Again (Dubbed)** | `dt-alert-mrs-jackson-dating-someone-again` | 77 / 77 | 77 eps | HLS/MP4 | ✅ Verificado |
| **Alfa's Beloved Wife** | `dt-alfas-beloved-wife` | 11 / 11 | 11 eps | HLS/MP4 | ✅ Verificado |
| **The Deadly Game I Control** | `dt-all-hail-my-deadly-game` | 40 / 40 | 40 eps | HLS/MP4 | ✅ Verificado |
| **All I Wanted… Was a Place to Belong** | `dt-all-i-wanted-was-a-place-to-belong` | 21 / 21 | 21 eps | HLS/MP4 | ✅ Verificado |
| **All My Love Was Wasted** | `dt-all-my-love-was-wasted` | 40 / 40 | 40 eps | HLS/MP4 | ✅ Verificado |
| **All of the Entertainment Circle is Waiting for Us to Get Divorced** | `dt-all-of-the-entertainment-circle-is-waiting-for-us-to-get-divorced` | 75 / 75 | 75 eps | HLS/MP4 | ✅ Verificado |
| **All right, I am the heir of the billionaire** | `dt-all-right-i-am-the-heir-of-the-billionaire` | 58 / 58 | 58 eps | HLS/MP4 | ✅ Verificado |
| **All Too Late** | `dt-all-too-late` | 80 / 80 | 80 eps | HLS/MP4 | ✅ Verificado |
| **All You Need Is Love** | `dt-all-you-need-is-love` | 58 / 58 | 58 eps | HLS/MP4 | ✅ Verificado |
| **Almighty** | `dt-almighty` | 87 / 87 | 87 eps | HLS/MP4 | ✅ Verificado |
| **Alpha Daddy, I Found Mommy** | `dt-alpha-daddy-i-found-mommy-2` | 7 / 7 | 7 eps | HLS/MP4 | ✅ Verificado |
| **Alpha Hayley's Destined Mate** | `dt-alpha-hayleys-destined-mate` | 79 / 79 | 79 eps | HLS/MP4 | ✅ Verificado |
| **Alpha, I'm a Vampire** | `dt-alpha-im-a-vampire` | 14 / 14 | 14 eps | HLS/MP4 | ✅ Verificado |
| **Alpha of My Heart** | `dt-alpha-of-my-heart-2` | 35 / 35 | 35 eps | HLS/MP4 | ✅ Verificado |
| **Alpha of Shadows: The Queen Returns** | `dt-alpha-of-shadows-the-queen-returns-3` | 52 / 52 | 52 eps | HLS/MP4 | ✅ Verificado |
| **Alpha, Please Mark Me** | `dt-alpha-please-mark-me` | 73 / 73 | 73 eps | HLS/MP4 | ✅ Verificado |
| **Alpha’s Fake or Fated Mate** | `dt-alpha-s-fake-or-fated-mate` | 47 / 47 | 47 eps | HLS/MP4 | ✅ Verificado |
| **Alpha, She Wasn't the One** | `dt-alpha-she-wasnt-the-one` | 70 / 70 | 70 eps | HLS/MP4 | ✅ Verificado |
| **Alpha's Abandoned Luna** | `dt-alphas-abandoned-luna` | 36 / 36 | 36 eps | HLS/MP4 | ✅ Verificado |
| **Alpha's Captive Mate** | `dt-alphas-captive-mate-2` | 24 / 24 | 24 eps | HLS/MP4 | ✅ Verificado |
| **Alpha's Fated Captive** | `dt-alphas-fated-captive-3` | 77 / 77 | 77 eps | HLS/MP4 | ✅ Verificado |
| **Alpha's Fated Love** | `dt-alphas-fated-love` | 6 / 6 | 6 eps | HLS/MP4 | ✅ Verificado |
| **Alpha's Hidden Luna** | `dt-alphas-hidden-luna` | 12 / 12 | 12 eps | HLS/MP4 | ✅ Verificado |
| **Alpha's Unwanted Bride: Moonlit Contract** | `dt-alphas-unwanted-bride-moonlit-contract` | 19 / 19 | 19 eps | HLS/MP4 | ✅ Verificado |
| **Alpha's Vampire Pet** | `dt-alphas-vampire-pet` | 5 / 5 | 5 eps | HLS/MP4 | ✅ Verificado |
| **Altarboy** | `dt-altarboy` | 63 / 63 | 63 eps | HLS/MP4 | ✅ Verificado |
| **Always picking her, so why cry when I leave?** | `dt-always-picking-her-so-why-cry-when-i-leave-2` | 62 / 62 | 62 eps | HLS/MP4 | ✅ Verificado |
| **Always picking her, so why cry when I leave?** | `dt-always-picking-her-so-why-cry-when-i-leave-3` | 62 / 62 | 62 eps | HLS/MP4 | ✅ Verificado |
| **Always picking her, so why cry when I leave?** | `dt-always-picking-her-so-why-cry-when-i-leave-6` | 62 / 62 | 62 eps | HLS/MP4 | ✅ Verificado |
| **American Flame** | `dt-american-flame` | 21 / 21 | 21 eps | HLS/MP4 | ✅ Verificado |
| **American Sniper: The Last Round** | `dt-american-sniper-the-last-round` | 63 / 63 | 63 eps | HLS/MP4 | ✅ Verificado |
| **Amnesiac CEO Husband** | `dt-amnesiac-ceo-husband` | 79 / 79 | 79 eps | HLS/MP4 | ✅ Verificado |
| **An ancient Titan is sealed within my body** | `dt-an-ancient-titan-is-sealed-within-my-body-3` | 96 / 96 | 96 eps | HLS/MP4 | ✅ Verificado |
| **An Archmage in the City** | `dt-an-archmage-in-the-city` | 53 / 53 | 53 eps | HLS/MP4 | ✅ Verificado |
| **An Ocean of Stars Between Us** | `dt-an-ocean-of-stars-between-us` | 55 / 55 | 55 eps | HLS/MP4 | ✅ Verificado |
| **Andrologist: His condition only manifests in me.** | `dt-andrologist-his-condition-only-manifests-in-me` | 78 / 78 | 78 eps | HLS/MP4 | ✅ Verificado |
| **Andrologist: His condition only manifests in me.** | `dt-andrologist-his-condition-only-manifests-in-me-2` | 78 / 78 | 78 eps | HLS/MP4 | ✅ Verificado |
| **Andrologist: His condition only manifests in me.** | `dt-andrologist-his-condition-only-manifests-in-me-3` | 62 / 62 | 62 eps | HLS/MP4 | ✅ Verificado |
| **Andrologist: His condition only manifests in me.** | `dt-andrologist-his-condition-only-manifests-in-me-4` | 78 / 78 | 78 eps | HLS/MP4 | ✅ Verificado |
| **Another Appointment by Mrs. Gu (Dubbed)** | `dt-another-appointment-by-mrs-gu` | 66 / 66 | 66 eps | HLS/MP4 | ✅ Verificado |
| **Ant, Evolved (Dubbed)** | `dt-ant-evolved` | 53 / 53 | 53 eps | HLS/MP4 | ✅ Verificado |
| **Antarctic Fortress** | `dt-antarctic-fortress` | 42 / 42 | 42 eps | HLS/MP4 | ✅ Verificado |
| **​Anti-Drama Family Restaurant** | `dt-anti-drama-family-restaurant` | 83 / 83 | 83 eps | HLS/MP4 | ✅ Verificado |
| **Apex Instinct** | `dt-apex-instinct` | 17 / 17 | 17 eps | HLS/MP4 | ✅ Verificado |
| **Apocalypse Boss: My Employees are S-Rank Mutants Season 2** | `dt-apocalypse-boss-my-employees-are-s-rank-mutants-season-2` | 57 / 57 | 57 eps | HLS/MP4 | ✅ Verificado |
| **Apocalypse Hotel** | `dt-apocalypse-hotel` | 77 / 77 | 77 eps | HLS/MP4 | ✅ Verificado |
| **Apocalypse Mother: Protecte My Girl at All Costs** | `dt-apocalypse-mother-protecte-my-girl-at-all-costs` | 30 / 30 | 30 eps | HLS/MP4 | ✅ Verificado |
| **Apocalypse: My Infinite RV Upgrade (Dubbed)** | `dt-apocalypse-my-infinite-rv-upgrade-2` | 32 / 32 | 32 eps | HLS/MP4 | ✅ Verificado |
| **Apocalypse Reborn: Kill Ex & Security Guard** | `dt-apocalypse-reborn-kill-ex-security-guard` | 18 / 18 | 18 eps | HLS/MP4 | ✅ Verificado |
| **Apocalypse Reborn: The Power Alliance** | `dt-apocalypse-reborn-the-power-alliance` | 16 / 16 | 16 eps | HLS/MP4 | ✅ Verificado |
| **Apocalypse Reborn: The World’s Savior** | `dt-apocalypse-reborn-the-worlds-savior` | 70 / 70 | 70 eps | HLS/MP4 | ✅ Verificado |
| **Apocalypse Reckoning: Road to Revenge** | `dt-apocalypse-reckoning-road-to-revenge` | 45 / 45 | 45 eps | HLS/MP4 | ✅ Verificado |
| **Apocalypse Survival Code** | `dt-apocalypse-survival-code` | 55 / 55 | 55 eps | HLS/MP4 | ✅ Verificado |
| **Apocalypse: The Zombie Queen is My Mom** | `dt-apocalypse-the-zombie-queen-is-my-mom` | 5 / 5 | 5 eps | HLS/MP4 | ✅ Verificado |
| **Apocalyptic Pet Shop II** | `dt-apocalyptic-pet-shop-ii` | 37 / 37 | 37 eps | HLS/MP4 | ✅ Verificado |
| **Apocalyptic Rebirth:Starting from Zero** | `dt-apocalyptic-rebirth-starting-from-zero` | 37 / 37 | 37 eps | HLS/MP4 | ✅ Verificado |
| **Ark of Revenge: A Ruthless Rebirth in the Apocalypse** | `dt-ark-of-revenge-a-ruthless-rebirth-in-the-apocalypse` | 38 / 38 | 38 eps | HLS/MP4 | ✅ Verificado |
| **Armor and Rouge** | `dt-armor-and-rouge` | 9 / 9 | 9 eps | HLS/MP4 | ✅ Verificado |
| **Arresting My Husband & Twin in Bed** | `dt-arresting-my-husband-twin-in-bed` | 50 / 50 | 50 eps | HLS/MP4 | ✅ Verificado |
| **As Hell,As Her** | `dt-as-hell-as-her` | 60 / 60 | 60 eps | HLS/MP4 | ✅ Verificado |
| **As Hell,As Her** | `dt-as-hell-as-her-2` | 60 / 60 | 60 eps | HLS/MP4 | ✅ Verificado |
| **As Hell,As Her** | `dt-as-hell-as-her-3` | 58 / 58 | 58 eps | HLS/MP4 | ✅ Verificado |
| **As Hell,As Her** | `dt-as-hell-as-her-4` | 60 / 60 | 60 eps | HLS/MP4 | ✅ Verificado |
| **Ascendance of the Unwanted Husband** | `dt-ascendance-of-the-unwanted-husband` | 78 / 78 | 78 eps | HLS/MP4 | ✅ Verificado |
| **Ascension of the Rebellious Consort** | `dt-ascension-of-the-rebellious-consort` | 76 / 76 | 76 eps | HLS/MP4 | ✅ Verificado |
| **Ascension Today (Dubbed)** | `dt-ascension-today-3` | 36 / 36 | 36 eps | HLS/MP4 | ✅ Verificado |
| **Ashes of a Silent Love** | `dt-ashes-of-a-silent-love` | 106 / 106 | 106 eps | HLS/MP4 | ✅ Verificado |
| **Ashes of a Silent Love** | `dt-ashes-of-a-silent-love-2` | 106 / 106 | 106 eps | HLS/MP4 | ✅ Verificado |
| **Ashes of Blackgate: The Detective's Claim** | `dt-ashes-of-blackgate-the-detectives-claim-2` | 50 / 50 | 50 eps | HLS/MP4 | ✅ Verificado |
| **Ashes of My Wedding Dress Rise of a Mafia Boss** | `dt-ashes-of-my-wedding-dress-rise-of-a-mafia-boss-2` | 42 / 42 | 42 eps | HLS/MP4 | ✅ Verificado |
| **Ashes to Honor (Dubbed)** | `dt-ashes-to-honor` | 36 / 36 | 36 eps | HLS/MP4 | ✅ Verificado |
| **Asset Lockdown: A Mother's Trillion-Dollar Revenge** | `dt-asset-lockdown-a-mothers-trillion-dollar-revenge-3` | 48 / 48 | 48 eps | HLS/MP4 | ✅ Verificado |
| **At The End of The Night Is The Warmth of The Sun** | `dt-at-the-end-of-the-night-is-the-warmth-of-the-sun` | 44 / 44 | 44 eps | HLS/MP4 | ✅ Verificado |
| **At The End of The Night Is The Warmth of The Sun** | `dt-at-the-end-of-the-night-is-the-warmth-of-the-sun-2` | 50 / 50 | 50 eps | HLS/MP4 | ✅ Verificado |
| **At The End of The Night Is The Warmth of The Sun** | `dt-at-the-end-of-the-night-is-the-warmth-of-the-sun-3` | 50 / 50 | 50 eps | HLS/MP4 | ✅ Verificado |
| **At The End of The Night Is The Warmth of The Sun** | `dt-at-the-end-of-the-night-is-the-warmth-of-the-sun-4` | 47 / 47 | 47 eps | HLS/MP4 | ✅ Verificado |
| **At The End of The Night Is The Warmth of The Sun** | `dt-at-the-end-of-the-night-is-the-warmth-of-the-sun-5` | 27 / 27 | 27 eps | HLS/MP4 | ✅ Verificado |
| **At The End of The Night Is The Warmth of The Sun** | `dt-at-the-end-of-the-night-is-the-warmth-of-the-sun-6` | 25 / 25 | 25 eps | HLS/MP4 | ✅ Verificado |
| **At the wedding, the husband passionately sang his white moonlight** | `dt-at-the-wedding-the-husband-passionately-sang-his-white-moonlight` | 21 / 21 | 21 eps | HLS/MP4 | ✅ Verificado |
| **At the wedding, the husband passionately sang his white moonlight** | `dt-at-the-wedding-the-husband-passionately-sang-his-white-moonlight-2` | 30 / 30 | 30 eps | HLS/MP4 | ✅ Verificado |
| **At the wedding, the husband passionately sang his white moonlight** | `dt-at-the-wedding-the-husband-passionately-sang-his-white-moonlight-3` | 30 / 30 | 30 eps | HLS/MP4 | ✅ Verificado |
| **At the wedding, the husband passionately sang his white moonlight** | `dt-at-the-wedding-the-husband-passionately-sang-his-white-moonlight-4` | 30 / 30 | 30 eps | HLS/MP4 | ✅ Verificado |
| **At the wedding, the husband passionately sang his white moonlight** | `dt-at-the-wedding-the-husband-passionately-sang-his-white-moonlight-5` | 30 / 30 | 30 eps | HLS/MP4 | ✅ Verificado |
| **At the wedding, the husband passionately sang his white moonlight** | `dt-at-the-wedding-the-husband-passionately-sang-his-white-moonlight-6` | 30 / 30 | 30 eps | HLS/MP4 | ✅ Verificado |
| **Athena’s Return: The Fall of Olympus** | `dt-athenas-return-the-fall-of-olympus-2` | 60 / 60 | 60 eps | HLS/MP4 | ✅ Verificado |
| **Atlante’s Mistaken Fiancée** | `dt-atlantes-mistaken-fiancee-2` | 82 / 82 | 82 eps | HLS/MP4 | ✅ Verificado |
| **ATM Transfer Rrecord** | `dt-atm-transfer-rrecord` | 35 / 35 | 35 eps | HLS/MP4 | ✅ Verificado |
| **Auction Of Lies** | `dt-auction-of-lies-2` | 31 / 31 | 31 eps | HLS/MP4 | ✅ Verificado |
| **Aurora: The Rejected Empress** | `dt-aurora-the-rejected-empress` | 27 / 27 | 27 eps | HLS/MP4 | ✅ Verificado |
| **Aviation Empire: Scorned Wife Takes Control** | `dt-aviation-empire-scorned-wife-takes-control` | 15 / 15 | 15 eps | HLS/MP4 | ✅ Verificado |
| **Aviation Empire: Scorned Wife Takes Control** | `dt-aviation-empire-scorned-wife-takes-control-2` | 15 / 15 | 15 eps | HLS/MP4 | ✅ Verificado |
| **Aviation Empire: Scorned Wife Takes Control** | `dt-aviation-empire-scorned-wife-takes-control-3` | 15 / 15 | 15 eps | HLS/MP4 | ✅ Verificado |
| **Aviation Empire: Scorned Wife Takes Control** | `dt-aviation-empire-scorned-wife-takes-control-4` | 15 / 15 | 15 eps | HLS/MP4 | ✅ Verificado |
| **Aviation Revenge: From Broke to Ruler** | `dt-aviation-revenge-from-broke-to-ruler` | 15 / 15 | 15 eps | HLS/MP4 | ✅ Verificado |
| **Aviation Revenge: From Broke to Ruler** | `dt-aviation-revenge-from-broke-to-ruler-2` | 15 / 15 | 15 eps | HLS/MP4 | ✅ Verificado |
| **Aviation Revenge: From Broke to Ruler** | `dt-aviation-revenge-from-broke-to-ruler-3` | 15 / 15 | 15 eps | HLS/MP4 | ✅ Verificado |
| **Aviation Temptation: Undercover Lover's Revenge Game** | `dt-aviation-temptation-undercover-lovers-revenge-game-2` | 63 / 63 | 63 eps | HLS/MP4 | ✅ Verificado |
| **Aviation Temptation: Undercover Lover's Revenge Game** | `dt-aviation-temptation-undercover-lovers-revenge-game-3` | 68 / 68 | 68 eps | HLS/MP4 | ✅ Verificado |
| **Aviation Temptation: Undercover Lover's Revenge Game** | `dt-aviation-temptation-undercover-lovers-revenge-game-4` | 52 / 52 | 52 eps | HLS/MP4 | ✅ Verificado |
| **Awakened Housewife:THE LAWYER HUSBAND LOST HIS MIND** | `dt-awakened-housewife-the-lawyer-husband-lost-his-mind-3` | 60 / 60 | 60 eps | HLS/MP4 | ✅ Verificado |
| **Awakened Housewife:THE LAWYER HUSBAND LOST HIS MIND** | `dt-awakened-housewife-the-lawyer-husband-lost-his-mind-4` | 60 / 60 | 60 eps | HLS/MP4 | ✅ Verificado |
| **Awakened: Mafia Queen** | `dt-awakened-mafia-queen` | 45 / 45 | 45 eps | HLS/MP4 | ✅ Verificado |
| **Too Late to Judge (Dubbed)** | `dt-awakening-2` | 50 / 50 | 50 eps | HLS/MP4 | ✅ Verificado |
| **Awakening of the Plain Girl** | `dt-awakening-of-the-plain-girl` | 5 / 5 | 5 eps | HLS/MP4 | ✅ Verificado |
| **AWAKENING: SPEED META BODYGUARD** | `dt-awakening-speed-meta-bodyguard-3` | 35 / 35 | 35 eps | HLS/MP4 | ✅ Verificado |
| **AWAKENING: SPEED META BODYGUARD** | `dt-awakening-speed-meta-bodyguard-4` | 58 / 58 | 58 eps | HLS/MP4 | ✅ Verificado |
| **AWAKENING: SPEED META BODYGUARD** | `dt-awakening-speed-meta-bodyguard-5` | 38 / 38 | 38 eps | HLS/MP4 | ✅ Verificado |
| **AWAKENING: SPEED META BODYGUARD** | `dt-awakening-speed-meta-bodyguard-6` | 60 / 60 | 60 eps | HLS/MP4 | ✅ Verificado |
| **Awakening the Forgotten Gods** | `dt-awakening-the-forgotten-gods` | 68 / 68 | 68 eps | HLS/MP4 | ✅ Verificado |
| **Away from the Crown's Reach (Dubbed)** | `dt-away-from-the-crown-s-reach-2` | 28 / 28 | 28 eps | HLS/MP4 | ✅ Verificado |
| **Baby Betrayal** | `dt-baby-betrayal` | 10 / 10 | 10 eps | HLS/MP4 | ✅ Verificado |
| **Babymaking on Divorce Day** | `dt-babymaking-on-divorce-day` | 68 / 68 | 68 eps | HLS/MP4 | ✅ Verificado |
| **Baby's Secret Teach Mommy to Hook the Billionaire Tycoon** | `dt-babys-secret-teach-mommy-to-hook-the-billionaire-tycoon` | 30 / 30 | 30 eps | HLS/MP4 | ✅ Verificado |
| **Back at Eight: The Football Legend** | `dt-back-at-eight-the-football-legend` | 51 / 51 | 51 eps | HLS/MP4 | ✅ Verificado |
| **Back Before the Apocalypse** | `dt-back-before-the-apocalypse` | 30 / 30 | 30 eps | HLS/MP4 | ✅ Verificado |
| **Back for It All** | `dt-back-for-it-all` | 60 / 60 | 60 eps | HLS/MP4 | ✅ Verificado |
| **Back for It All** | `dt-back-for-it-all-2` | 60 / 60 | 60 eps | HLS/MP4 | ✅ Verificado |
| **Back for It All** | `dt-back-for-it-all-3` | 60 / 60 | 60 eps | HLS/MP4 | ✅ Verificado |
| **Back for It All** | `dt-back-for-it-all-6` | 60 / 60 | 60 eps | HLS/MP4 | ✅ Verificado |
| **Back for It All** | `dt-back-for-it-all-7` | 60 / 60 | 60 eps | HLS/MP4 | ✅ Verificado |
| **Back from Mars,Her Ex Regrets Everything!** | `dt-back-from-mars-her-ex-regrets-everything-3` | 40 / 40 | 40 eps | HLS/MP4 | ✅ Verificado |
| **Back from Mars,Her Ex Regrets Everything!** | `dt-back-from-mars-her-ex-regrets-everything-4` | 29 / 29 | 29 eps | HLS/MP4 | ✅ Verificado |
| **Back to 18: I'm Your Mother** | `dt-back-to-18-im-your-mother-2` | 60 / 60 | 60 eps | HLS/MP4 | ✅ Verificado |
| **Back to 18: I'm Your Mother** | `dt-back-to-18-im-your-mother-3` | 60 / 60 | 60 eps | HLS/MP4 | ✅ Verificado |
| **Back to 1983: A Second Chance at Fate (Dubbed)** | `dt-back-to-1983-a-second-chance-at-fate` | 62 / 62 | 62 eps | HLS/MP4 | ✅ Verificado |
| **Back to 1990:Smartphone Run the World** | `dt-back-to-1990-smartphone-run-the-world` | 50 / 50 | 50 eps | HLS/MP4 | ✅ Verificado |
| **Back to Ancient Times as a Duke** | `dt-back-to-ancient-times-as-a-duke` | 89 / 89 | 89 eps | HLS/MP4 | ✅ Verificado |
| **Back to Doomsday Eve** | `dt-back-to-doomsday-eve` | 37 / 37 | 37 eps | HLS/MP4 | ✅ Verificado |
| **Back to the 80s** | `dt-back-to-the-80s-3` | 59 / 59 | 59 eps | HLS/MP4 | ✅ Verificado |
| **Back to the Day We Met** | `dt-back-to-the-day-we-met` | 59 / 59 | 59 eps | HLS/MP4 | ✅ Verificado |
| **Back to Your Heart** | `dt-back-to-your-heart-4` | 32 / 32 | 32 eps | HLS/MP4 | ✅ Verificado |
| **Back With Baby, Ex Regrets Deeply** | `dt-back-with-baby-ex-regrets-deeply` | 70 / 70 | 70 eps | HLS/MP4 | ✅ Verificado |
| **Backdoor Brawler: The Unexpected Successor** | `dt-backdoor-brawler-the-unexpected-successor` | 41 / 41 | 41 eps | HLS/MP4 | ✅ Verificado |
| **Backstage Romance with the Popstar** | `dt-backstage-romance-with-the-popstar` | 63 / 63 | 63 eps | HLS/MP4 | ✅ Verificado |
| **Bad Boy Sleeps Next Door** | `dt-bad-boy-sleeps-next-door-6` | 15 / 15 | 15 eps | HLS/MP4 | ✅ Verificado |
| **Bad Sister** | `dt-bad-sister` | 36 / 36 | 36 eps | HLS/MP4 | ✅ Verificado |
| **Baiting with Her** | `dt-baiting-with-her` | 39 / 39 | 39 eps | HLS/MP4 | ✅ Verificado |
| **Banished After 500 Years** | `dt-banished-after-500-years` | 32 / 32 | 32 eps | HLS/MP4 | ✅ Verificado |
| **BANISHED BY THE QUEEN, I AM THE TRUE LORD OF SEAS** | `dt-banished-by-the-queen-i-am-the-true-lord-of-seas` | 69 / 69 | 69 eps | HLS/MP4 | ✅ Verificado |
| **Banished Daughter: Secrets of the Capital** | `dt-banished-daughter-secrets-of-the-capital` | 61 / 61 | 61 eps | HLS/MP4 | ✅ Verificado |
| **Bankrupt My Cheating Husband** | `dt-bankrupt-my-cheating-husband` | 18 / 18 | 18 eps | HLS/MP4 | ✅ Verificado |
| **Battle for Brilliance** | `dt-battle-for-brilliance-3` | 30 / 30 | 30 eps | HLS/MP4 | ✅ Verificado |
| **Battle for the Summit** | `dt-battle-for-the-summit` | 2 / 2 | 2 eps | HLS/MP4 | ✅ Verificado |
| **Be Her Billionaire Protector** | `dt-be-her-billionaire-protector` | 82 / 82 | 82 eps | HLS/MP4 | ✅ Verificado |
| **Be in Love with the Stunning President** | `dt-be-in-love-with-the-stunning-president` | 80 / 80 | 80 eps | HLS/MP4 | ✅ Verificado |
| **Be My Heart Be Your Eye** | `dt-be-my-heart-be-your-eye-2` | 56 / 56 | 56 eps | HLS/MP4 | ✅ Verificado |
| **Beach Volleyball Virgin** | `dt-beach-volleyball-virgin-4` | 51 / 51 | 51 eps | HLS/MP4 | ✅ Verificado |
| **Beast Soul Awakening: I Contracted a Six-Winged Angel** | `dt-beast-soul-awakening-i-contracted-a-six-winged-angel-2` | 40 / 40 | 40 eps | HLS/MP4 | ✅ Verificado |
| **Beastbound** | `dt-beastbound` | 29 / 29 | 29 eps | HLS/MP4 | ✅ Verificado |
| **Beastfall: The Dragon's System** | `dt-beastfall-the-dragons-system` | 51 / 51 | 51 eps | HLS/MP4 | ✅ Verificado |
| **Beastmate’s Vengeance: Serpent Reborn (Dubbed)** | `dt-beastmate-s-vengeance-serpent-reborn` | 52 / 52 | 52 eps | HLS/MP4 | ✅ Verificado |
| **BECAUSE OF A SHEEP,I MADE THE SCUM FIANCE REGRET IT** | `dt-because-of-a-sheep-i-made-the-scum-fiance-regret-it-3` | 40 / 40 | 40 eps | HLS/MP4 | ✅ Verificado |
| **Becoming a Queen in Vertical Screen Dramas** | `dt-becoming-a-queen-in-vertical-screen-dramas-2` | 50 / 50 | 50 eps | HLS/MP4 | ✅ Verificado |
| **Bedded and Buffed: Claiming My Shifter Harem** | `dt-bedded-and-buffed-claiming-my-shifter-harem` | 30 / 30 | 30 eps | HLS/MP4 | ✅ Verificado |
| **Bedroom Show, Living Room Trap** | `dt-bedroom-show-living-room-trap` | 45 / 45 | 45 eps | HLS/MP4 | ✅ Verificado |
| **Bedroom Show, Living Room Trap** | `dt-bedroom-show-living-room-trap-2` | 50 / 50 | 50 eps | HLS/MP4 | ✅ Verificado |
| **Bedroom Show, Living Room Trap** | `dt-bedroom-show-living-room-trap-4` | 33 / 33 | 33 eps | HLS/MP4 | ✅ Verificado |
| **Before the Wedding, My Husband Slept with Stepsister** | `dt-before-the-wedding-my-husband-slept-with-stepsister` | 10 / 10 | 10 eps | HLS/MP4 | ✅ Verificado |
| **Beg for my return after kicking me out** | `dt-beg-for-my-return-after-kicking-me-out-5` | 48 / 48 | 48 eps | HLS/MP4 | ✅ Verificado |
| **Beg the Wife You Threw Away** | `dt-beg-the-wife-you-threw-away` | 48 / 48 | 48 eps | HLS/MP4 | ✅ Verificado |
| **Begin Again with the rejected heiress** | `dt-begin-again-with-the-rejected-heiress-3` | 74 / 74 | 74 eps | HLS/MP4 | ✅ Verificado |
| **Behind Closed Doors** | `dt-behind-closed-doors-3` | 47 / 47 | 47 eps | HLS/MP4 | ✅ Verificado |
| **BEHIND CLOSED DOORS: The horror of Dubai's secret parties** | `dt-behind-closed-doors-the-horror-of-dubais-secret-parties` | 8 / 8 | 8 eps | HLS/MP4 | ✅ Verificado |
| **Behind the Lies - I Was Always His** | `dt-behind-the-lies-i-was-always-his` | 10 / 10 | 10 eps | HLS/MP4 | ✅ Verificado |
| **Behold!The Son of King Arthur is Back!** | `dt-behold-the-son-of-king-arthur-is-back` | 30 / 30 | 30 eps | HLS/MP4 | ✅ Verificado |
| **Belated Love** | `dt-belated-love-3` | 41 / 41 | 41 eps | HLS/MP4 | ✅ Verificado |
| **Beneath the White Coat** | `dt-beneath-the-white-coat-2` | 55 / 55 | 55 eps | HLS/MP4 | ✅ Verificado |
| **Best Friend's Betrayal** | `dt-best-friends-betrayal` | 44 / 44 | 44 eps | HLS/MP4 | ✅ Verificado |
| **BETRAYAL AND ROYAL ADORE** | `dt-betrayal-and-royal-adore-3` | 66 / 66 | 66 eps | HLS/MP4 | ✅ Verificado |
| **Betrayal by the Demon Lord** | `dt-betrayal-by-the-demon-lord` | 5 / 5 | 5 eps | HLS/MP4 | ✅ Verificado |
| **Betrayed Alpha Heiress: Return for the King** | `dt-betrayed-alpha-heiress-return-for-the-king` | 22 / 22 | 22 eps | HLS/MP4 | ✅ Verificado |
| **Betrayed Alpha Queen Rises from the Ashes** | `dt-betrayed-alpha-queen-rises-from-the-ashes` | 56 / 56 | 56 eps | HLS/MP4 | ✅ Verificado |
| **Betrayed by All: I Hold the Secret Wealth** | `dt-betrayed-by-all-i-hold-the-secret-wealth` | 11 / 11 | 11 eps | HLS/MP4 | ✅ Verificado |
| **Betrayed by her beloved she returns to reclaim everything** | `dt-betrayed-by-her-beloved-she-returns-to-reclaim-everything-3` | 15 / 15 | 15 eps | HLS/MP4 | ✅ Verificado |
| **Betrayed by Him, Reborn by Her** | `dt-betrayed-by-him-reborn-by-her-2` | 62 / 62 | 62 eps | HLS/MP4 | ✅ Verificado |
| **Betrayed BY LOVE, CHOSEN BY DESTINY** | `dt-betrayed-by-love-chosen-by-destiny-3` | 60 / 60 | 60 eps | HLS/MP4 | ✅ Verificado |
| **Betrayed BY LOVE, CHOSEN BY DESTINY** | `dt-betrayed-by-love-chosen-by-destiny-4` | 60 / 60 | 60 eps | HLS/MP4 | ✅ Verificado |
| **Betrayed BY LOVE, CHOSEN BY DESTINY** | `dt-betrayed-by-love-chosen-by-destiny-5` | 58 / 58 | 58 eps | HLS/MP4 | ✅ Verificado |
| **Betrayed by My Blood Brother** | `dt-betrayed-by-my-blood-brother` | 22 / 22 | 22 eps | HLS/MP4 | ✅ Verificado |
| **Betrayed by My Blood Brother** | `dt-betrayed-by-my-blood-brother-2` | 30 / 30 | 30 eps | HLS/MP4 | ✅ Verificado |
| **Betrayed By My Ex , Married To The Billionaire** | `dt-betrayed-by-my-ex-married-to-the-billionaire-3` | 67 / 67 | 67 eps | HLS/MP4 | ✅ Verificado |
| **Betrayed By My Ex , Married To The Billionaire** | `dt-betrayed-by-my-ex-married-to-the-billionaire-4` | 66 / 66 | 66 eps | HLS/MP4 | ✅ Verificado |
| **Betrayed By My Ex , Married To The Billionaire** | `dt-betrayed-by-my-ex-married-to-the-billionaire-5` | 57 / 57 | 57 eps | HLS/MP4 | ✅ Verificado |
| **Betrayed By My Ex , Married To The Billionaire** | `dt-betrayed-by-my-ex-married-to-the-billionaire-6` | 61 / 61 | 61 eps | HLS/MP4 | ✅ Verificado |
| **Betrayed by My Husband Claimed by a Billionaire** | `dt-betrayed-by-my-husband-claimed-by-a-billionaire-3` | 67 / 67 | 67 eps | HLS/MP4 | ✅ Verificado |
| **Betrayed By My Husband, I Took Revenge** | `dt-betrayed-by-my-husband-i-took-revenge-3` | 60 / 60 | 60 eps | HLS/MP4 | ✅ Verificado |
| **Betrayed By My Husband, I Took Revenge** | `dt-betrayed-by-my-husband-i-took-revenge-4` | 54 / 54 | 54 eps | HLS/MP4 | ✅ Verificado |
| **Betrayed by scum, Trise Asa Rich heiress** | `dt-betrayed-by-scum-trise-asa-rich-heiress-4` | 22 / 22 | 22 eps | HLS/MP4 | ✅ Verificado |
| **Betrayed by scum, Trise Asa Rich heiress** | `dt-betrayed-by-scum-trise-asa-rich-heiress-5` | 70 / 70 | 70 eps | HLS/MP4 | ✅ Verificado |
| **Betrayed by the Fleet Captain, I Rule as the Supreme Galactic Commander** | `dt-betrayed-by-the-fleet-captain-i-rule-as-the-supreme-galactic-commander-3` | 62 / 62 | 62 eps | HLS/MP4 | ✅ Verificado |
| **Betrayed by the Fleet Captain, I Rule as the Supreme Galactic Commander** | `dt-betrayed-by-the-fleet-captain-i-rule-as-the-supreme-galactic-commander-4` | 55 / 55 | 55 eps | HLS/MP4 | ✅ Verificado |
| **Betrayed by the Wolf King** | `dt-betrayed-by-the-wolf-king` | 10 / 10 | 10 eps | HLS/MP4 | ✅ Verificado |
| **Betrayed Her, They All Regret** | `dt-betrayed-her-they-all-regret` | 71 / 71 | 71 eps | HLS/MP4 | ✅ Verificado |
| **(Dubbed) Betrayed Him? Now They’ll Beg!** | `dt-betrayed-him-now-theyll-beg` | 70 / 70 | 70 eps | HLS/MP4 | ✅ Verificado |
| **BETRAYED ON THE PLANE** | `dt-betrayed-on-the-plane-3` | 71 / 71 | 71 eps | HLS/MP4 | ✅ Verificado |
| **BETRAYED ON THE PLANE** | `dt-betrayed-on-the-plane-4` | 57 / 57 | 57 eps | HLS/MP4 | ✅ Verificado |
| **BETRAYED ON THE PLANE** | `dt-betrayed-on-the-plane-5` | 71 / 71 | 71 eps | HLS/MP4 | ✅ Verificado |
| **BETRAYED ON THE PLANE** | `dt-betrayed-on-the-plane-6` | 68 / 68 | 68 eps | HLS/MP4 | ✅ Verificado |
| **BETRAYED ON THE PLANE** | `dt-betrayed-on-the-plane-7` | 45 / 45 | 45 eps | HLS/MP4 | ✅ Verificado |
| **BETRAYED ON THE PLANE** | `dt-betrayed-on-the-plane-8` | 48 / 48 | 48 eps | HLS/MP4 | ✅ Verificado |
| **BETRAYED ON THE PLANE** | `dt-betrayed-on-the-plane-9` | 77 / 77 | 77 eps | HLS/MP4 | ✅ Verificado |
| **Betrayed Reborn Betrothed to the Snake** | `dt-betrayed-reborn-betrothed-to-the-snake` | 20 / 20 | 20 eps | HLS/MP4 | ✅ Verificado |
| **Betrayed:She Fights Back** | `dt-betrayed-she-fights-back-3` | 11 / 11 | 11 eps | HLS/MP4 | ✅ Verificado |
| **Betrayed:She Fights Back** | `dt-betrayed-she-fights-back-4` | 15 / 15 | 15 eps | HLS/MP4 | ✅ Verificado |
| **Betrayed? Watch Her Flip the Board** | `dt-betrayed-watch-her-flip-the-board` | 49 / 49 | 49 eps | HLS/MP4 | ✅ Verificado |
| **Betraying the Fated Bond, the Alpha Regrets It** | `dt-betraying-the-fated-bond-the-alpha-regrets-it-2` | 60 / 60 | 60 eps | HLS/MP4 | ✅ Verificado |
| **Between the Monster and the Sea** | `dt-between-the-monster-and-the-sea` | 3 / 3 | 3 eps | HLS/MP4 | ✅ Verificado |
| **Between Two Crowns (Dubbed)** | `dt-between-two-crowns` | 43 / 43 | 43 eps | HLS/MP4 | ✅ Verificado |
| **Beyond Stars and Oceans** | `dt-beyond-stars-and-oceans` | 85 / 85 | 85 eps | HLS/MP4 | ✅ Verificado |
| **Beyond the Chemo: My Ruthless Revenge** | `dt-beyond-the-chemo-my-ruthless-revenge` | 39 / 39 | 39 eps | HLS/MP4 | ✅ Verificado |
| **BID FAREWELL TO INFERIOR EX-HUSBAND, WELCOME TOP-TIER NEW LOVER** | `dt-bid-farewell-to-inferior-ex-husband-welcome-top-tier-new-lover-3` | 74 / 74 | 74 eps | HLS/MP4 | ✅ Verificado |
| **BID FAREWELL TO INFERIOR EX-HUSBAND, WELCOME TOP-TIER NEW LOVER** | `dt-bid-farewell-to-inferior-ex-husband-welcome-top-tier-new-lover-4` | 66 / 66 | 66 eps | HLS/MP4 | ✅ Verificado |
| **BID FAREWELL TO INFERIOR EX-HUSBAND, WELCOME TOP-TIER NEW LOVER** | `dt-bid-farewell-to-inferior-ex-husband-welcome-top-tier-new-lover-5` | 39 / 39 | 39 eps | HLS/MP4 | ✅ Verificado |
| **Big Betrackson of Gamble** | `dt-big-betrackson-of-gamble` | 13 / 13 | 13 eps | HLS/MP4 | ✅ Verificado |
| **Big Boss Is Back** | `dt-big-boss-is-back` | 102 / 102 | 102 eps | HLS/MP4 | ✅ Verificado |
| **Bikini,Betrayal,and Billions** | `dt-bikini-betrayal-and-billions-2` | 59 / 59 | 59 eps | HLS/MP4 | ✅ Verificado |
| **Billion Dollar Bed: Addicted to Him** | `dt-billion-dollar-bed-addicted-to-him-5` | 41 / 41 | 41 eps | HLS/MP4 | ✅ Verificado |
| **Billion Dollar Bed: Addicted to Him** | `dt-billion-dollar-bed-addicted-to-him-subtitled` | 32 / 32 | 32 eps | HLS/MP4 | ✅ Verificado |
| **BILLIONAIRE BROTHERS FOUND ME IN A DINER** | `dt-billionaire-brothers-found-me-in-a-diner-3` | 95 / 95 | 95 eps | HLS/MP4 | ✅ Verificado |
| **Billionaire by Chance** | `dt-billionaire-by-chance` | 20 / 20 | 20 eps | HLS/MP4 | ✅ Verificado |
| **Billionaire CEO's Runaway WiFe** | `dt-billionaire-ceos-runaway-wife-3` | 15 / 15 | 15 eps | HLS/MP4 | ✅ Verificado |
| **Billionaire Dad's Return** | `dt-billionaire-dads-return` | 76 / 76 | 76 eps | HLS/MP4 | ✅ Verificado |
| **Billionaire Godfather's Delicate Sweetheart** | `dt-billionaire-godfathers-delicate-sweetheart` | 22 / 22 | 22 eps | HLS/MP4 | ✅ Verificado |
| **BILLIONAIRE HEIRESS&MERCENARY KING** | `dt-billionaire-heiress-mercenary-king` | 51 / 51 | 51 eps | HLS/MP4 | ✅ Verificado |
| **BILLIONAIRE HEIRESS&MERCENARY KING** | `dt-billionaire-heiress-mercenary-king-2` | 80 / 80 | 80 eps | HLS/MP4 | ✅ Verificado |
| **BILLIONAIRE HEIRESS&MERCENARY KING** | `dt-billionaire-heiress-mercenary-king-3` | 64 / 64 | 64 eps | HLS/MP4 | ✅ Verificado |
| **BILLIONAIRE HEIRESS&MERCENARY KING** | `dt-billionaire-heiress-mercenary-king-4` | 25 / 25 | 25 eps | HLS/MP4 | ✅ Verificado |
| **BILLIONAIRE HEIRESS&MERCENARY KING** | `dt-billionaire-heiress-mercenary-king-5` | 57 / 57 | 57 eps | HLS/MP4 | ✅ Verificado |
| **BILLIONAIRE HEIRESS&MERCENARY KING** | `dt-billionaire-heiress-mercenary-king-6` | 80 / 80 | 80 eps | HLS/MP4 | ✅ Verificado |
| **BILLIONAIRE HEIRESS&MERCENARY KING** | `dt-billionaire-heiress-mercenary-king-7` | 80 / 80 | 80 eps | HLS/MP4 | ✅ Verificado |
| **BILLIONAIRE HEIRESS&MERCENARY KING** | `dt-billionaire-heiress-mercenary-king-8` | 57 / 57 | 57 eps | HLS/MP4 | ✅ Verificado |
| **BILLIONAIRE HEIRESS&MERCENARY KING** | `dt-billionaire-heiress-mercenary-king-9` | 63 / 63 | 63 eps | HLS/MP4 | ✅ Verificado |
| **BILLIONAIRE PLAYBOY‘S REPLACEMENT BRIDE** | `dt-billionaire-playboys-replacement-bride-2` | 70 / 70 | 70 eps | HLS/MP4 | ✅ Verificado |
| **Billionaire's Substitute Bride** | `dt-billionaire-s-substitute-bride` | 69 / 69 | 69 eps | HLS/MP4 | ✅ Verificado |
| **Billionaire Went Crazy for Lost Love** | `dt-billionaire-went-crazy-for-lost-love` | 104 / 104 | 104 eps | HLS/MP4 | ✅ Verificado |
| **Billionaires on a,Budget** | `dt-billionaires-on-a-budget` | 15 / 15 | 15 eps | HLS/MP4 | ✅ Verificado |
| **Billionaires on a,Budget** | `dt-billionaires-on-a-budget-2` | 15 / 15 | 15 eps | HLS/MP4 | ✅ Verificado |
| **Billionaires on a,Budget** | `dt-billionaires-on-a-budget-3` | 15 / 15 | 15 eps | HLS/MP4 | ✅ Verificado |
| **Billionaires on a,Budget** | `dt-billionaires-on-a-budget-4` | 15 / 15 | 15 eps | HLS/MP4 | ✅ Verificado |
| **Billionaires on a,Budget** | `dt-billionaires-on-a-budget-5` | 15 / 15 | 15 eps | HLS/MP4 | ✅ Verificado |
| **Billionaires on a,Budget** | `dt-billionaires-on-a-budget-6` | 15 / 15 | 15 eps | HLS/MP4 | ✅ Verificado |
| **Billionaires on a,Budget** | `dt-billionaires-on-a-budget-7` | 15 / 15 | 15 eps | HLS/MP4 | ✅ Verificado |
| **Billionaire’s Passionate Love** | `dt-billionaires-passionate-love-3` | 54 / 54 | 54 eps | HLS/MP4 | ✅ Verificado |
| **Billionaire’s Passionate Love** | `dt-billionaires-passionate-love-4` | 56 / 56 | 56 eps | HLS/MP4 | ✅ Verificado |
| **Bite, Breed, Survive** | `dt-bite-breed-survive` | 23 / 23 | 23 eps | HLS/MP4 | ✅ Verificado |
| **Bitten Addicted: Baron's Blood Bride** | `dt-bitten-addicted-barons-blood-bride` | 67 / 67 | 67 eps | HLS/MP4 | ✅ Verificado |
| **Bitter Roots, Sweet Blooms** | `dt-bitter-roots-sweet-blooms` | 44 / 44 | 44 eps | HLS/MP4 | ✅ Verificado |
| **Bittersweet Symphony** | `dt-bittersweet-symphony` | 21 / 21 | 21 eps | HLS/MP4 | ✅ Verificado |
| **Black Blood** | `dt-black-blood` | 7 / 7 | 7 eps | HLS/MP4 | ✅ Verificado |
| **Black Crown: The Godmother’s Revenge** | `dt-black-crown-the-godmothers-revenge` | 60 / 60 | 60 eps | HLS/MP4 | ✅ Verificado |
| **Black Crown: The Godmother’s Revenge** | `dt-black-crown-the-godmothers-revenge-3` | 60 / 60 | 60 eps | HLS/MP4 | ✅ Verificado |
| **Black Mamba: A Mother's Revenge** | `dt-black-mamba-a-mothers-revenge-3` | 60 / 60 | 60 eps | HLS/MP4 | ✅ Verificado |
| **Black Mamba: A Mother's Revenge** | `dt-black-mamba-a-mothers-revenge-4` | 46 / 46 | 46 eps | HLS/MP4 | ✅ Verificado |
| **Black Mamba: A Mother's Revenge** | `dt-black-mamba-a-mothers-revenge-5` | 29 / 29 | 29 eps | HLS/MP4 | ✅ Verificado |
| **Black Mamba: A Mother's Revenge** | `dt-black-mamba-a-mothers-revenge-6` | 58 / 58 | 58 eps | HLS/MP4 | ✅ Verificado |
| **Black Mamba: A Mother's Revenge** | `dt-black-mamba-a-mothers-revenge-7` | 49 / 49 | 49 eps | HLS/MP4 | ✅ Verificado |
| **Black Myth Wukong** | `dt-black-myth-wukong` | 59 / 59 | 59 eps | HLS/MP4 | ✅ Verificado |
| **Black Swan: Ballet Comeback** | `dt-black-swan-ballet-comeback-3` | 76 / 76 | 76 eps | HLS/MP4 | ✅ Verificado |
| **Bladesman: Dugu Mu** | `dt-bladesman-dugu-mu` | 12 / 12 | 12 eps | HLS/MP4 | ✅ Verificado |
| **Blaze of the Fated Fall** | `dt-blaze-of-the-fated-fall-3` | 39 / 39 | 39 eps | HLS/MP4 | ✅ Verificado |
| **Blaze of the Fated Fall** | `dt-blaze-of-the-fated-fall-4` | 36 / 36 | 36 eps | HLS/MP4 | ✅ Verificado |
| **Blaze of the Fated Fall** | `dt-blaze-of-the-fated-fall-5` | 29 / 29 | 29 eps | HLS/MP4 | ✅ Verificado |
| **Blaze of the Fated Fall** | `dt-blaze-of-the-fated-fall-6` | 59 / 59 | 59 eps | HLS/MP4 | ✅ Verificado |
| **Blaze of the Fated Fall** | `dt-blaze-of-the-fated-fall-7` | 60 / 60 | 60 eps | HLS/MP4 | ✅ Verificado |
| **Blaze of the Fated Fall** | `dt-blaze-of-the-fated-fall-8` | 60 / 60 | 60 eps | HLS/MP4 | ✅ Verificado |
| **Blessed With Twins** | `dt-blessed-with-twins` | 86 / 86 | 86 eps | HLS/MP4 | ✅ Verificado |
| **Blind Draw** | `dt-blind-draw-2` | 18 / 18 | 18 eps | HLS/MP4 | ✅ Verificado |
| **Blind Escape** | `dt-blind-escape` | 19 / 19 | 19 eps | HLS/MP4 | ✅ Verificado |
| **BLIND HEIR'S REVENGE** | `dt-blind-heirs-revenge-3` | 60 / 60 | 60 eps | HLS/MP4 | ✅ Verificado |
| **BLIND HEIR'S REVENGE** | `dt-blind-heirs-revenge-4` | 43 / 43 | 43 eps | HLS/MP4 | ✅ Verificado |
| **BLIND HEIR'S REVENGE** | `dt-blind-heirs-revenge-5` | 60 / 60 | 60 eps | HLS/MP4 | ✅ Verificado |
| **BLIND HEIR'S REVENGE** | `dt-blind-heirs-revenge-6` | 47 / 47 | 47 eps | HLS/MP4 | ✅ Verificado |
| **BLIND HEIR'S REVENGE** | `dt-blind-heirs-revenge-7` | 47 / 47 | 47 eps | HLS/MP4 | ✅ Verificado |
| **Blind Man's Demon God Pets** | `dt-blind-mans-demon-god-pets` | 64 / 64 | 64 eps | HLS/MP4 | ✅ Verificado |
| **Blind to Their Lies, Married to His Fortune** | `dt-blind-to-their-lies-married-to-his-fortune-3` | 45 / 45 | 45 eps | HLS/MP4 | ✅ Verificado |
| **Blind Vows** | `dt-blind-vows` | 28 / 28 | 28 eps | HLS/MP4 | ✅ Verificado |
| **Blizzard Rebirth: Saving the Wilsons** | `dt-blizzard-rebirth-saving-the-wilsons` | 61 / 61 | 61 eps | HLS/MP4 | ✅ Verificado |
| **Blood and Legacy** | `dt-blood-and-legacy-2` | 26 / 26 | 26 eps | HLS/MP4 | ✅ Verificado |
| **Blood-Bound Bride I Married My Ex's Father** | `dt-blood-bound-bride-i-married-my-exs-father-2` | 60 / 60 | 60 eps | HLS/MP4 | ✅ Verificado |
| **Blood-Bound Bride I Married My Ex's Father** | `dt-blood-bound-bride-i-married-my-exs-father-3` | 60 / 60 | 60 eps | HLS/MP4 | ✅ Verificado |
| **Blood Bride** | `dt-blood-bride-3` | 60 / 60 | 60 eps | HLS/MP4 | ✅ Verificado |
| **Blood Bride** | `dt-blood-bride-4` | 51 / 51 | 51 eps | HLS/MP4 | ✅ Verificado |
| **Blood Contract My Vampire Daddy** | `dt-blood-contract-my-vampire-daddy-3` | 11 / 11 | 11 eps | HLS/MP4 | ✅ Verificado |
| **Blood Crown: The Slave Who Broke Immortals** | `dt-blood-crown-the-slave-who-broke-immortals` | 21 / 21 | 21 eps | HLS/MP4 | ✅ Verificado |
| **Blood Harvest** | `dt-blood-harvest-4` | 26 / 26 | 26 eps | HLS/MP4 | ✅ Verificado |
| **Blood Hell Storm​** | `dt-blood-hell-storm` | 52 / 52 | 52 eps | HLS/MP4 | ✅ Verificado |
| **Blood Lotus (Dubbed)** | `dt-blood-lotus` | 47 / 47 | 47 eps | HLS/MP4 | ✅ Verificado |
| **Blood Marked Mate** | `dt-blood-marked-mate` | 35 / 35 | 35 eps | HLS/MP4 | ✅ Verificado |
| **Blood Mate** | `dt-blood-mate-4` | 15 / 15 | 15 eps | HLS/MP4 | ✅ Verificado |
| **Blood Mate** | `dt-blood-mate-5` | 15 / 15 | 15 eps | HLS/MP4 | ✅ Verificado |
| **Blood Mate** | `dt-blood-mate-6` | 15 / 15 | 15 eps | HLS/MP4 | ✅ Verificado |
| **Blood Moon A Cold Marriage** | `dt-blood-moon-a-cold-marriage-3` | 76 / 76 | 76 eps | HLS/MP4 | ✅ Verificado |
| **Blood Moon A Cold Marriage** | `dt-blood-moon-a-cold-marriage-4` | 64 / 64 | 64 eps | HLS/MP4 | ✅ Verificado |
| **Blood on the Rose** | `dt-blood-on-the-rose-3` | 32 / 32 | 32 eps | HLS/MP4 | ✅ Verificado |
| **Blood on the Rose** | `dt-blood-on-the-rose-4` | 32 / 32 | 32 eps | HLS/MP4 | ✅ Verificado |
| **Blood on the Rose** | `dt-blood-on-the-rose-5` | 28 / 28 | 28 eps | HLS/MP4 | ✅ Verificado |
| **BLOOD PACT REBORN** | `dt-blood-pact-reborn-4` | 47 / 47 | 47 eps | HLS/MP4 | ✅ Verificado |
| **BLOOD PACT : VENGEFUL HUNT** | `dt-blood-pact-vengeful-hunt-3` | 10 / 10 | 10 eps | HLS/MP4 | ✅ Verificado |
| **Blood Pearl of the Mer** | `dt-blood-pearl-of-the-mer` | 9 / 9 | 9 eps | HLS/MP4 | ✅ Verificado |
| **Blood Return Heiress Crushes the Rich Clan** | `dt-blood-return-heiress-crushes-the-rich-clan` | 65 / 65 | 65 eps | HLS/MP4 | ✅ Verificado |
| **Blood Return Heiress Crushes the Rich Clan** | `dt-blood-return-heiress-crushes-the-rich-clan-2` | 65 / 65 | 65 eps | HLS/MP4 | ✅ Verificado |
| **Blood Return Heiress Crushes the Rich Clan** | `dt-blood-return-heiress-crushes-the-rich-clan-3` | 65 / 65 | 65 eps | HLS/MP4 | ✅ Verificado |
| **Blood Return Heiress Crushes the Rich Clan** | `dt-blood-return-heiress-crushes-the-rich-clan-4` | 35 / 35 | 35 eps | HLS/MP4 | ✅ Verificado |
| **Blood Return Heiress Crushes the Rich Clan** | `dt-blood-return-heiress-crushes-the-rich-clan-5` | 30 / 30 | 30 eps | HLS/MP4 | ✅ Verificado |
| **Blood Return Heiress Crushes the Rich Clan** | `dt-blood-return-heiress-crushes-the-rich-clan-6` | 60 / 60 | 60 eps | HLS/MP4 | ✅ Verificado |
| **Blood Return Heiress Crushes the Rich Clan** | `dt-blood-return-heiress-crushes-the-rich-clan-7` | 65 / 65 | 65 eps | HLS/MP4 | ✅ Verificado |
| **Blood & Silver: Rise of the Alpha's Rejected Mate** | `dt-blood-silver-rise-of-the-alphas-rejected-mate` | 74 / 74 | 74 eps | HLS/MP4 | ✅ Verificado |
| **Blood Ties The Missing Daughter** | `dt-blood-ties-the-missing-daughter-3` | 44 / 44 | 44 eps | HLS/MP4 | ✅ Verificado |
| **Blood-Weeping Rose** | `dt-blood-weeping-rose-3` | 9 / 9 | 9 eps | HLS/MP4 | ✅ Verificado |
| **Bloodbound Queen-I Kissed the Hunter Who Saved Me** | `dt-bloodbound-queen-i-kissed-the-hunter-who-saved-me-2` | 40 / 40 | 40 eps | HLS/MP4 | ✅ Verificado |
| **Bloody dress, his whole family begged me on their knees to stop** | `dt-bloody-dress-his-whole-family-begged-me-on-their-knees-to-stop-3` | 60 / 60 | 60 eps | HLS/MP4 | ✅ Verificado |
| **Bloody Vanity** | `dt-bloody-vanity` | 21 / 21 | 21 eps | HLS/MP4 | ✅ Verificado |
| **Bloom From Ashes** | `dt-bloom-from-ashes` | 49 / 49 | 49 eps | HLS/MP4 | ✅ Verificado |
| **Blossoming Without You** | `dt-blossoming-without-you` | 70 / 70 | 70 eps | HLS/MP4 | ✅ Verificado |
| **Blue Is Your Collar** | `dt-blue-is-your-collar` | 80 / 80 | 80 eps | HLS/MP4 | ✅ Verificado |
| **Body Swap: CEO And the Princess** | `dt-body-swap-ceo-and-the-princess` | 84 / 84 | 84 eps | HLS/MP4 | ✅ Verificado |
| **Bodyguard Wins CEO Love** | `dt-bodyguard-wins-ceo-love` | 43 / 43 | 43 eps | HLS/MP4 | ✅ Verificado |
| **Bond Betrayed, Queen Reborn** | `dt-bond-betrayed-queen-reborn` | 7 / 7 | 7 eps | HLS/MP4 | ✅ Verificado |
| **Born Again for Him** | `dt-born-again-for-him` | 72 / 72 | 72 eps | HLS/MP4 | ✅ Verificado |
| **Born in Blood** | `dt-born-in-blood` | 17 / 17 | 17 eps | HLS/MP4 | ✅ Verificado |
| **Born Rich, Built Richer (Dubbed)** | `dt-born-rich-built-richer-2` | 55 / 55 | 55 eps | HLS/MP4 | ✅ Verificado |
| **(Dubbed) Born to Dominate** | `dt-born-to-dominate-2` | 69 / 69 | 69 eps | HLS/MP4 | ✅ Verificado |
| **Boss, Intern Is Your Wife!?** | `dt-boss-intern-is-your-wife` | 80 / 80 | 80 eps | HLS/MP4 | ✅ Verificado |
| **Boss, Intern Is Your Wife!?** | `dt-boss-intern-is-your-wife-2` | 60 / 60 | 60 eps | HLS/MP4 | ✅ Verificado |
| **Boss, Your Wife Is Super Cool!** | `dt-boss-your-wife-is-super-cool-3` | 76 / 76 | 76 eps | HLS/MP4 | ✅ Verificado |
| **Boss, You've Got The Wrong Wife** | `dt-boss-youve-got-the-wrong-wife-2` | 82 / 82 | 82 eps | HLS/MP4 | ✅ Verificado |
| **Bossy Husband Who Loved Me** | `dt-bossy-husband-who-loved-me` | 75 / 75 | 75 eps | HLS/MP4 | ✅ Verificado |
| **Bound by a Forlorn Fate** | `dt-bound-by-a-forlorn-fate` | 59 / 59 | 59 eps | HLS/MP4 | ✅ Verificado |
| **Bound by Contract** | `dt-bound-by-contract-3` | 6 / 6 | 6 eps | HLS/MP4 | ✅ Verificado |
| **Bound by Contract** | `dt-bound-by-contract-4` | 8 / 8 | 8 eps | HLS/MP4 | ✅ Verificado |
| **Bound by Contract** | `dt-bound-by-contract-5` | 15 / 15 | 15 eps | HLS/MP4 | ✅ Verificado |
| **Bound by Fire** | `dt-bound-by-fire` | 98 / 98 | 98 eps | HLS/MP4 | ✅ Verificado |
| **Bound by Fire** | `dt-bound-by-fire-2` | 13 / 13 | 13 eps | HLS/MP4 | ✅ Verificado |
| **Bound by Love** | `dt-bound-by-love` | 92 / 92 | 92 eps | HLS/MP4 | ✅ Verificado |
| **Bound By My Author** | `dt-bound-by-my-author` | 15 / 15 | 15 eps | HLS/MP4 | ✅ Verificado |
| **Bound by the Alpha’s Chain** | `dt-bound-by-the-alphas-chain` | 23 / 23 | 23 eps | HLS/MP4 | ✅ Verificado |
| **Bound by the Billionaire** | `dt-bound-by-the-billionaire` | 48 / 48 | 48 eps | HLS/MP4 | ✅ Verificado |
| **Bound by the Debt of Sin** | `dt-bound-by-the-debt-of-sin` | 72 / 72 | 72 eps | HLS/MP4 | ✅ Verificado |
| **Bound to My Missing Wife** | `dt-bound-to-my-missing-wife` | 62 / 62 | 62 eps | HLS/MP4 | ✅ Verificado |
| **Bound to the Ancient Vampire:A Modern Girl's Guide to Chaos** | `dt-bound-to-the-ancient-vampire-a-modern-girls-guide-to-chaos-3` | 121 / 121 | 121 eps | HLS/MP4 | ✅ Verificado |
| **Bound to the Ancient Vampire:A Modern Girl's Guide to Chaos** | `dt-bound-to-the-ancient-vampire-a-modern-girls-guide-to-chaos-4` | 119 / 119 | 119 eps | HLS/MP4 | ✅ Verificado |
| **Bound to the Ancient Vampire:A Modern Girl's Guide to Chaos** | `dt-bound-to-the-ancient-vampire-a-modern-girls-guide-to-chaos-5` | 71 / 71 | 71 eps | HLS/MP4 | ✅ Verificado |
| **Bound to the Ancient Vampire:A Modern Girl's Guide to Chaos** | `dt-bound-to-the-ancient-vampire-a-modern-girls-guide-to-chaos-6` | 96 / 96 | 96 eps | HLS/MP4 | ✅ Verificado |
| **Bound to the Ancient Vampire:A Modern Girl's Guide to Chaos** | `dt-bound-to-the-ancient-vampire-a-modern-girls-guide-to-chaos-7` | 121 / 121 | 121 eps | HLS/MP4 | ✅ Verificado |
| **Bound to the Ancient Vampire:A Modern Girl's Guide to Chaos** | `dt-bound-to-the-ancient-vampire-a-modern-girls-guide-to-chaos-8` | 88 / 88 | 88 eps | HLS/MP4 | ✅ Verificado |
| **Bound to the Dragon King** | `dt-bound-to-the-dragon-king` | 17 / 17 | 17 eps | HLS/MP4 | ✅ Verificado |
| **Bound to the Midnight King** | `dt-bound-to-the-midnight-king` | 18 / 18 | 18 eps | HLS/MP4 | ✅ Verificado |
| **Bound to the Rebel Wolf** | `dt-bound-to-the-rebel-wolf` | 61 / 61 | 61 eps | HLS/MP4 | ✅ Verificado |
| **Bound to the Vampire King** | `dt-bound-to-the-vampire-king` | 71 / 71 | 71 eps | HLS/MP4 | ✅ Verificado |
| **Brace Up for Divorce, Mr. Li: A Tale of Resilience (Dubbed)** | `dt-brace-up-for-divorce-mr-li-a-tale-of-resilience` | 67 / 67 | 67 eps | HLS/MP4 | ✅ Verificado |
| **Break Her, Then Hold Her** | `dt-break-her-then-hold-her-3` | 13 / 13 | 13 eps | HLS/MP4 | ✅ Verificado |
| **Break Her, Then Hold Her** | `dt-break-her-then-hold-her-4` | 15 / 15 | 15 eps | HLS/MP4 | ✅ Verificado |
| **Breaking Free** | `dt-breaking-free-6` | 61 / 61 | 61 eps | HLS/MP4 | ✅ Verificado |
| **Breaking News** | `dt-breaking-news` | 68 / 68 | 68 eps | HLS/MP4 | ✅ Verificado |
| **Breaking the Bro Code** | `dt-breaking-the-bro-code` | 20 / 20 | 20 eps | HLS/MP4 | ✅ Verificado |
| **Breaking the Cocoon: Rebirth** | `dt-breaking-the-cocoon-rebirth` | 30 / 30 | 30 eps | HLS/MP4 | ✅ Verificado |
| **Breaking the Ice** | `dt-breaking-the-ice` | 70 / 70 | 70 eps | HLS/MP4 | ✅ Verificado |
| **Breakup Settlement System** | `dt-breakup-settlement-system` | 29 / 29 | 29 eps | HLS/MP4 | ✅ Verificado |
| **Breathe** | `dt-breathe` | 49 / 49 | 49 eps | HLS/MP4 | ✅ Verificado |
| **Bred by My Siren King Brother-in-Law** | `dt-bred-by-my-siren-king-brother-in-law-2` | 29 / 29 | 29 eps | HLS/MP4 | ✅ Verificado |
| **Breeding With The Horseman** | `dt-breeding-with-the-horseman` | 65 / 65 | 65 eps | HLS/MP4 | ✅ Verificado |
| **Breeding With The Horseman** | `dt-breeding-with-the-horseman-2` | 54 / 54 | 54 eps | HLS/MP4 | ✅ Verificado |
| **Breeding With The Horseman** | `dt-breeding-with-the-horseman-3` | 45 / 45 | 45 eps | HLS/MP4 | ✅ Verificado |
| **Bride Beggar Turns Powerful** | `dt-bride-beggar-turns-powerful` | 60 / 60 | 60 eps | HLS/MP4 | ✅ Verificado |
| **Bride Beggar Turns Powerful** | `dt-bride-beggar-turns-powerful-2` | 60 / 60 | 60 eps | HLS/MP4 | ✅ Verificado |
| **Bride Beggar Turns Powerful** | `dt-bride-beggar-turns-powerful-5` | 46 / 46 | 46 eps | HLS/MP4 | ✅ Verificado |
| **Bride Beggar Turns Powerful** | `dt-bride-beggar-turns-powerful-6` | 48 / 48 | 48 eps | HLS/MP4 | ✅ Verificado |
| **Bride Chooses Again** | `dt-bride-chooses-again` | 72 / 72 | 72 eps | HLS/MP4 | ✅ Verificado |
| **Bride for the Cursed Lycan Kings** | `dt-bride-for-the-cursed-lycan-kings` | 5 / 5 | 5 eps | HLS/MP4 | ✅ Verificado |
| **Bride in Disguise (Dubbed)** | `dt-bride-in-disguise` | 97 / 97 | 97 eps | HLS/MP4 | ✅ Verificado |
| **Bride of the Curse** | `dt-bride-of-the-curse` | 47 / 47 | 47 eps | HLS/MP4 | ✅ Verificado |
| **Bride of the Mercenary King: A Billion Heiress’s Vow** | `dt-bride-of-the-mercenary-king-a-billion-heiresss-vow-3` | 45 / 45 | 45 eps | HLS/MP4 | ✅ Verificado |
| **Bride of the North** | `dt-bride-of-the-north` | 52 / 52 | 52 eps | HLS/MP4 | ✅ Verificado |
| **Bride of the North** | `dt-bride-of-the-north-2` | 60 / 60 | 60 eps | HLS/MP4 | ✅ Verificado |
| **Bride of the Underworld** | `dt-bride-of-the-underworld` | 40 / 40 | 40 eps | HLS/MP4 | ✅ Verificado |
| **Bride of Vengeance** | `dt-bride-of-vengeance-4` | 59 / 59 | 59 eps | HLS/MP4 | ✅ Verificado |
| **Bride's Revenge** | `dt-brides-revenge` | 99 / 99 | 99 eps | HLS/MP4 | ✅ Verificado |
| **Bride's Revenge** | `dt-brides-revenge-2` | 120 / 120 | 120 eps | HLS/MP4 | ✅ Verificado |
| **Bride's Revenge** | `dt-brides-revenge-3` | 56 / 56 | 56 eps | HLS/MP4 | ✅ Verificado |
| **Bride's Revenge** | `dt-brides-revenge-4` | 116 / 116 | 116 eps | HLS/MP4 | ✅ Verificado |
| **Bride's Revenge** | `dt-brides-revenge-5` | 118 / 118 | 118 eps | HLS/MP4 | ✅ Verificado |
| **Bride's Revenge** | `dt-brides-revenge-6` | 103 / 103 | 103 eps | HLS/MP4 | ✅ Verificado |
| **Bride's Revenge** | `dt-brides-revenge-7` | 110 / 110 | 110 eps | HLS/MP4 | ✅ Verificado |
| **Bringing Back the Hidden Wife** | `dt-bringing-back-the-hidden-wife` | 88 / 88 | 88 eps | HLS/MP4 | ✅ Verificado |
| **Bringing Trouble Upon Oneself:The 99-Day Deal with the Cold-Faced Boss** | `dt-bringing-trouble-upon-oneself-the-99-day-deal-with-the-cold-faced-boss` | 120 / 120 | 120 eps | HLS/MP4 | ✅ Verificado |
| **Brink of Control** | `dt-brink-of-control-3` | 53 / 53 | 53 eps | HLS/MP4 | ✅ Verificado |
| **Brink of Control** | `dt-brink-of-control-4` | 41 / 41 | 41 eps | HLS/MP4 | ✅ Verificado |
| **Brink of Control** | `dt-brink-of-control-5` | 43 / 43 | 43 eps | HLS/MP4 | ✅ Verificado |
| **Brink of Control** | `dt-brink-of-control-7` | 45 / 45 | 45 eps | HLS/MP4 | ✅ Verificado |
| **Broke After Divorce,I'm Nova Billionaire** | `dt-broke-after-divorce-im-nova-billionaire-4` | 70 / 70 | 70 eps | HLS/MP4 | ✅ Verificado |
| **Broke After Divorce,I'm Nova Billionaire** | `dt-broke-after-divorce-im-nova-billionaire-5` | 60 / 60 | 60 eps | HLS/MP4 | ✅ Verificado |
| **Broke After Divorce,I'm Nova Billionaire** | `dt-broke-after-divorce-im-nova-billionaire-6` | 8 / 8 | 8 eps | HLS/MP4 | ✅ Verificado |
| **Broke Yesterday, Billionaire Today (Dubbed)** | `dt-broke-yesterday-billionaire-today-2` | 9 / 9 | 9 eps | HLS/MP4 | ✅ Verificado |
| **Broken Body, No Forgiveness** | `dt-broken-body-no-forgiveness-2` | 44 / 44 | 44 eps | HLS/MP4 | ✅ Verificado |
| **Broken Bonds, Fresh Scars** | `dt-broken-bonds-fresh-scars` | 56 / 56 | 56 eps | HLS/MP4 | ✅ Verificado |
| **Broken Champion** | `dt-broken-champion` | 44 / 44 | 44 eps | HLS/MP4 | ✅ Verificado |
| **Broken Goodbye: Hello, Mr. Lawyer** | `dt-broken-goodbye-hello-mr-lawyer` | 27 / 27 | 27 eps | HLS/MP4 | ✅ Verificado |
| **Broken Marriage, Mistaken Love** | `dt-broken-marriage-mistaken-love` | 11 / 11 | 11 eps | HLS/MP4 | ✅ Verificado |
| **Broken Vows, Riding to Glory** | `dt-broken-vows-riding-to-glory` | 63 / 63 | 63 eps | HLS/MP4 | ✅ Verificado |
| **Broken Vows, Riding to Glory** | `dt-broken-vows-riding-to-glory-5` | 52 / 52 | 52 eps | HLS/MP4 | ✅ Verificado |
| **Broken Vows, Riding to Glory** | `dt-broken-vows-riding-to-glory-6` | 63 / 63 | 63 eps | HLS/MP4 | ✅ Verificado |
| **Brother-in-Law by Day, Lover by Night** | `dt-brother-in-law-by-day-lover-by-night` | 31 / 31 | 31 eps | HLS/MP4 | ✅ Verificado |
| **Brothers in Arms** | `dt-brothers-in-arms` | 72 / 72 | 72 eps | HLS/MP4 | ✅ Verificado |
| **Bullied by Her Family, the Billionaire Strikes Back** | `dt-bullied-by-her-family-the-billionaire-strikes-back-3` | 60 / 60 | 60 eps | HLS/MP4 | ✅ Verificado |
| **Buried Alive With Cheating Husband** | `dt-buried-alive-with-cheating-husband` | 39 / 39 | 39 eps | HLS/MP4 | ✅ Verificado |
| **BURIED SACRIFICE** | `dt-buried-sacrifice` | 42 / 42 | 42 eps | HLS/MP4 | ✅ Verificado |
| **Burn Him, Bury Him** | `dt-burn-him-bury-him-4` | 50 / 50 | 50 eps | HLS/MP4 | ✅ Verificado |
| **Burn of Your Lips** | `dt-burn-of-your-lips-3` | 15 / 15 | 15 eps | HLS/MP4 | ✅ Verificado |
| **Burn of Your Lips** | `dt-burn-of-your-lips-4` | 15 / 15 | 15 eps | HLS/MP4 | ✅ Verificado |
| **Burning Flame Captive** | `dt-burning-flame-captive-2` | 60 / 60 | 60 eps | HLS/MP4 | ✅ Verificado |
| **Burning Flame of Love Triangle** | `dt-burning-flame-of-love-triangle` | 70 / 70 | 70 eps | HLS/MP4 | ✅ Verificado |
| **Burning Love and Unhindered Adoration** | `dt-burning-love-and-unhindered-adoration` | 76 / 76 | 76 eps | HLS/MP4 | ✅ Verificado |
| **Burning Sister** | `dt-burning-sister` | 98 / 98 | 98 eps | HLS/MP4 | ✅ Verificado |
| **Burning Winter** | `dt-burning-winter` | 70 / 70 | 70 eps | HLS/MP4 | ✅ Verificado |
| **Burnt Roses, Frozen Heart** | `dt-burnt-roses-frozen-heart` | 21 / 21 | 21 eps | HLS/MP4 | ✅ Verificado |
| **Busting the Fake Stepmom at My Father’s Wedding** | `dt-busting-the-fake-stepmom-at-my-fathers-wedding` | 68 / 68 | 68 eps | HLS/MP4 | ✅ Verificado |
| **But Daddy I Love Him** | `dt-but-daddy-i-love-him-3` | 46 / 46 | 46 eps | HLS/MP4 | ✅ Verificado |
| **By Design** | `dt-by-design` | 47 / 47 | 47 eps | HLS/MP4 | ✅ Verificado |
| **Bye bye scumbag, hello top-tier Alpha** | `dt-bye-bye-scumbag-hello-top-tier-alpha-2` | 30 / 30 | 30 eps | HLS/MP4 | ✅ Verificado |
| **Bye, Son! The Legacy’s Not Yours!** | `dt-bye-son-the-legacys-not-yours` | 57 / 57 | 57 eps | HLS/MP4 | ✅ Verificado |
| **Bygone Light Shines ON THE GUTTER** | `dt-bygone-light-shines-on-the-gutter-3` | 70 / 70 | 70 eps | HLS/MP4 | ✅ Verificado |
| **Bygone Light Shines ON THE GUTTER** | `dt-bygone-light-shines-on-the-gutter-4` | 70 / 70 | 70 eps | HLS/MP4 | ✅ Verificado |
| **Bygone Light Shines ON THE GUTTER** | `dt-bygone-light-shines-on-the-gutter-5` | 64 / 64 | 64 eps | HLS/MP4 | ✅ Verificado |
| **Bygone Light Shines ON THE GUTTER** | `dt-bygone-light-shines-on-the-gutter-6` | 69 / 69 | 69 eps | HLS/MP4 | ✅ Verificado |
| **Bygone Light Shines ON THE GUTTER** | `dt-bygone-light-shines-on-the-gutter-7` | 70 / 70 | 70 eps | HLS/MP4 | ✅ Verificado |
| **Bygone Light Shines ON THE GUTTER** | `dt-bygone-light-shines-on-the-gutter-8` | 70 / 70 | 70 eps | HLS/MP4 | ✅ Verificado |
| **Bygone Light Shines ON THE GUTTER** | `dt-bygone-light-shines-on-the-gutter-9` | 70 / 70 | 70 eps | HLS/MP4 | ✅ Verificado |
| **Caged by His Training** | `dt-caged-by-his-training` | 60 / 60 | 60 eps | HLS/MP4 | ✅ Verificado |
| **Caged by His Training** | `dt-caged-by-his-training-3` | 60 / 60 | 60 eps | HLS/MP4 | ✅ Verificado |
| **Caged by the Mafia Boss** | `dt-caged-by-the-mafia-boss` | 48 / 48 | 48 eps | HLS/MP4 | ✅ Verificado |
| **CAGED LOVE: The QUEEN'S REVENGE** | `dt-caged-love-the-queens-revenge-3` | 60 / 60 | 60 eps | HLS/MP4 | ✅ Verificado |
| **CAGED LOVE: The QUEEN'S REVENGE** | `dt-caged-love-the-queens-revenge-4` | 60 / 60 | 60 eps | HLS/MP4 | ✅ Verificado |
| **Caged Sparrow** | `dt-caged-sparrow` | 66 / 66 | 66 eps | HLS/MP4 | ✅ Verificado |
| **Calculated Betrayal** | `dt-calculated-betrayal` | 35 / 35 | 35 eps | HLS/MP4 | ✅ Verificado |
| **CALL ME A LOWLY CLEANER? THEY'D BEG ME TO BE CEO** | `dt-call-me-a-lowly-cleaner-theyd-beg-me-to-be-ceo-3` | 60 / 60 | 60 eps | HLS/MP4 | ✅ Verificado |
| **CALL ME A LOWLY CLEANER? THEY'D BEG ME TO BE CEO** | `dt-call-me-a-lowly-cleaner-theyd-beg-me-to-be-ceo-4` | 60 / 60 | 60 eps | HLS/MP4 | ✅ Verificado |
| **CALL ME A LOWLY CLEANER? THEY'D BEG ME TO BE CEO** | `dt-call-me-a-lowly-cleaner-theyd-beg-me-to-be-ceo-5` | 60 / 60 | 60 eps | HLS/MP4 | ✅ Verificado |
| **Call Me Father, Love Me Lover** | `dt-call-me-father-love-me-lover-4` | 60 / 60 | 60 eps | HLS/MP4 | ✅ Verificado |
| **Call Me Love, Professor** | `dt-call-me-love-professor-3` | 53 / 53 | 53 eps | HLS/MP4 | ✅ Verificado |
| **Callsign: Legacy** | `dt-callsign-legacy` | 64 / 64 | 64 eps | HLS/MP4 | ✅ Verificado |
| **Campus King's Early Access** | `dt-campus-king-s-early-access` | 137 / 137 | 137 eps | HLS/MP4 | ✅ Verificado |
| **Cancel the Wedding, Queen Moves On** | `dt-cancel-the-wedding-queen-moves-on` | 71 / 71 | 71 eps | HLS/MP4 | ✅ Verificado |
| **Cancer Makes Me Stronger** | `dt-cancer-makes-me-stronger` | 72 / 72 | 72 eps | HLS/MP4 | ✅ Verificado |
| **Captain,Down On His Knees** | `dt-captain-down-on-his-knees` | 60 / 60 | 60 eps | HLS/MP4 | ✅ Verificado |
| **Captain,Down On His Knees** | `dt-captain-down-on-his-knees-2` | 60 / 60 | 60 eps | HLS/MP4 | ✅ Verificado |
| **Captain,Down On His Knees** | `dt-captain-down-on-his-knees-3` | 60 / 60 | 60 eps | HLS/MP4 | ✅ Verificado |
| **Captain,Down On His Knees** | `dt-captain-down-on-his-knees-4` | 60 / 60 | 60 eps | HLS/MP4 | ✅ Verificado |
| **Captain & His Secret Agent** | `dt-captain-his-secret-agent` | 15 / 15 | 15 eps | HLS/MP4 | ✅ Verificado |
| **Captain & His Secret Agent** | `dt-captain-his-secret-agent-2` | 15 / 15 | 15 eps | HLS/MP4 | ✅ Verificado |
| **Captain & His Secret Agent** | `dt-captain-his-secret-agent-3` | 15 / 15 | 15 eps | HLS/MP4 | ✅ Verificado |
| **Captive Love from the Mob Boss** | `dt-captive-love-from-the-mob-boss` | 65 / 65 | 65 eps | HLS/MP4 | ✅ Verificado |
| **Captive Love from the Mob Boss(Dubbed)** | `dt-captive-love-from-the-mob-boss-dubbed` | 65 / 65 | 65 eps | HLS/MP4 | ✅ Verificado |
| **Carefree Security Guard Meets His Star** | `dt-carefree-security-guard-meets-his-star` | 86 / 86 | 86 eps | HLS/MP4 | ✅ Verificado |
| **Carry On With My Heart** | `dt-carry-on-with-my-heart` | 60 / 60 | 60 eps | HLS/MP4 | ✅ Verificado |
| **Carrying My Boss’s Baby** | `dt-carrying-my-bosss-baby` | 96 / 96 | 96 eps | HLS/MP4 | ✅ Verificado |
| **Carrying the Throne** | `dt-carrying-the-throne-2` | 70 / 70 | 70 eps | HLS/MP4 | ✅ Verificado |
| **Cast Aside by Pureblood Duke, Crown of the Wolf Queen** | `dt-cast-aside-by-pureblood-duke-crown-of-the-wolf-queen` | 67 / 67 | 67 eps | HLS/MP4 | ✅ Verificado |
| **Cast Aside by Pureblood Duke, Crown of the Wolf Queen** | `dt-cast-aside-by-pureblood-duke-crown-of-the-wolf-queen-2` | 67 / 67 | 67 eps | HLS/MP4 | ✅ Verificado |
| **Cast Him Like the Wind** | `dt-cast-him-like-the-wind` | 53 / 53 | 53 eps | HLS/MP4 | ✅ Verificado |
| **Cast Out by the Mob, My Whole Family Ascended** | `dt-cast-out-by-the-mob-my-whole-family-ascended-2` | 46 / 46 | 46 eps | HLS/MP4 | ✅ Verificado |
| **Cast Out by the Mob, My Whole Family Ascended** | `dt-cast-out-by-the-mob-my-whole-family-ascended-5` | 57 / 57 | 57 eps | HLS/MP4 | ✅ Verificado |
| **Casting Off the Prince Consort: No More a Foolish Princess** | `dt-casting-off-the-prince-consort-no-more-a-foolish-princess` | 33 / 33 | 33 eps | HLS/MP4 | ✅ Verificado |
| **Catching the True Princess** | `dt-catching-the-true-princess` | 65 / 65 | 65 eps | HLS/MP4 | ✅ Verificado |
| **CAT'S VENGEANCE** | `dt-cats-vengeance` | 23 / 23 | 23 eps | HLS/MP4 | ✅ Verificado |
| **Caught Between His Hands** | `dt-caught-between-his-hands` | 25 / 25 | 25 eps | HLS/MP4 | ✅ Verificado |
| **Caught in the Love Trap** | `dt-caught-in-the-love-trap` | 73 / 73 | 73 eps | HLS/MP4 | ✅ Verificado |
| **Caught on Camera: Cheating in Progress** | `dt-caught-on-camera-cheating-in-progress` | 17 / 17 | 17 eps | HLS/MP4 | ✅ Verificado |
| **CEO and the Country Girl** | `dt-ceo-and-the-country-girl` | 59 / 59 | 59 eps | HLS/MP4 | ✅ Verificado |
| **CEO's Apology: Rebuilding Love After Divorce(Subtitled Version2)** | `dt-ceo-s-apology-rebuilding-love-after-divorce-2` | 86 / 86 | 86 eps | HLS/MP4 | ✅ Verificado |
| **CEO & the Country Girl** | `dt-ceo-the-country-girl` | 59 / 59 | 59 eps | HLS/MP4 | ✅ Verificado |
| **CEO Wants My Little Rascal** | `dt-ceo-wants-my-little-rascal` | 68 / 68 | 68 eps | HLS/MP4 | ✅ Verificado |
| **CEO’s Pursuit: Baby and Wife No Escape** | `dt-ceos-pursuit-baby-and-wife-no-escape-2` | 84 / 84 | 84 eps | HLS/MP4 | ✅ Verificado |
| **CEO's Rejected Wife** | `dt-ceos-rejected-wife` | 20 / 20 | 20 eps | HLS/MP4 | ✅ Verificado |
| **CEO's Replacement Bride** | `dt-ceos-replacement-bride` | 94 / 94 | 94 eps | HLS/MP4 | ✅ Verificado |
| **CEO's Serendipitous Encounter** | `dt-ceos-serendipitous-encounter` | 61 / 61 | 61 eps | HLS/MP4 | ✅ Verificado |
| **CEO's Silent Devotion** | `dt-ceos-silent-devotion` | 49 / 49 | 49 eps | HLS/MP4 | ✅ Verificado |
| **Chained By Her Love** | `dt-chained-by-her-love` | 62 / 62 | 62 eps | HLS/MP4 | ✅ Verificado |
| **Chained to the Dragon Prince** | `dt-chained-to-the-dragon-prince` | 23 / 23 | 23 eps | HLS/MP4 | ✅ Verificado |
| **Chasing My Rejected Wife** | `dt-chasing-my-rejected-wife` | 83 / 83 | 83 eps | HLS/MP4 | ✅ Verificado |
| **Chasing My Wife** | `dt-chasing-my-wife` | 83 / 83 | 83 eps | HLS/MP4 | ✅ Verificado |
| **Cheat on Me, Get Fed to Fish** | `dt-cheat-on-me-get-fed-to-fish-3` | 11 / 11 | 11 eps | HLS/MP4 | ✅ Verificado |
| **Cheat on Me, Get Fed to Fish** | `dt-cheat-on-me-get-fed-to-fish-4` | 80 / 80 | 80 eps | HLS/MP4 | ✅ Verificado |
| **Cheated with a robot** | `dt-cheated-with-a-robot` | 50 / 50 | 50 eps | HLS/MP4 | ✅ Verificado |
| **Cherished by My Uncle After the Family Rift** | `dt-cherished-by-my-uncle-after-the-family-rift` | 71 / 71 | 71 eps | HLS/MP4 | ✅ Verificado |
| **Chosen Alpha** | `dt-chosen-alpha` | 17 / 17 | 17 eps | HLS/MP4 | ✅ Verificado |
| **Chosen by a Queen of Vampire** | `dt-chosen-by-a-queen-of-vampire` | 44 / 44 | 44 eps | HLS/MP4 | ✅ Verificado |
| **Chosen by a Vampire** | `dt-chosen-by-a-vampire` | 44 / 44 | 44 eps | HLS/MP4 | ✅ Verificado |
| **Christmas Mix up** | `dt-christmas-mix-up` | 36 / 36 | 36 eps | HLS/MP4 | ✅ Verificado |
| **Cinderella Bears the Mafia Boss's Child** | `dt-cinderella-bears-the-mafia-bosss-child-3` | 65 / 65 | 65 eps | HLS/MP4 | ✅ Verificado |
| **Cinderella Bears the Mafia Boss's Child** | `dt-cinderella-bears-the-mafia-bosss-child-4` | 65 / 65 | 65 eps | HLS/MP4 | ✅ Verificado |
| **Cinderella Bears the Mafia Boss's Child** | `dt-cinderella-bears-the-mafia-bosss-child-6` | 62 / 62 | 62 eps | HLS/MP4 | ✅ Verificado |
| **Cinderella Bears the Mafia Boss's Child** | `dt-cinderella-bears-the-mafia-bosss-child-7` | 65 / 65 | 65 eps | HLS/MP4 | ✅ Verificado |
| **Cinderella's Dangerous Game** | `dt-cinderellas-dangerous-game` | 16 / 16 | 16 eps | HLS/MP4 | ✅ Verificado |
| **Cinderella's Revenge** | `dt-cinderellas-revenge-2` | 80 / 80 | 80 eps | HLS/MP4 | ✅ Verificado |
| **Cinta di Tengah Malam Berembun** | `dt-cinta-di-tengah-malam-berembun` | 94 / 94 | 94 eps | HLS/MP4 | ✅ Verificado |
| **Cinta yang Tak Sepatutnya** | `dt-cinta-yang-tak-sepatutnya` | 23 / 23 | 23 eps | HLS/MP4 | ✅ Verificado |
| **Claimed by My Ex's Godfather** | `dt-claimed-by-my-exs-godfather` | 40 / 40 | 40 eps | HLS/MP4 | ✅ Verificado |
| **Claimed by the Alien Warlords** | `dt-claimed-by-the-alien-warlords` | 30 / 30 | 30 eps | HLS/MP4 | ✅ Verificado |
| **Claimed by the Alpha King** | `dt-claimed-by-the-alpha-king` | 33 / 33 | 33 eps | HLS/MP4 | ✅ Verificado |
| **Claimed by the CEO** | `dt-claimed-by-the-ceo` | 51 / 51 | 51 eps | HLS/MP4 | ✅ Verificado |
| **Claimed by the Dragon** | `dt-claimed-by-the-dragon` | 41 / 41 | 41 eps | HLS/MP4 | ✅ Verificado |
| **Claimed by the Fox King** | `dt-claimed-by-the-fox-king` | 37 / 37 | 37 eps | HLS/MP4 | ✅ Verificado |
| **Claimed by the Godfather** | `dt-claimed-by-the-godfather` | 51 / 51 | 51 eps | HLS/MP4 | ✅ Verificado |
| **Claimed by the Mafia King** | `dt-claimed-by-the-mafia-king` | 10 / 10 | 10 eps | HLS/MP4 | ✅ Verificado |
| **Claimed by the Ruthless Alpha after Rejection** | `dt-claimed-by-the-ruthless-alpha-after-rejection-subtitled` | 27 / 27 | 27 eps | HLS/MP4 | ✅ Verificado |
| **Claimed by the Supreme Commander: The Outcast Luna** | `dt-claimed-by-the-supreme-commander-the-outcast-luna` | 53 / 53 | 53 eps | HLS/MP4 | ✅ Verificado |
| **Claimed By Three Vampire Brothers** | `dt-claimed-by-three-vampire-brothers` | 31 / 31 | 31 eps | HLS/MP4 | ✅ Verificado |
| **Clained by His Rival:The Siren's New Empire** | `dt-clained-by-his-rival-the-sirens-new-empire` | 20 / 20 | 20 eps | HLS/MP4 | ✅ Verificado |
| **Clara's Redemption** | `dt-claras-redemption` | 50 / 50 | 50 eps | HLS/MP4 | ✅ Verificado |
| **Clara's Redemption** | `dt-claras-redemption-2` | 43 / 43 | 43 eps | HLS/MP4 | ✅ Verificado |
| **Clara's Redemption** | `dt-claras-redemption-3` | 21 / 21 | 21 eps | HLS/MP4 | ✅ Verificado |
| **Clara's Redemption** | `dt-claras-redemption-4` | 46 / 46 | 46 eps | HLS/MP4 | ✅ Verificado |
| **Cloak of the Reaper: Forbidden Deal** | `dt-cloak-of-the-reaper-forbidden-deal` | 32 / 32 | 32 eps | HLS/MP4 | ✅ Verificado |
| **Clouded Promise** | `dt-clouded-promise` | 67 / 67 | 67 eps | HLS/MP4 | ✅ Verificado |
| **COLD BOSS‘S SECRETS STAND-IN LOVE** | `dt-cold-bosss-secrets-stand-in-love-3` | 60 / 60 | 60 eps | HLS/MP4 | ✅ Verificado |
| **COLD BOSS‘S SECRETS STAND-IN LOVE** | `dt-cold-bosss-secrets-stand-in-love-4` | 60 / 60 | 60 eps | HLS/MP4 | ✅ Verificado |
| **COLD BOSS‘S SECRETS STAND-IN LOVE** | `dt-cold-bosss-secrets-stand-in-love-5` | 60 / 60 | 60 eps | HLS/MP4 | ✅ Verificado |
| **COLD BOSS‘S SECRETS STAND-IN LOVE** | `dt-cold-bosss-secrets-stand-in-love-6` | 60 / 60 | 60 eps | HLS/MP4 | ✅ Verificado |
| **COLD BOSS‘S SECRETS STAND-IN LOVE** | `dt-cold-bosss-secrets-stand-in-love-7` | 60 / 60 | 60 eps | HLS/MP4 | ✅ Verificado |
| **COLD BOSS‘S SECRETS STAND-IN LOVE** | `dt-cold-bosss-secrets-stand-in-love-8` | 60 / 60 | 60 eps | HLS/MP4 | ✅ Verificado |
| **Cold CEO’s Late Cry** | `dt-cold-ceos-late-cry` | 77 / 77 | 77 eps | HLS/MP4 | ✅ Verificado |
| **Cold CEO's Only Sweet Wife** | `dt-cold-ceos-only-sweet-wife` | 38 / 38 | 38 eps | HLS/MP4 | ✅ Verificado |
| **Cold CEO's Only Sweet Wife** | `dt-cold-ceos-only-sweet-wife-10` | 80 / 80 | 80 eps | HLS/MP4 | ✅ Verificado |
| **Cold CEO's Only Sweet Wife** | `dt-cold-ceos-only-sweet-wife-11` | 79 / 79 | 79 eps | HLS/MP4 | ✅ Verificado |
| **Cold CEO's Only Sweet Wife** | `dt-cold-ceos-only-sweet-wife-2` | 60 / 60 | 60 eps | HLS/MP4 | ✅ Verificado |
| **Cold CEO's Only Sweet Wife** | `dt-cold-ceos-only-sweet-wife-3` | 52 / 52 | 52 eps | HLS/MP4 | ✅ Verificado |
| **Cold CEO's Only Sweet Wife** | `dt-cold-ceos-only-sweet-wife-4` | 59 / 59 | 59 eps | HLS/MP4 | ✅ Verificado |
| **Cold CEO's Only Sweet Wife** | `dt-cold-ceos-only-sweet-wife-5` | 80 / 80 | 80 eps | HLS/MP4 | ✅ Verificado |
| **Cold CEO's Only Sweet Wife** | `dt-cold-ceos-only-sweet-wife-6` | 70 / 70 | 70 eps | HLS/MP4 | ✅ Verificado |
| **Cold CEO's Only Sweet Wife** | `dt-cold-ceos-only-sweet-wife-7` | 34 / 34 | 34 eps | HLS/MP4 | ✅ Verificado |
| **Cold CEO's Only Sweet Wife** | `dt-cold-ceos-only-sweet-wife-8` | 70 / 70 | 70 eps | HLS/MP4 | ✅ Verificado |
| **Cold CEO's Only Sweet Wife** | `dt-cold-ceos-only-sweet-wife-9` | 80 / 80 | 80 eps | HLS/MP4 | ✅ Verificado |
| **Cold Wave** | `dt-cold-wave` | 12 / 12 | 12 eps | HLS/MP4 | ✅ Verificado |
| **Comeback At The Awards** | `dt-comeback-at-the-awards-3` | 29 / 29 | 29 eps | HLS/MP4 | ✅ Verificado |
| **Comeback At The Awards** | `dt-comeback-at-the-awards-5` | 18 / 18 | 18 eps | HLS/MP4 | ✅ Verificado |
| **Complete Submission of the Savage Dog** | `dt-complete-submission-of-the-savage-dog` | 10 / 10 | 10 eps | HLS/MP4 | ✅ Verificado |
| **Concubine's Gambit** | `dt-concubine-s-gambit` | 47 / 47 | 47 eps | HLS/MP4 | ✅ Verificado |
| **Confessions of a Vegas Showgirl** | `dt-confessions-of-a-vegas-showgirl` | 67 / 67 | 67 eps | HLS/MP4 | ✅ Verificado |
| **Confined by Obsessive Love** | `dt-confined-by-obsessive-love` | 85 / 85 | 85 eps | HLS/MP4 | ✅ Verificado |
| **Conquer Four Heroines to Rise** | `dt-conquer-four-heroines-to-rise` | 46 / 46 | 46 eps | HLS/MP4 | ✅ Verificado |
| **Consumed by Him Day and Night(Dubbed)** | `dt-consumed-by-him-day-and-nightdubbed` | 68 / 68 | 68 eps | HLS/MP4 | ✅ Verificado |
| **Contract Bride Forbidden Love** | `dt-contract-bride-forbidden-love` | 120 / 120 | 120 eps | HLS/MP4 | ✅ Verificado |
| **Contract Bride Forbidden Love** | `dt-contract-bride-forbidden-love-2` | 15 / 15 | 15 eps | HLS/MP4 | ✅ Verificado |
| **Contract Bride Forbidden Love** | `dt-contract-bride-forbidden-love-3` | 63 / 63 | 63 eps | HLS/MP4 | ✅ Verificado |
| **Contract Bride Forbidden Love** | `dt-contract-bride-forbidden-love-4` | 15 / 15 | 15 eps | HLS/MP4 | ✅ Verificado |
| **CONTRACT CRISIS** | `dt-contract-crisis-3` | 80 / 80 | 80 eps | HLS/MP4 | ✅ Verificado |
| **CONTRACT CRISIS** | `dt-contract-crisis-4` | 80 / 80 | 80 eps | HLS/MP4 | ✅ Verificado |
| **Contract Love Trap** | `dt-contract-love-trap` | 70 / 70 | 70 eps | HLS/MP4 | ✅ Verificado |
| **Contract Nanny: The Pilot's Caged Obsession** | `dt-contract-nanny-the-pilots-caged-obsession-4` | 15 / 15 | 15 eps | HLS/MP4 | ✅ Verificado |
| **Contract Nanny: The Pilot's Caged Obsession** | `dt-contract-nanny-the-pilots-caged-obsession-5` | 15 / 15 | 15 eps | HLS/MP4 | ✅ Verificado |
| **Contract To Love** | `dt-contract-to-love-2` | 80 / 80 | 80 eps | HLS/MP4 | ✅ Verificado |
| **Corrupting My Billionaire Boss's Heart** | `dt-corrupting-my-billionaire-bosss-heart` | 82 / 82 | 82 eps | HLS/MP4 | ✅ Verificado |
| **Cost of Wrong Love:A BILLIONAIRE'S Repentance** | `dt-cost-of-wrong-love-a-billionaires-repentance-3` | 80 / 80 | 80 eps | HLS/MP4 | ✅ Verificado |
| **Could Have Heard Your Heartbeat** | `dt-could-have-heard-your-heartbeat` | 69 / 69 | 69 eps | HLS/MP4 | ✅ Verificado |
| **Countdown to Death:All Villains Game** | `dt-countdown-to-death-all-villains-game-3` | 15 / 15 | 15 eps | HLS/MP4 | ✅ Verificado |
| **Countdown to Death:All Villains Game** | `dt-countdown-to-death-all-villains-game-4` | 15 / 15 | 15 eps | HLS/MP4 | ✅ Verificado |
| **Countdown to Death:All Villains Game** | `dt-countdown-to-death-all-villains-game-5` | 15 / 15 | 15 eps | HLS/MP4 | ✅ Verificado |
| **Country Girl, CEO’s Wife** | `dt-country-girl-ceos-wife` | 56 / 56 | 56 eps | HLS/MP4 | ✅ Verificado |
| **Country Girl, CEO’s Wife(Dubbed)** | `dt-country-girl-ceos-wife-dubbed` | 68 / 68 | 68 eps | HLS/MP4 | ✅ Verificado |
| **Country Mom's Urban Victory** | `dt-country-moms-urban-victory` | 57 / 57 | 57 eps | HLS/MP4 | ✅ Verificado |
| **Court Intrigues (Dubbed)** | `dt-court-intrigues-2` | 74 / 74 | 74 eps | HLS/MP4 | ✅ Verificado |
| **Courtship a Hundred Times** | `dt-courtship-a-hundred-times` | 80 / 80 | 80 eps | HLS/MP4 | ✅ Verificado |
| **Cowardly Ghost** | `dt-cowardly-ghost` | 9 / 9 | 9 eps | HLS/MP4 | ✅ Verificado |
| **Cowgirl’s Kingpin** | `dt-cowgirls-kingpin` | 30 / 30 | 30 eps | HLS/MP4 | ✅ Verificado |
| **Craving My StepBrother From Next Door** | `dt-craving-my-stepbrother-from-next-door-2` | 32 / 32 | 32 eps | HLS/MP4 | ✅ Verificado |
| **Crazy Animals Save the World (Dubbed)** | `dt-crazy-animals-save-the-world-2` | 58 / 58 | 58 eps | HLS/MP4 | ✅ Verificado |
| **Crazy Drama Under the Table** | `dt-crazy-drama-under-the-table` | 60 / 60 | 60 eps | HLS/MP4 | ✅ Verificado |
| **Crazy Drama Under the Table** | `dt-crazy-drama-under-the-table-2` | 60 / 60 | 60 eps | HLS/MP4 | ✅ Verificado |
| **Crazy Duke Fakes Frailty, Craving My Domination** | `dt-crazy-duke-fakes-frailty-craving-my-domination` | 15 / 15 | 15 eps | HLS/MP4 | ✅ Verificado |
| **Crazy Duke Fakes Frailty, Craving My Domination** | `dt-crazy-duke-fakes-frailty-craving-my-domination-2` | 15 / 15 | 15 eps | HLS/MP4 | ✅ Verificado |
| **Crazy Duke Fakes Frailty, Craving My Domination** | `dt-crazy-duke-fakes-frailty-craving-my-domination-3` | 41 / 41 | 41 eps | HLS/MP4 | ✅ Verificado |
| **Crazy for Love** | `dt-crazy-for-love` | 87 / 87 | 87 eps | HLS/MP4 | ✅ Verificado |
| **Crazy Revenge Catching Cheater at Opening Banquet** | `dt-crazy-revenge-catching-cheater-at-opening-banquet-2` | 57 / 57 | 57 eps | HLS/MP4 | ✅ Verificado |
| **Crazy Thing Called Love** | `dt-crazy-thing-called-love` | 76 / 76 | 76 eps | HLS/MP4 | ✅ Verificado |
| **Crazy Tycoon’s Obsession** | `dt-crazy-tycoons-obsession-3` | 8 / 8 | 8 eps | HLS/MP4 | ✅ Verificado |
| **Crazy Tycoon’s Obsession** | `dt-crazy-tycoons-obsession-4` | 15 / 15 | 15 eps | HLS/MP4 | ✅ Verificado |
| **Crean rosettes on the cake** | `dt-crean-rosettes-on-the-cake` | 35 / 35 | 35 eps | HLS/MP4 | ✅ Verificado |
| **Creation Itself Is Love** | `dt-creation-itself-is-love` | 51 / 51 | 51 eps | HLS/MP4 | ✅ Verificado |
| **Crepe and Cashier** | `dt-crepe-and-cashier` | 62 / 62 | 62 eps | HLS/MP4 | ✅ Verificado |
| **Cross-Era Detective​** | `dt-cross-era-detective` | 100 / 100 | 100 eps | HLS/MP4 | ✅ Verificado |
| **Crossing The Line With My Neighbor** | `dt-crossing-the-line-with-my-neighbor` | 42 / 42 | 42 eps | HLS/MP4 | ✅ Verificado |
| **Crown of Love and Retribution** | `dt-crown-of-love-and-retribution` | 54 / 54 | 54 eps | HLS/MP4 | ✅ Verificado |
| **Crown of Shadows: The Empress’s Revenge** | `dt-crown-of-shadows-the-empresss-revenge` | 98 / 98 | 98 eps | HLS/MP4 | ✅ Verificado |
| **Crown Prince, Don't Cry** | `dt-crown-prince-dont-cry` | 65 / 65 | 65 eps | HLS/MP4 | ✅ Verificado |
| **Crown Prince Who?** | `dt-crown-prince-who` | 60 / 60 | 60 eps | HLS/MP4 | ✅ Verificado |
| **Crowned in Blood** | `dt-crowned-in-blood` | 51 / 51 | 51 eps | HLS/MP4 | ✅ Verificado |
| **Crowned in Blood** | `dt-crowned-in-blood-2` | 56 / 56 | 56 eps | HLS/MP4 | ✅ Verificado |
| **CRUSH AGAIN This time, she holds the power** | `dt-crush-again-this-time-she-holds-the-power-2` | 60 / 60 | 60 eps | HLS/MP4 | ✅ Verificado |
| **Crush on the Girl Who Fell to Kingdom** | `dt-crush-on-the-girl-who-fell-to-kingdom` | 98 / 98 | 98 eps | HLS/MP4 | ✅ Verificado |
| **Cry For Losing Me** | `dt-cry-for-losing-me` | 47 / 47 | 47 eps | HLS/MP4 | ✅ Verificado |
| **Crying Over Characters (Dubbed)** | `dt-crying-over-characters` | 81 / 81 | 81 eps | HLS/MP4 | ✅ Verificado |
| **Cursed Blood, Abyssal Crown** | `dt-cursed-blood-abyssal-crown` | 35 / 35 | 35 eps | HLS/MP4 | ✅ Verificado |
| **Cursed Bloodlines: A Fortune Teller's Tale** | `dt-cursed-bloodlines-a-fortune-teller-s-tale` | 80 / 80 | 80 eps | HLS/MP4 | ✅ Verificado |
| **Cursed by Love** | `dt-cursed-by-love` | 6 / 6 | 6 eps | HLS/MP4 | ✅ Verificado |
| **Curtain Call for Love** | `dt-curtain-call-for-love` | 60 / 60 | 60 eps | HLS/MP4 | ✅ Verificado |
| **Cute Baby Assist, Daddy Can't Escape** | `dt-cute-baby-assist-daddy-cant-escape` | 70 / 70 | 70 eps | HLS/MP4 | ✅ Verificado |
| **Cute Royal on the Hunt: My Brothers** | `dt-cute-royal-on-the-hunt-my-brothers` | 16 / 16 | 16 eps | HLS/MP4 | ✅ Verificado |
| **cutie pie's plan** | `dt-cutie-pies-plan` | 33 / 33 | 33 eps | HLS/MP4 | ✅ Verificado |
| **Daddy Dominant's Good Girl** | `dt-daddy-dominants-good-girl` | 54 / 54 | 54 eps | HLS/MP4 | ✅ Verificado |
| **Daddy Drafted** | `dt-daddy-drafted` | 10 / 10 | 10 eps | HLS/MP4 | ✅ Verificado |
| **Daddy Forgot, but Mommy Remembers** | `dt-daddy-forgot-but-mommy-remembers` | 42 / 42 | 42 eps | HLS/MP4 | ✅ Verificado |
| **Daddy Hunt: CEO’s Baby Rescue** | `dt-daddy-hunt-ceos-baby-rescue` | 53 / 53 | 53 eps | HLS/MP4 | ✅ Verificado |
| **Daddy Hunt: The Five-Baby Squad** | `dt-daddy-hunt-the-five-baby-squad` | 31 / 31 | 31 eps | HLS/MP4 | ✅ Verificado |
| **Daddy I'm Your Lucky Star!** | `dt-daddy-im-your-lucky-star` | 61 / 61 | 61 eps | HLS/MP4 | ✅ Verificado |
| **Daddy, Pinky Promise** | `dt-daddy-pinky-promise` | 32 / 32 | 32 eps | HLS/MP4 | ✅ Verificado |
| **Daddy, This Is My Mommy** | `dt-daddy-this-is-my-mommy-2` | 100 / 100 | 100 eps | HLS/MP4 | ✅ Verificado |
| **Daddy, You Lost Your Little Princess** | `dt-daddy-you-lost-your-little-princess` | 36 / 36 | 36 eps | HLS/MP4 | ✅ Verificado |
| **Daddy's Got Girls and Guns** | `dt-daddys-got-girls-and-guns` | 61 / 61 | 61 eps | HLS/MP4 | ✅ Verificado |
| **Daddy's little LUCKY Charm NOT A POOR LITTLE THING** | `dt-daddys-little-lucky-charm-not-a-poor-little-thing-2` | 59 / 59 | 59 eps | HLS/MP4 | ✅ Verificado |
| **DADDY'S LOVE Never Too Late** | `dt-daddys-love-never-too-late-3` | 15 / 15 | 15 eps | HLS/MP4 | ✅ Verificado |
| **DADDY'S LOVE Never Too Late** | `dt-daddys-love-never-too-late-4` | 15 / 15 | 15 eps | HLS/MP4 | ✅ Verificado |
| **DADDY'S LOVE Never Too Late** | `dt-daddys-love-never-too-late-5` | 15 / 15 | 15 eps | HLS/MP4 | ✅ Verificado |
| **DADDY'S LOVE Never Too Late** | `dt-daddys-love-never-too-late-6` | 15 / 15 | 15 eps | HLS/MP4 | ✅ Verificado |
| **DADDY'S LOVE Never Too Late** | `dt-daddys-love-never-too-late-7` | 15 / 15 | 15 eps | HLS/MP4 | ✅ Verificado |
| **Daddy's Miracle Daughter(Dubbed)** | `dt-daddys-miracle-daughterdubbed` | 40 / 40 | 40 eps | HLS/MP4 | ✅ Verificado |
| **Damn! He is the Emperor!** | `dt-damn-he-is-the-emperor` | 61 / 61 | 61 eps | HLS/MP4 | ✅ Verificado |
| **Damn, I Hurt My Savior** | `dt-damn-i-hurt-my-savior` | 60 / 60 | 60 eps | HLS/MP4 | ✅ Verificado |
| **Damn! I'm the Richest Man** | `dt-damn-im-the-richest-man` | 93 / 93 | 93 eps | HLS/MP4 | ✅ Verificado |
| **Dancing with the Devil I Hated** | `dt-dancing-with-the-devil-i-hated` | 10 / 10 | 10 eps | HLS/MP4 | ✅ Verificado |
| **Dancing with the Devil I Hated** | `dt-dancing-with-the-devil-i-hated-2` | 6 / 6 | 6 eps | HLS/MP4 | ✅ Verificado |
| **Dancing with the Devil I Hated** | `dt-dancing-with-the-devil-i-hated-3` | 13 / 13 | 13 eps | HLS/MP4 | ✅ Verificado |
| **Dangerous Contract: Let Me Go, Mr. CEO** | `dt-dangerous-contract-let-me-go-mr-ceo` | 62 / 62 | 62 eps | HLS/MP4 | ✅ Verificado |
| **Dangerous Desire** | `dt-dangerous-desire` | 25 / 25 | 25 eps | HLS/MP4 | ✅ Verificado |
| **Dangerous Drop** | `dt-dangerous-drop` | 31 / 31 | 31 eps | HLS/MP4 | ✅ Verificado |
| **Dangerous Liaisons (Dubbed)** | `dt-dangerous-liaisons` | 95 / 95 | 95 eps | HLS/MP4 | ✅ Verificado |
| **Dangerous Touch** | `dt-dangerous-touch-2` | 30 / 30 | 30 eps | HLS/MP4 | ✅ Verificado |
| **Dark Lord** | `dt-dark-lord` | 64 / 64 | 64 eps | HLS/MP4 | ✅ Verificado |
| **Dark Lord (Dubbed)** | `dt-dark-lord-2` | 58 / 58 | 58 eps | HLS/MP4 | ✅ Verificado |
| **Dark Myth: The Unrivalled Knight** | `dt-dark-myth-the-unrivalled-knight` | 58 / 58 | 58 eps | HLS/MP4 | ✅ Verificado |
| **Dark Wedding** | `dt-dark-wedding` | 30 / 30 | 30 eps | HLS/MP4 | ✅ Verificado |
| **Darling, Call Me Dad** | `dt-darling-call-me-dad` | 100 / 100 | 100 eps | HLS/MP4 | ✅ Verificado |
| **Darling, You Were Here All Along** | `dt-darling-you-were-here-all-along` | 60 / 60 | 60 eps | HLS/MP4 | ✅ Verificado |
| **Date Me, Make Me Rich** | `dt-date-me-make-me-rich` | 36 / 36 | 36 eps | HLS/MP4 | ✅ Verificado |
| **Daughter-in-Law, I'm Not Your Love Rival** | `dt-daughter-in-law-im-not-your-love-rival` | 62 / 62 | 62 eps | HLS/MP4 | ✅ Verificado |
| **Daughter of Satan: Returned from Hell** | `dt-daughter-of-satan-returned-from-hell-3` | 15 / 15 | 15 eps | HLS/MP4 | ✅ Verificado |
| **Daughter of Satan: Returned from Hell** | `dt-daughter-of-satan-returned-from-hell-4` | 69 / 69 | 69 eps | HLS/MP4 | ✅ Verificado |
| **DAUGHTER OF ZEUS: THE QUEEN'S JUDGMENT** | `dt-daughter-of-zeus-the-queens-judgment-3` | 52 / 52 | 52 eps | HLS/MP4 | ✅ Verificado |
