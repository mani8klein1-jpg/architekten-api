# Datenbank befüllen

from database import SessionLocal, Foerderung

def seed_database():
    db = SessionLocal()

    foerderungen = [
        Foerderung(
            name="Dachdämmung",
            massnahme="dach",
            gebaeudetyp="einfamilienhaus",
            zuschuss="BAFA - 20% Zuschuss",
            details="Förderung für Dämmung von Dach und oberster Geschossdecke.",
            max_foerderung=5000.0
        ),
        Foerderung(
            name="Heizungstausch",
            massnahme="heizung",
            gebaeudetyp="einfamilienhaus",
            zuschuss="KfW - bis zu 35% Zuschuss",
            details="Förderung für den Austausch alter Heizungen gegen klimafreundliche Alternativen.",
            max_foerderung=15000.0
        ),
        Foerderung(
            name="Heizungstausch (Mehrfamilienhaus)",
            massnahme="heizung",
            gebaeudetyp="mehrfamilienhaus",
            zuschuss="KfW - bis zu 35% Zuschuss",
            details="Bei Mehrfamilienhäusern sind oft höhere Fördersummen möglich.",
            max_foerderung=30000.0
        ),
        Foerderung(
            name="Fenster austauschen",
            massnahme="fenster",
            gebaeudetyp="einfamilienhaus",
            zuschuss="BAFA - 15% Zuschuss",
            details="Förderung für energieeffiziente Fenster mit U-Wert < 1,0.",
            max_foerderung=4000.0
        ),
        Foerderung(
            name="Gebäudehülle dämmen",
            massnahme="gebaeudehuelle",
            gebaeudetyp="einfamilienhaus",
            zuschuss="BAFA - 20% Zuschuss + KfW-Darlehen",
            details="Förderung für Außenwand-, Dach- und Kellerdeckendämmung.",
            max_foerderung=10000.0
        ),
        Foerderung(
            name="Energieeffizienter Neubau",
            massnahme="neubau",
            gebaeudetyp="einfamilienhaus",
            zuschuss="KfW - bis zu 150.000 € Darlehen",
            details="KfW-Förderung für Neubauten mit hohem Energieeffizienz-Standard.",
            max_foerderung=150000.0
        ),
    ]

    db.add_all(foerderungen)
    db.commit()
    db.close()
    print("✅ Förderdaten erfolgreich eingefügt!")

if __name__ == "__main__":
    seed_database()