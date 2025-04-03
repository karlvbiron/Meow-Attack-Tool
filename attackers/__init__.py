# Import the attackers
from attackers.mongodb import MongoDBAttacker
from attackers.elasticsearch import ElasticsearchAttacker
from core.attack_factory import AttackFactory

# Register all attackers with the factory
AttackFactory.register_attacker(MongoDBAttacker)
AttackFactory.register_attacker(ElasticsearchAttacker)

__all__ = ['MongoDBAttacker', 'ElasticsearchAttacker']