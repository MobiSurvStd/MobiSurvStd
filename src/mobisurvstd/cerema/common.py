MODE_MAP = {
    1: "walking",  # Marche à pied.
    10: "bicycle:driver:traditional:shared",  # Conducteur VLS
    11: "bicycle:driver:traditional",  # Conducteur de vélo.
    12: "bicycle:passenger",  # Passager de vélo.
    13: "motorcycle:driver:moped",  # Conducteur de deux ou trois roues motorisés < 50 cm3.
    14: "motorcycle:passenger:moped",  # Passager de deux ou trois roues motorisés < 50 cm3.
    15: "motorcycle:driver:moto",  # Conducteur de deux ou trois roues motorisés >= 50 cm3
    16: "motorcycle:passenger:moto",  # Passager de deux ou trois roues motorisés >= 50 cm3.
    17: "motorcycle:driver",  # Conducteur de deux ou trois roues motorisés (si pas de détail sur la cylindrée).
    18: "motorcycle:passenger",  # Passager de deux ou trois roues motorisés (si pas de détail sur la cylindrée)..
    21: "car:driver",  # Conducteur de véhicule particulier (VP).
    22: "car:passenger",  # Passager de véhicule particulier (VP).
    31: "public_transit:urban:bus",  # Passager bus urbain (réseau ville centre).
    32: "public_transit:urban:tram",  # Passager tramway (réseau ville centre).
    33: "public_transit:urban:metro",  # Passager métro (réseau ville centre).
    34: "public_transit:urban:funicular",  # Note. Not documented. Used in Le Havre (and other surveys?).
    37: "public_transit:urban:demand_responsive",  # Transport à la demande (U ou IU)
    38: "public_transit:urban",  # Passager autres réseaux urbains ds aire enquête.
    39: "public_transit:urban",  # Passager autre réseau urbain hors AE
    41: "public_transit:urban:coach",  # Passager transports interurbains routiers et autres autocars (TER routiers, lignes régulières départementales, scolaires, périscolaires, occasionnel….).
    42: "public_transit:interurban:coach",  # Cars longues distances (Eurolines/Isilines, Ouibus, Flixbus…)).
    43: "public_transit:interurban:coach",  # Passagers autocars anciennes définitions
    51: "public_transit:interurban:other_train",  # Passager Train
    61: "taxi_or_VTC",  # Passager taxi.
    71: "employer_transport",  # Transport employeur (exclusivement)
    72: "public_transit:school",  # For Thionville 2012
    81: "truck:driver",  # Conducteur de fourgon, camionnette, camion (pour tournées professionnelles ou déplacements privés).
    82: "truck:passenger",  # Passager de fourgon, camionnette, camion (pour tournées professionnelles ou déplacements privés)..
    91: "water_transport",  # Transport Fluvial ou maritime.
    92: "airplane",  # Avion.
    93: "personal_transporter:non_motorized",  # Roller, skate, trottinette non électrique
    94: "wheelchair",  # Fauteuil roulant.
    95: "other",  # Autres modes (tracteur, engin agricole, quad, etc.).
    96: "personal_transporter:motorized",  # Petits engins électriques (trottinette, segway, solowheel, etc)
    97: "personal_transporter:unspecified",  # Roller, skate, trottinette électrique ou non (ancien code)
}


# For the EMC2 surveys, categories 17 and 18 have moved to 19 and 20, while 17 and 18 are now
# representing electric bicycle.
# Category 51 as been split from Train (general, interurban) to 4 distinct train modes.
# Category 61 as been split from taxi (general) to taxi and VTC.
EMC2_MODE_MAP = MODE_MAP.copy()
EMC2_MODE_MAP.update(
    {
        17: "bicycle:driver:electric",  # Conducteur de vélo Assistance Electrique
        18: "bicycle:driver:electric:shared",  # Conducteur de vélo Assistance Electrique en Libre Service
        19: "motorcycle:driver",  # Conducteur de deux ou trois roues motorisés (si pas de détail sur la cylindrée).
        20: "motorcycle:passenger",  # Passager de deux ou trois roues motorisés (si pas de détail sur la cylindrée)..
        51: "public_transit:interurban:TGV",  # Passager TGV
        52: "public_transit:urban:TER",  # Passager train TER
        53: "public_transit:interurban:intercités",  # Passagers autres trains (Intercité, TET)
        54: "public_transit:interurban:other_train",  # Passager train non précisé
        61: "taxi",  # Passager taxi.
        62: "VTC",  # Passager VTC
    }
)

# For open-data Nantes, some new modes are defined.
NANTES_MODE_MAP = MODE_MAP.copy()
NANTES_MODE_MAP.update(
    {
        19: "bicycle:driver:traditional:shared",  # Conducteur de vélo Libre-Service ou location
        30: "public_transit:urban:bus",  # Passager bus réseau Cap Atlantique
        34: "public_transit:urban:bus",  # Passager bus réseau Nantes TAN (y compris express)
        35: "public_transit:urban:bus",  # Passager Chronobus (C1 à C7) réseau Nantes TAN
        36: "public_transit:urban:bus",  # Passager hélYce BHNS réseau ST Nazaire STRAN
        37: "public_transit:urban:bus",  # Passager bus réseau ST Nazaire STRAN (lignes U urbaines, Ty Bus, C1, SD, Zénibus)
        38: "public_transit:urban:demand_responsive",  # Transport à la demande et PMR (Proxitan à Nantes, Liberty Bus et Ty Bus Taxi à St Nazaire, Lila et Abeille)
        52: "public_transit:urban:TER",  # Passager TER
        53: "public_transit:interurban:other_train",  # Passager autre train (TGV, Corail, InterCités et Grandes Lignes…)
        73: "public_transit:school",  # Passagers transports scolaires (réseau STRAN)
    }
)
