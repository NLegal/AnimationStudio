from __future__ import annotations
from typing import Dict, List, Optional
from src.story_engine.models import EpisodeBlueprint, SeasonPlan, SeriesPlan
from src.story_engine.generator import EpisodeGenerator

class SeriesPlanner:
    def __init__(self):
        self._series_plan = SeriesPlan(
            title="Little Learning Town",
            seasons=[
                SeasonPlan(season_number=1, title="Meet the Characters",
                    description="Introduce the main characters and their world",
                    episodes=[], curriculum_focus=["friendship", "emotions", "language"]),
                SeasonPlan(season_number=2, title="Learning Colors",
                    description="Explore the vibrant world of colors",
                    episodes=[], curriculum_focus=["colors", "shapes", "art"]),
                SeasonPlan(season_number=3, title="Learning Numbers",
                    description="Discover numbers and counting",
                    episodes=[], curriculum_focus=["numbers", "counting", "problem-solving"]),
                SeasonPlan(season_number=4, title="Animal Adventures",
                    description="Explore the animal kingdom",
                    episodes=[], curriculum_focus=["animals", "ocean", "farm", "science"]),
                SeasonPlan(season_number=5, title="School Time",
                    description="Learn about school, community, and healthy habits",
                    episodes=[], curriculum_focus=["community-helpers", "healthy-habits", "transportation", "geography"]),
                SeasonPlan(season_number=6, title="Science Fun",
                    description="Explore science, space, and the natural world",
                    episodes=[], curriculum_focus=["science", "space", "seasons", "weather"]),
            ],
        )
        self._holiday_schedule: Dict[str, str] = {
            "new-year": "2026-01-01",
            "valentines-day": "2026-02-14",
            "easter": "2026-04-05",
            "spring": "2026-03-20",
            "summer": "2026-06-21",
            "back-to-school": "2026-09-01",
            "halloween": "2026-10-31",
            "thanksgiving": "2026-11-26",
            "christmas": "2026-12-25",
            "winter": "2026-12-21",
        }

    def plan_season(self, season_number: int, episode_count: int = 20,
                    generator: Optional[EpisodeGenerator] = None) -> SeasonPlan:
        gen = generator or EpisodeGenerator()
        season_plan = self.get_season_plan(season_number)
        for ep_num in range(1, episode_count + 1):
            ep = gen.generate_episode(season=season_number, episode_number=ep_num,
                                      target_age="2-5", difficulty=((ep_num - 1) % 3) + 1)
            season_plan.episodes.append(ep)
        return season_plan

    def plan_holiday_episodes(self, year: int,
                              generator: Optional[EpisodeGenerator] = None) -> List[EpisodeBlueprint]:
        gen = generator or EpisodeGenerator()
        episodes: List[EpisodeBlueprint] = []
        ep_num = 1
        for holiday_name in self._holiday_schedule:
            ep = gen.generate_episode(season=1, episode_number=ep_num,
                                      holiday=holiday_name, target_age="2-5", difficulty=1)
            episodes.append(ep)
            ep_num += 1
        return episodes

    def get_season_plan(self, season_number: int) -> SeasonPlan:
        for season in self._series_plan.seasons:
            if season.season_number == season_number:
                return season
        new_season = SeasonPlan(season_number=season_number, title=f"Season {season_number}",
                                 description="", episodes=[], curriculum_focus=[])
        self._series_plan.seasons.append(new_season)
        return new_season

    def get_series_plan(self) -> SeriesPlan:
        return self._series_plan

    def get_holiday_schedule(self, year: int) -> Dict:
        return dict(self._holiday_schedule)
