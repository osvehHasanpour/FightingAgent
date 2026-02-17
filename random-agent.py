import json
import random
import numpy as np
from collections import defaultdict, deque
from math import log2, sqrt
import time

class AdvancedFighterAI:
    def __init__(self):
        # Markov model for opponent action prediction
        self.opponent_model = {
            'attack_transitions': defaultdict(lambda: defaultdict(int)),
            'move_transitions': defaultdict(lambda: defaultdict(int)),
            'last_actions': deque(maxlen=3)
        }
        
        # Combat parameters
        self.ideal_attack_range = (120, 180)  # Preferred attack distance range
        self.safe_distance = 200  # Distance to maintain when not attacking
        self.aggression_threshold = 0.7  # Threshold to switch to aggressive mode
        self.defensive_threshold = 0.3  # Threshold to switch to defensive mode
        
        # State tracking
        self.current_strategy = "balanced"
        self.last_health_diff = 0
        self.attack_pattern = []
        self.dash_history = []
        self.frame_counter = 0
        
        # Performance metrics
        self.successful_attacks = 0
        self.failed_attacks = 0
        self.dodged_attacks = 0
        
    def initialize_saved_data(self):
        return {
            "opponent_model": {
                "attack_transitions": defaultdict(lambda: defaultdict(int)),
                "move_transitions": defaultdict(lambda: defaultdict(int)),
                "last_actions": []
            },
            "combat_stats": {
                "successful_attacks": 0,
                "failed_attacks": 0,
                "dodged_attacks": 0
            },
            "strategy_history": [],
            "health_differential": 0,
            "frame_data": {},
            "last_update": time.time()
        }

    def update_opponent_model(self, saved_data, opponent_action, distance):
        """Update Markov model with opponent's latest action"""
        if len(saved_data["opponent_model"]["last_actions"]) > 0:
            last_action = saved_data["opponent_model"]["last_actions"][-1]
            
            # Update attack transition probabilities
            if 'attack' in opponent_action:
                saved_data["opponent_model"]["attack_transitions"][last_action][opponent_action['attack']] += 1
            
            # Update movement transition probabilities
            if 'move' in opponent_action:
                saved_data["opponent_model"]["move_transitions"][last_action][opponent_action['move']] += 1
        
        # Store current action
        action_key = self._create_action_key(opponent_action, distance)
        saved_data["opponent_model"]["last_actions"].append(action_key)
        if len(saved_data["opponent_model"]["last_actions"]) > 5:
            saved_data["opponent_model"]["last_actions"].pop(0)
            
        return saved_data

    def _create_action_key(self, action, distance):
        """Create a standardized key for action tracking"""
        parts = []
        if action.get('attack'):
            parts.append(f"atk{action['attack']}")
        if action.get('move'):
            parts.append(f"mov{action['move']}")
        if action.get('jump'):
            parts.append("jmp")
        if action.get('dash'):
            parts.append(f"dsh{action['dash']}")
        
        dist_category = "close" if distance < 150 else "mid" if distance < 250 else "far"
        parts.append(dist_category)
        
        return "_".join(parts)

    def predict_opponent_action(self, saved_data, distance):
        """Predict opponent's next action using Markov model"""
        if not saved_data["opponent_model"]["last_actions"]:
            return None
            
        last_action = saved_data["opponent_model"]["last_actions"][-1]
        
        # Predict attack
        attack_transitions = saved_data["opponent_model"]["attack_transitions"][last_action]
        if attack_transitions:
            total = sum(attack_transitions.values())
            attack_probs = {k: v/total for k, v in attack_transitions.items()}
            predicted_attack = max(attack_probs.items(), key=lambda x: x[1])[0]
        else:
            predicted_attack = None
            
        # Predict movement
        move_transitions = saved_data["opponent_model"]["move_transitions"][last_action]
        if move_transitions:
            total = sum(move_transitions.values())
            move_probs = {k: v/total for k, v in move_transitions.items()}
            predicted_move = max(move_probs.items(), key=lambda x: x[1])[0]
        else:
            predicted_move = None
            
        return {
            'attack': predicted_attack,
            'move': predicted_move
        }

    def calculate_optimal_position(self, fighter_x, opponent_x, opponent_attacking):
        """Determine the best position relative to opponent"""
        current_distance = abs(fighter_x - opponent_x)
        
        if opponent_attacking:
            # If opponent is attacking, maintain safe distance
            if fighter_x < opponent_x:
                return opponent_x - self.safe_distance
            else:
                return opponent_x + self.safe_distance
        else:
            # Otherwise position for optimal attack range
            if fighter_x < opponent_x:
                return opponent_x - random.randint(*self.ideal_attack_range)
            else:
                return opponent_x + random.randint(*self.ideal_attack_range)

    def determine_strategy(self, health_diff, opponent_aggression):
        """Select strategy based on game state"""
        if health_diff > 30:
            # Significant health lead - play defensively
            return "defensive"
        elif health_diff < -20:
            # Significant health deficit - play aggressively
            return "aggressive"
        elif opponent_aggression > self.aggression_threshold:
            # Opponent is very aggressive - counter with defense
            return "counter"
        elif opponent_aggression < self.defensive_threshold:
            # Opponent is passive - press the attack
            return "press"
        else:
            # Balanced approach
            return "balanced"

    def calculate_opponent_aggression(self, saved_data):
        """Measure how aggressive the opponent is being"""
        if not saved_data["opponent_model"]["last_actions"]:
            return 0.5
            
        attack_actions = 0
        total_actions = 0
        
        for action in saved_data["opponent_model"]["last_actions"]:
            if "atk" in action:
                attack_actions += 1
            total_actions += 1
            
        return attack_actions / total_actions if total_actions > 0 else 0.5

    def make_move(self, fighter_info, opponent_info, saved_data):
        # Initialize saved data if empty
        if not saved_data:
            saved_data = self.initialize_saved_data()
            
        # Calculate game variables
        distance = abs(fighter_info['x'] - opponent_info['x'])
        light_cd, heavy_cd = fighter_info['attack_cooldown']
        dash_cd = fighter_info['dash_cooldown']
        health_diff = fighter_info['health'] - opponent_info['health']
        opponent_aggression = self.calculate_opponent_aggression(saved_data)
        
        # Update opponent model
        predicted_action = self.predict_opponent_action(saved_data, distance)
        
        # Determine optimal strategy
        current_strategy = self.determine_strategy(health_diff, opponent_aggression)
        
        # Base actions
        actions = {
            'move': None,
            'attack': None,
            'jump': False,
            'dash': None,
            'debug':  {
            },
            'saved_data': saved_data
        }
        
        # Handle predicted opponent attacks
        if predicted_action and predicted_action.get('attack'):
            if distance < 180:  # Only dodge if opponent is in attack range
                # 80% chance to dodge predicted attack
                if random.random() < 0.8:
                    if dash_cd == 0:
                        actions['dash'] = 'left' if fighter_info['x'] > opponent_info['x'] else 'right'
                        actions['debug']['action'] = 'dodging'
                        saved_data["combat_stats"]["dodged_attacks"] += 1
                        return actions
                    else:
                        actions['jump'] = True
                        actions['debug']['action'] = 'jumping'
                        saved_data["combat_stats"]["dodged_attacks"] += 1
                        return actions
        
        # Strategic positioning
        optimal_x = self.calculate_optimal_position(
            fighter_info['x'], 
            opponent_info['x'], 
            opponent_info['attacking']
        )
        
        if fighter_info['x'] < optimal_x - 10:
            actions['move'] = 'right'
        elif fighter_info['x'] > optimal_x + 10:
            actions['move'] = 'left'
        
        # Attack logic based on strategy
        if current_strategy == "aggressive" or current_strategy == "press":
            # Aggressive attack pattern
            if distance < 180:
                if heavy_cd == 0 and random.random() < 0.7:
                    actions['attack'] = 2
                elif light_cd == 0:
                    actions['attack'] = 1
        elif current_strategy == "defensive" or current_strategy == "counter":
            # Conservative attack pattern
            if distance < 150 and random.random() < 0.4:
                if light_cd == 0:
                    actions['attack'] = 1
        else:  # balanced
            # Mixed attack pattern
            if distance < 180:
                if heavy_cd == 0 and random.random() < 0.4:
                    actions['attack'] = 2
                elif light_cd == 0 and random.random() < 0.6:
                    actions['attack'] = 1
        
        # Special moves based on cooldowns
        if dash_cd == 0 and distance > 200 and current_strategy in ["aggressive", "press"]:
            if random.random() < 0.3:
                actions['dash'] = 'right' if fighter_info['x'] < opponent_info['x'] else 'left'
        
        # Periodic jump to avoid predictability
        if self.frame_counter % 40 == 0 and distance < 220:
            actions['jump'] = True
        
        self.frame_counter += 1
        return actions

# Main function to interface with game
def make_move(fighter_info, opponent_info, saved_data):
    ai = AdvancedFighterAI()
    result = ai.make_move(fighter_info, opponent_info, saved_data)
    
    # Convert debug info to string for output
    if isinstance(result['debug'], dict):
        debug_str = "; ".join(f"{k}: {v}" for k, v in result['debug'].items())
        result['debug'] = debug_str
    
    return result

# Input handler
if __name__ == "__main__":
    input_data = input()
    json_data = json.loads(input_data)
    fighter_info = json_data['fighter']
    opponent_info = json_data['opponent']
    saved_data = json_data.get('saved_data', {})
    result = make_move(fighter_info, opponent_info, saved_data)
    print(json.dumps(result))