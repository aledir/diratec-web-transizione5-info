"""Funzioni per il calcolo dello score dei lead."""
import re
from cat.log import log

def calculate_lead_score(azienda_data, investimenti_data):
    """Calcola lo score del lead in base ai dati forniti"""
    score = 0

    # Punteggio per dimensione/settore azienda
    if azienda_data.get("dimensione"):
        dimensione = azienda_data["dimensione"].lower()
        if "grande" in dimensione:
            score += 20
        elif "media" in dimensione:
            score += 15
        elif "piccola" in dimensione:
            score += 10

    # Punteggio per budget di investimento
    if investimenti_data.get("budget"):
        budget_str = investimenti_data["budget"].lower()

        # Estrai il valore numerico
        budget_match = re.search(r'(\d+(?:\.\d+)?)', budget_str.replace(',', '.'))
        if budget_match:
            budget = float(budget_match.group(1))

            # Determina l'unità (k, K, mila, milioni, M, ecc.)
            unit_multiplier = 1
            if re.search(r'[kK]|mila', budget_str):
                unit_multiplier = 1000
            elif re.search(r'[mM]|milion', budget_str):
                unit_multiplier = 1000000

            # Calcola il budget reale
            real_budget = budget * unit_multiplier

            # Assegna il punteggio in base al budget
            if real_budget >= 1000000:  # > 1M€
                score += 30
            elif real_budget >= 500000:  # > 500K€
                score += 20
            elif real_budget >= 100000:  # > 100K€
                score += 10

    # Punteggio per tempistiche
    if investimenti_data.get("tempistiche"):
        tempistiche = investimenti_data["tempistiche"].lower()
        if "un mese" in tempistiche or "immediato" in tempistiche or "subito" in tempistiche:
            score += 25
        elif "tre mesi" in tempistiche or "trimestre" in tempistiche:
            score += 15
        else:
            score += 5

    return score

def get_lead_status(score):
    """Determina lo stato del lead in base allo score"""
    if score >= 70:
        return "qualificato"
    elif score >= 40:
        return "interessante"
    else:
        return "da approfondire"