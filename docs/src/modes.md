<style>
    .content main {
        max-width: 1400px;
    }
</style>

# Mode comparison

Each survey uses its own list of transportation modes.
The table below shows, for each MobiSurvStd mode (variables [`main_mode`](format/trips.md#main_mode)
of trips and [`mode`](format/legs.md#mode) of legs), the original modalities that are mapped to it
in each survey type.
Original modalities are given as `code` followed by the label from the survey's documentation (in
French).
A dash (–) means that the survey type has no modality mapped to that mode.

The EDGT, EDVM, and EMD surveys share the same mode definitions.
The EMC² surveys use the same definitions too, except for electric bicycles, motorcycles (unspecified
size), trains, taxis, and VTC, which use new or different codes.

Note that some public-transit modalities and the car / truck distinction are not fully consistent across survey types.

| Mode | EMC² | EDGT / EDVM / EMD | EGT2010 | EGT2020 | EMP2019 | EMG2023 |
| --- | --- | --- | --- | --- | --- | --- |
| `walking` | `1` Marche à pied | `1` Marche à pied | `1` Marche à pied | `B611` Marche + A pied<br>`B61` Marche + non réponse<br>`B612` *(undocumented)*<br>`B613` *(undocumented)* | `1.1` Uniquement marche à pied<br>`1.2` Porté, transporté en poussette | `MAP` Marche à pied |
| `bicycle:driver` | – | – | – | `B40` Vélo | `2.1` Bicyclette, tricycle (y compris à assistance électrique) sauf vélo en libre-service | – |
| `bicycle:driver:shared` | – | – | `60` Véli'b<br>`61` Autre vélo en libre service | – | `2.2` Vélo en libre-service | – |
| `bicycle:driver:traditional` | `11` Conducteur de vélo | `11` Conducteur de vélo | `62` Vélo personnel | – | – | `VELO` Vélo |
| `bicycle:driver:traditional:shared` | `10` Conducteur VLS | `10` Conducteur VLS | – | – | – | – |
| `bicycle:driver:electric` | `17` Conducteur de vélo Assistance Electrique | – | `63` Vélo personnel à assistance électrique | – | – | `VAE` Vélo à assistance électrique |
| `bicycle:driver:electric:shared` | `18` Conducteur de vélo Assistance Electrique en Libre Service | – | – | – | – | – |
| `bicycle:passenger` | `12` Passager de vélo | `12` Passager de vélo | – | – | – | – |
| `motorcycle:driver` | `19` Conducteur de deux ou trois roues motorisés (si pas de détail sur la cylindrée) | `17` Conducteur de deux ou trois roues motorisés (si pas de détail sur la cylindrée) | `55` Conducteur véhicule à 2 (ou 3) roues à moteur immatriculé | `B31` Moto, scooter + Conducteur | `2.7` Motocycles sans précision (y compris quads) | `2RM` Deux-roues motorisé |
| `motorcycle:passenger` | `20` Passager de deux ou trois roues motorisés (si pas de détail sur la cylindrée) | `18` Passager de deux ou trois roues motorisés (si pas de détail sur la cylindrée) | `75` Passager d'un véhicule à 2 (ou 3) roues à moteur immatriculé | `B32` Moto, scooter + Passager | – | – |
| `motorcycle:driver:moped` | `13` Conducteur de deux ou trois roues motorisés < 50 cm3 | `13` Conducteur de deux ou trois roues motorisés < 50 cm3 | `54` Conducteur véhicule à 2 (ou 3) roues à moteur non immatriculé | – | `2.3` Cyclomoteur (2 roues de moins de 50 cm3) - Conducteur | – |
| `motorcycle:passenger:moped` | `14` Passager de deux ou trois roues motorisés < 50 cm3 | `14` Passager de deux ou trois roues motorisés < 50 cm3 | `74` Passager d'un véhicule à 2 (ou 3) roues à moteur non immatriculé | – | `2.4` Cyclomoteur (2 roues de moins de 50 cm3) - Passager | – |
| `motorcycle:driver:moto` | `15` Conducteur de deux ou trois roues motorisés >= 50 cm3 | `15` Conducteur de deux ou trois roues motorisés >= 50 cm3 | – | – | `2.5` Moto (plus de 50 cm3) - Conducteur (y compris avec side-car et scooter à trois roues) | – |
| `motorcycle:passenger:moto` | `16` Passager de deux ou trois roues motorisés >= 50 cm3 | `16` Passager de deux ou trois roues motorisés >= 50 cm3 | – | – | `2.6` Moto (plus de 50 cm3) - Passager (y compris avec side-car et scooter à trois roues) | – |
| `car:driver` | `21` Conducteur de véhicule particulier (VP) | `21` Conducteur de véhicule particulier (VP) | `50` Conducteur voiture particulière<br>`51` Conducteur dans un système de covoiturage organisé<br>`52` Conducteur véhicule utilitaire 800 à 1 000 kg | `B21` Voiture + Conducteur | `3.1` Voiture, VUL, voiturette… - Conducteur<br>`3.3` Voiture, VUL, voiturette… - Tantôt conducteur tantôt passager<br>`3.4` Trois ou quatre roues sans précision | `VPC` Voiture particulière en tant que conducteur |
| `car:passenger` | `22` Passager de véhicule particulier (VP) | `22` Passager de véhicule particulier (VP) | `70` Passager d'une voiture particulière<br>`71` Passager dans un système de covoiturage organisé<br>`72` Passager d'un véhicule utilitaire 800 à 1 000 kg | `B22` Voiture + Passager | `3.2` Voiture, VUL, voiturette… - Passager | `VPP` Voiture particulière en tant que passager |
| `taxi` | `61` Passager taxi | – | `35` Taxi | `B511` Taxi, Uber ou autres VTC + Taxi (artisan taxi, G7, taxis-bleus…) | – | – |
| `VTC` | `62` Passager VTC | – | – | `B512` Taxi, Uber ou autres VTC + Über<br>`B513` Taxi, Uber ou autres VTC + Autres VTC | – | – |
| `taxi_or_VTC` | – | `61` Passager taxi | – | `B51` Taxi, Uber ou autres VTC + non réponse | `4.1` Taxi (individuel, collectif), VTC | `TAXI/VTC` Taxi ou Vtc |
| `public_transit:urban` | `38` Passager autres réseaux urbains ds aire enquête<br>`39` Passager autre réseau urbain hors AE | `38` Passager autres réseaux urbains ds aire enquête<br>`39` Passager autre réseau urbain hors AE | – | `B15` Transports collectifs : Autres<br>`B524` Transports collectifs hors Ile-de-France (bus, car, tramway, métro, TER…) | `5.10` Autres transports urbains et régionaux (sans précision) | – |
| `public_transit:urban:bus` | `31` Passager bus urbain (réseau ville centre) | `31` Passager bus urbain (réseau ville centre) | `15` TVM<br>`16` Autobus Paris RATP (Numéro de ligne inférieur à 100)<br>`17` Autobus de banlieue RATP (Numéro de ligne supérieur à 100)<br>`18` Autre autobus de banlieue OPTILE (ex APTR,ADATRIF)<br>`19` Noctilien (bus de nuit ex Noctambus) | `B14` Transports collectifs : Bus | `5.1` Autobus urbain, trolleybus | `BUS` Bus |
| `public_transit:urban:coach` | `41` Passager transports interurbains routiers et autres autocars (TER routiers, lignes régulières départementales, scolaires, périscolaires, occasionnel….) | `41` Passager transports interurbains routiers et autres autocars (TER routiers, lignes régulières départementales, scolaires, périscolaires, occasionnel….) | – | – | `5.3` Autocar de ligne (sauf SNCF)<br>`5.5` Autocar TER | – |
| `public_transit:urban:tram` | `32` Passager tramway (réseau ville centre) | `32` Passager tramway (réseau ville centre) | `14` Tramway (y compris le T4) | `B13` Transports collectifs : Tramway | `5.6` Tramway | `TRAM` Tramway |
| `public_transit:urban:metro` | `33` Passager métro (réseau ville centre) | `33` Passager métro (réseau ville centre) | `12` Orly-Val<br>`13` Métro | `B12` Transports collectifs : Métro | `5.7` Métro, VAL, funiculaire | `METRO` Métro |
| `public_transit:urban:funicular` | `34` *(undocumented)* | `34` *(undocumented)* | – | – | – | – |
| `public_transit:urban:rail` | – | – | `10` Train de banlieue SNCF(Transilien)<br>`11` RER (Lignes A, B, C, D, E ou Eole) | `B11` Transports collectifs : Train ou RER | `5.8` RER, SNCF banlieue | `RER/TRAIN` RER ou Train du réseau régional francilien<br>`RER/METRO` *(undocumented)* |
| `public_transit:urban:TER` | `52` Passager train TER | – | `43` TER | – | `5.9` TER | – |
| `public_transit:urban:demand_responsive` | `37` Transport à la demande (U ou IU) | `37` Transport à la demande (U ou IU) | `30` Transport à la demande | `B527` Autres modes + Transport à la demande (TAD) | – | `TAD` Transport à la demande |
| `public_transit:interurban:coach` | `42` Cars longues distances (Eurolines/Isilines, Ouibus, Flixbus…)<br>`43` Passagers autocars anciennes définitions | `42` Cars longues distances (Eurolines/Isilines, Ouibus, Flixbus…)<br>`43` Passagers autocars anciennes définitions | – | `B529` Cars interurbains dits "cars Macron" | `5.4` Autre autocar (affrètement, service spécialisé) | – |
| `public_transit:interurban:TGV` | `51` Passager TGV | – | `41` TGV | – | `6.1` Train à grande vitesse, 1ère classe (TGV, Eurostar, etc.)<br>`6.2` Train à grande vitesse, 2ème classe (TGV, Eurostar, etc.) | – |
| `public_transit:interurban:intercités` | `53` Passagers autres trains (Intercité, TET) | – | – | – | – | – |
| `public_transit:interurban:other_train` | `54` Passager train non précisé | `51` Passager Train | `42` Grande ligne SNCF autre que TGV | `B522` TER ou TGV | `6.3` Autre train, 1ère classe<br>`6.4` Autre train, 2ème classe<br>`6.5` Train, sans précision | `TGV/INTERCITES/TER` TGV ou Intercités ou Train express régional |
| `public_transit:school` | `72` *(undocumented)* | `72` *(undocumented)* | `32` Ramassage scolaire | `B525` Autres modes + Ramassage scolaire | `4.4` Ramassage scolaire | – |
| `reduced_mobility_transport` | – | – | `33` Société de service spécialisée dans le transport des handicapés | `B528` Autres modes + Transport spécialisé pour les personnes à mobilité réduite (dont PAM) | `4.2` Transport spécialisé (handicapé) | – |
| `employer_transport` | `71` Transport employeur (exclusivement) | `71` Transport employeur (exclusivement) | `31` Transports employeurs | `B526` Autres modes + Transport employeur, navette d'entreprise | `4.3` Ramassage organisé par l'employeur | – |
| `truck:driver` | `81` Conducteur de fourgon, camionnette, camion (pour tournées professionnelles ou déplacements privés) | `81` Conducteur de fourgon, camionnette, camion (pour tournées professionnelles ou déplacements privés) | `53` Conducteur véhicule utilitaire de 1 000 kg ou plus | – | – | `VUL` Véhicule utilitaire léger |
| `truck:passenger` | `82` Passager de fourgon, camionnette, camion (pour tournées professionnelles ou déplacements privés) | `82` Passager de fourgon, camionnette, camion (pour tournées professionnelles ou déplacements privés) | `73` Passager véhicule utilitaire de 1 000 kg ou plus | – | – | – |
| `water_transport` | `91` Transport Fluvial ou maritime | `91` Transport Fluvial ou maritime | `20` Bateau bus - Voguéo | – | `5.2` Navette fluviale<br>`8.1` Bateau | – |
| `airplane` | `92` Avion | `92` Avion | `40` Avion | `B521` Avion | `7.1` Avion, classe première ou affaires<br>`7.2` Avion, classe premium économique<br>`7.3` Avion, classe économique | `AVION` Avion |
| `wheelchair` | `94` Fauteuil roulant | `94` Fauteuil roulant | `80` Fauteuil roulant avec ou sans moteur, voiturette (handicapés) | `B622` Fauteuil roulant + Fauteuil roulant motorisé ou scooter PMR<br>`B621` Fauteuil roulant + Fauteuil roulant manuel<br>`B62` Fauteuil roulant + non réponse | `1.4` Fauteuil roulant (y compris motorisé) | – |
| `personal_transporter:non_motorized` | `93` Roller, skate, trottinette non électrique | `93` Roller, skate, trottinette non électrique | – | `B614` Marche + Trottinette<br>`B616` Marche + Autres | – | – |
| `personal_transporter:motorized` | `96` Petits engins électriques (trottinette, segway, solowheel, etc) | `96` Petits engins électriques (trottinette, segway, solowheel, etc) | – | `B615` Marche + Trottinette électrique | – | `TROTTINETTE` Trottinette électrique |
| `personal_transporter:unspecified` | `97` Roller, skate, trottinette électrique ou non (ancien code) | `97` Roller, skate, trottinette électrique ou non (ancien code) | `81` Rollers, skate, trottinette | – | `1.3` Rollers, trottinette | – |
| `other` | `95` Autres modes (tracteur, engin agricole, quad, etc.) | `95` Autres modes (tracteur, engin agricole, quad, etc.) | `34` Autres transports privés collectifs (navettes, …)<br>`82` Autre moyen de transport | `B52` Autres modes + non réponse<br>`B523` Autres modes + Autre | `9.1` Autre | `AUTRE` Autre mode (skateboard, roller, ...) |

Notes:

- Codes marked *(undocumented)* appear in the data but are not documented:
  - In EDGT / EDVM / EMD / EMC², code `34` is used in Le Havre (and possibly other surveys) and code
    `72` in Thionville 2012.
  - In EGT2020, codes `B612` and `B613` are assumed to be walking because they start with `B61`
    ("Marche").
  - In EMG2023, the single entry `RER/METRO` is assumed to be a typo for `RER/TRAIN`.
- In EMP2019, codes `9999` and `vide` (no answer) are mapped to null.
