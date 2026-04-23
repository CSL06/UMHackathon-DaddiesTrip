from .base_agent import BaseAgent
import datetime

class BookingAgent(BaseAgent):
    def get_details(self, compressed_draft, trip_summary):
        current_year = datetime.datetime.now().year
        today = datetime.date.today().isoformat()
        dest = trip_summary.get("destination", "the destination")
        requires_flight = trip_summary.get("requires_flight", True)
        travel_dates = trip_summary.get("travel_dates", "")
        duration = trip_summary.get("duration_days", 7)

        date_instruction = f"Travel dates: {travel_dates}." if travel_dates else f"Depart in {current_year}."

        system_prompt = f"""You are the Booking Agent for DaddiesTrip. Travellers depart from KUL, Malaysia.
Today is {today}. {date_instruction} All dates must be {current_year} or later. NEVER use past dates.

Return CONCISE JSON:
{{
  "destination_currency": "<ISO>",
  "destination_iata": "<IATA>",
  "destination_review": {{"name":"...","rating":"4.x/5","review_count":"...","review_comment":"short line"}},
  "flight_options": [/* 3 options if requires_flight, else [] */],
  "itinerary_details": [/* EXACTLY {duration} entries, one per day */]
}}

FLIGHTS (if requires_flight=true):
- Exactly 3 options with different airlines (e.g. AirAsia AK, Malaysia Airlines MH, Batik Air OD).
- "cost_myr"=per-person round-trip. departure.airport="KUL", return.airport=destination IATA.
- Include departure/return date, time, airline, airline_iata, cost_myr.
- "google_flights" URL with correct date.

PER DAY (you MUST output EXACTLY {duration} days — EVERY day needs hotel and food):
- "day": N
- "hotel": {{"name":"...","cost_myr":N,"rating":"4.x/5"}} — REQUIRED for EVERY day
- "activities": [{{"name":"...","cost_myr":N,"schedule":"HH:MM-HH:MM","transport_to_next":{{"mode":"walk|bus|metro|taxi","duration":"X min","estimated_cost_myr":0}}}}]
- For metro transport: specify the exact line/route name (e.g. "Tokyo Metro Ginza Line", "JR Yamanote Line")
- "food_recommendations": [{{"name":"...","avg_cost_myr":N}}]
- "daily_food_cost_myr": N
- "transportation": {{"route":"summary of day transit","cost_myr":N}}

Keep responses SHORT. Realistic costs for KUL→{dest}."""

        user_prompt = f"Trip: {trip_summary}\nItinerary to book: {compressed_draft}"
        return self.query(system_prompt, user_prompt, max_tokens=6000)
