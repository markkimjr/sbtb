import traceback
from typing import List, Dict, Optional, Any

from sbtb.core.logging import logger
from sbtb.fighter.scraper import BoxingRankScraper, BoxingFightCardScraper
from sbtb.fighter.repository import FighterRepo, FightingOrganizationRepo, RankRepo, WeightClassRepo, FightCardRepo
from sbtb.fighter.schemas import FighterSchema, RawBoxerSchema, RankSchema, FightCardSchema


class BoxerScraperService:
    def __init__(self, scraper: BoxingRankScraper, fighter_repo: FighterRepo,
                 organization_repo: FightingOrganizationRepo,
                 rank_repo: RankRepo, weight_class_repo: WeightClassRepo):
        self.scraper = scraper
        self.fighter_repo = fighter_repo
        self.organization_repo = organization_repo
        self.rank_repo = rank_repo
        self.weight_class_repo = weight_class_repo

    async def scrape_and_update_boxing_ranks(self) -> List[RankSchema]:
        try:
            grouped_rankings: Dict[str, Dict[str, List[RawBoxerSchema]]] = await self.scraper.run_scraper()
            if not grouped_rankings:
                return []

            organizations = await self.organization_repo.get_all()
            weight_classes = await self.weight_class_repo.get_all()

            ranks_to_upsert = []
            for raw_weight_class, raw_organizations in grouped_rankings.items():
                for raw_organization, raw_boxers in raw_organizations.items():
                    for i, raw_boxer in enumerate(raw_boxers):
                        raw_fighter = FighterSchema(
                            name=raw_boxer.name
                        )
                        fighter = await self.fighter_repo.get_or_create(raw_fighter=raw_fighter)
                        if fighter is None:
                            logger.error(f"Failed to save fighter: {raw_fighter.name}")
                            continue

                        organization = next((org for org in organizations if org.name.value == raw_organization), None)
                        if organization is None:
                            logger.error(f"Organization not found: {raw_organization}")
                            continue

                        weight_class = next((wc for wc in weight_classes if wc.name == raw_weight_class), None)
                        if weight_class is None:
                            logger.error(f"Weight class not found: {raw_weight_class}")
                            continue

                        rank = RankSchema(
                            rank=raw_boxer.rank,
                            fighter_id=fighter.id,
                            weight_class_id=weight_class.id,
                            organization_id=organization.id
                        )
                        ranks_to_upsert.append(rank)

            saved_ranks = await self.rank_repo.bulk_upsert(ranks=ranks_to_upsert)
            logger.info(f"Updated {len(saved_ranks)} boxing rankings")

            return ranks_to_upsert
        except Exception as e:
            logger.error(f"ERROR OCCURRED WHILE SCRAPING BOXING RANKINGS {traceback.format_exc()}")
            return []


class BoxingFightCardService:
    def __init__(self, scraper: BoxingFightCardScraper, fighter_repo: FighterRepo,
                 weight_class_repo: WeightClassRepo, fight_card_repo: FightCardRepo):
        self.scraper = scraper
        self.fighter_repo = fighter_repo
        self.weight_class_repo = weight_class_repo
        self.fight_card_repo = fight_card_repo

    async def scrape_and_update_boxing_fight_cards(self) -> List[FightCardSchema]:
        try:
            updated_fight_cards = []
            parsed_fight_cards: Optional[List[Dict[str, Any]]] = await self.scraper.run_scraper()
            if not parsed_fight_cards:
                return []

            for i, parsed_fight_card in enumerate(parsed_fight_cards):
                logger.info(f"Updating fight card {i + 1}/{len(parsed_fight_cards)}")
                title_fighters = parsed_fight_card["title_fighters"]
                undercard_fighters = parsed_fight_card["undercard_fighters"]
                event_name = f"{title_fighters[0]} vs {title_fighters[1]}"
                fight_card_data = FightCardSchema(
                    event_name=event_name,
                    event_date=parsed_fight_card["fight_date"],
                    location=parsed_fight_card["location"],
                )
                # save fight card data to database
                fight_card = await self.fight_card_repo.get_or_create(raw_fight_card=fight_card_data, eager=True)
                matched_fighters = []

                # match fighters to fight_card
                for fighter_name in title_fighters + undercard_fighters:
                    fighter_name = fighter_name.lower()
                    raw_fighter = FighterSchema(name=fighter_name)
                    fighter = await self.fighter_repo.get_or_create(raw_fighter=raw_fighter)
                    if fighter is None:
                        logger.error(f"Failed to save fighter: {raw_fighter.name}")
                        continue

                    matched_fighters.append(fighter)

                fight_card.fighters = matched_fighters
                await self.fight_card_repo.save(fight_card=fight_card)
                updated_fight_cards.append(fight_card_data)

            logger.info(f"Updated {len(parsed_fight_cards)} boxing fight cards")
            return updated_fight_cards

        except Exception as e:
            logger.error(f"ERROR OCCURRED WHILE SCRAPING BOXING FIGHT CARDS {traceback.format_exc()}")
            return []
