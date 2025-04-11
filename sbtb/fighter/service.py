import traceback
from typing import List, Dict, Optional, Any

from sbtb.core.logging import logger
from sbtb.fighter.scraper import BoxingRankScraper, BoxingFightCardScraper
from sbtb.fighter.repository import FighterRepo, FightOrganizationRepo, RankRepo, WeightClassRepo, FightCardRepo
from sbtb.fighter.schemas import RawBoxerSchema, RankRead
from sbtb.fighter.domain import FighterDomain, RankDomain, FightCardDomain, WeightClassDomain, \
    FightOrganizationDomain


class BoxerScraperService:
    def __init__(self, scraper: BoxingRankScraper, fighter_repo: FighterRepo,
                 organization_repo: FightOrganizationRepo,
                 rank_repo: RankRepo, weight_class_repo: WeightClassRepo):
        self.scraper = scraper
        self.fighter_repo = fighter_repo
        self.organization_repo = organization_repo
        self.weight_class_repo = weight_class_repo
        self.rank_repo = rank_repo

    async def scrape_and_update_boxing_ranks(self) -> List[RankRead]:
        try:
            grouped_rankings: Dict[str, Dict[str, List[RawBoxerSchema]]] = await self.scraper.run_scraper()
            if not grouped_rankings:
                return []

            organizations: List[FightOrganizationDomain] = await self.organization_repo.get_all()
            weight_classes: List[WeightClassDomain] = await self.weight_class_repo.get_all()

            rank_reads = []
            ranks_to_upsert = []
            for raw_weight_class, raw_organizations in grouped_rankings.items():
                for raw_organization, raw_boxers in raw_organizations.items():
                    for i, raw_boxer in enumerate(raw_boxers):
                        raw_fighter = FighterDomain(
                            name=raw_boxer.name
                        )
                        fighter = await self.fighter_repo.get_or_create(raw_fighter=raw_fighter)
                        if fighter is None:
                            logger.error(f"Failed to save fighter: {raw_fighter.name}")
                            continue

                        organization = next((org for org in organizations if org.name == raw_organization), None)
                        if organization is None:
                            logger.error(f"Organization not found: {raw_organization}")
                            continue

                        weight_class = next((wc for wc in weight_classes if wc.name == raw_weight_class), None)
                        if weight_class is None:
                            logger.error(f"Weight class not found: {raw_weight_class}")
                            continue

                        rank = RankDomain(
                            rank=raw_boxer.rank,
                            fighter_id=fighter.id,
                            weight_class_id=weight_class.id,
                            organization_id=organization.id
                        )
                        ranks_to_upsert.append(rank)

                        rank_read = RankRead(
                            rank=rank.rank,
                            fighter_name=fighter.name,
                            organization_name=organization.name,
                            weight_class_name=weight_class.name,
                        )
                        rank_reads.append(rank_read)

            saved_ranks: List[RankDomain] = await self.rank_repo.bulk_upsert(ranks=ranks_to_upsert)
            logger.info(f"Updated {len(saved_ranks)} boxing rankings")

            return rank_reads
        except Exception as e:
            logger.error(f"ERROR OCCURRED WHILE SCRAPING BOXING RANKINGS {traceback.format_exc()}")
            return []


class BoxingFightCardService:
    def __init__(self, scraper: BoxingFightCardScraper, fighter_repo: FighterRepo,
                 fight_card_repo: FightCardRepo):
        self.scraper = scraper
        self.fighter_repo = fighter_repo
        self.fight_card_repo = fight_card_repo

    async def scrape_and_update_boxing_fight_cards(self) -> List[FightCardDomain]:
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
                fight_card_data = FightCardDomain(
                    event_name=event_name,
                    event_date=parsed_fight_card["fight_date"],
                    location=parsed_fight_card["location"],
                )
                # save fight card data to database
                saved_fight_card = await self.fight_card_repo.get_or_create(fight_card_domain=fight_card_data)
                matched_fighter = []

                # match fighters to fight_card
                for fighter_name in title_fighters + undercard_fighters:
                    fighter_name = fighter_name.lower()
                    raw_fighter = FighterDomain(name=fighter_name)
                    fighter = await self.fighter_repo.get_or_create(raw_fighter=raw_fighter)
                    if fighter is None:
                        logger.error(f"Failed to save fighter: {raw_fighter.name}")
                        continue

                    matched_fighter.append(fighter)

                saved_fight_card.fighters = matched_fighter
                await self.fight_card_repo.save(fight_card_domain=saved_fight_card)
                updated_fight_cards.append(saved_fight_card)

            logger.info(f"Updated {len(parsed_fight_cards)} boxing fight cards")
            return updated_fight_cards

        except Exception as e:
            logger.error(f"ERROR OCCURRED WHILE SCRAPING BOXING FIGHT CARDS {traceback.format_exc()}")
            return []
