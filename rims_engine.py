import os
import json
from datetime import datetime

class RIMSEngine:
    """
    RIMS 9 Newsjacking Automation Engine
    Automates the process from Google Trends capture to production-ready news pages.
    """

    def __init__(self, workspace_path):
        self.workspace_path = workspace_path
        self.template_path = os.path.join(workspace_path, "rims_template.html")
        self.output_dir = os.path.join(workspace_path, "news")
        
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def extract_trends(self):
        """
        Placeholder for trend extraction. 
        In real execution, this pulls from Google Trends CSV or Browser scrape.
        """
        print("[Engine] Extracting trends from Google Trends...")
        # Logic to be implemented or provided by browser tool results
        return []

    def scout_trend(self, trend_data):
        """
        Processes trend data through the 'Scout GPT' logic.
        Format based on user documentation.
        """
        print(f"[Engine] Scouting trend: {trend_data['name']}...")
        # Returns structured scouting report
        return {}

    def generate_article(self, scouting_report):
        """
        Processes scouting report through 'Writer/Designer GPT' logic.
        Generates Sarah Jenkins style Special Report.
        """
        print("[Engine] Generating Special Report article...")
        # Returns full article components
        return {}

    def generate_creatives(self, article_data):
        """
        Processes article data through 'Image Architect' and 'Notification Generator' logic.
        """
        print("[Engine] Generating image prompts and push notifications...")
        return {}

    def match_niche(self, scout_report):
        """
        Determines the monetization niche based on the scout report.
        """
        prompt = scout_report.get('primary_emotional_trigger', '').lower()
        content = str(scout_report).lower()
        
        if 'health' in content or 'weight' in content: return 'Health'
        if 'survival' in content or 'emergency' in content or 'safety' in content: return 'Survival'
        if 'tech' in content or 'security' in content or 'digital' in content: return 'Tech'
        
        return 'Wealth' # Default fallback

    def get_contextual_monetization(self, niche):
        """
        Pulls matched offers from offers_db.json.
        """
        with open(os.path.join(self.workspace_path, "offers_db.json"), 'r') as f:
            db = json.load(f)
            
        niche_data = db['categories'].get(niche, db['categories']['Wealth'])
        return niche_data

    def rebuild_home_page(self):
        """
        Scans the news directory and rebuilds the root index.html based on home_template.html.
        """
        print("[Engine] Rebuilding site homepage...")
        
        folders = [f for f in os.listdir(self.output_dir) if os.path.isdir(os.path.join(self.output_dir, f))]
        stories = []
        
        for folder in folders:
            meta_path = os.path.join(self.output_dir, folder, "meta.json")
            if os.path.exists(meta_path):
                with open(meta_path, 'r') as f:
                    stories.append(json.load(f))
        
        # Sort by date descending
        stories.sort(key=lambda x: x.get('date', ''), reverse=True)
        
        html_list = ""
        for s in stories:
            html_list += f"""
            <div class="story-card">
                <img src="news/{s['slug']}/assets/hero.png" class="story-img" alt="{s['headline']}">
                <div class="story-content">
                    <div class="story-meta">{s['category']}</div>
                    <a href="news/{s['slug']}/index.html" class="story-title">{s['headline']}</a>
                    <p class="story-excerpt">{s['dek']}</p>
                </div>
            </div>
            """
            
        with open(os.path.join(self.workspace_path, "home_template.html"), 'r') as f:
            home_html = f.read()
            
        home_html = home_html.replace("{{STORIES_LIST}}", html_list)
        home_html = home_html.replace("{{FALLBACK_LINK}}", "https://welcometoaurum.com")
        
        with open(os.path.join(self.workspace_path, "index.html"), 'w') as f:
            f.write(home_html)
            
        print(f"[Engine] Homepage refreshed with {len(stories)} stories.")

    def assemble_page(self, topic_slug, content, scout_report):
        """
        Injects article data and contextual ads into rims_template.html.
        """
        print(f"[Engine] Assembling page for {topic_slug}...")
        
        niche = self.match_niche(scout_report)
        monetization = self.get_contextual_monetization(niche)
        
        page_dir = os.path.join(self.output_dir, topic_slug)
        assets_dir = os.path.join(page_dir, "assets")
        
        if not os.path.exists(assets_dir):
            os.makedirs(assets_dir)
            
        # Save Metadata for Homepage
        meta = {
            "slug": topic_slug,
            "headline": content["headline"],
            "dek": content["dek"],
            "category": content.get("category", niche),
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        with open(os.path.join(page_dir, "meta.json"), 'w') as f:
            json.dump(meta, f)

        with open(self.template_path, 'r') as f:
            template = f.read()
            
        # Unified Placeholder Mapping
        mapping = {
            # ... (mapping values same as before)
            "TITLE": f"{content['headline']} | Crescent Ledger",
            "SITE_NAME": "Crescent Ledger",
            "LOGO_TEXT": "CL",
            "CATEGORY": content.get("category", niche),
            "HEADLINE": content["headline"],
            "DEK": content["dek"],
            "AUTHOR": content.get("author", "Staff Reporter"),
            "HERO_CAPTION": content.get("hero_caption", "Breaking news footage from the scene."),
            "ARTICLE_CONTENT": content["body_html"],
            "TIMELINE_HTML": content.get("timeline_html", ""),
            "RISK_DISCLAIMER": "Past performance does not guarantee future results. Investment involves risk.",
            "POPUP_TITLE": "Wait — Before You Go",
            "POPUP_TEXT": f"Don't miss the 2026 {niche} Migration report.",
            "POPUP_CTA": "Claim Your Free Invite →"
        }

        # Inject Featured Offer
        featured = monetization['featured']
        mapping["TEXT_TICKER_1"] = featured['cta']
        mapping["URL_TICKER_1"] = featured['link']

        # Inject Secondary Offers (Rotate through available)
        secondaries = monetization['secondary']
        for i in range(2, 5):
            offer = secondaries[(i-2) % len(secondaries)]
            mapping[f"TEXT_TICKER_{i}"] = offer['ticker_text']
            mapping[f"URL_TICKER_{i}"] = offer['link']
            
        for i in range(1, 4):
            offer = secondaries[(i-1) % len(secondaries)]
            mapping[f"TEXT_CONTEXT_{i}"] = offer['sidebar_text']
            mapping[f"URL_CONTEXT_{i}"] = offer['link']
            mapping[f"TEXT_REC_{i}"] = offer['sidebar_text']
            mapping[f"URL_REC_{i}"] = offer['link']
            mapping[f"TEXT_SPONSORED_{i}"] = offer['sidebar_text']
            mapping[f"URL_SPONSORED_{i}"] = offer['link']
            mapping[f"TEXT_WATCH_{i}"] = f"Why {offer['name']} is trending right now"
            mapping[f"URL_WATCH_{i}"] = offer['link']

        final_html = template
        for key, value in mapping.items():
            final_html = final_html.replace(f"{{{{{key}}}}}", str(value))
            
        with open(os.path.join(page_dir, "index.html"), "w") as f:
            f.write(final_html)
            
        print(f"[Engine] Done. Page ready at /news/{topic_slug}/ (Niche: {niche})")

if __name__ == "__main__":
    # Internal Dry Run logic
    engine = RIMSEngine("/Users/kd5000/Documents/Nrewsroom")
    print("RIMS Engine initialized. Waiting for prompt data...")
