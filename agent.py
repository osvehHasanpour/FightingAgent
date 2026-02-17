import json

ACTIONS = [
    "APPROACH",
    "RETREAT",
    "LIGHT_ATTACK_SEQUENCE",
    "HEAVY_ATTACK_OPPORTUNITY",
    "WAIT_FOR_COOLDOWN"
]

def reset_saved_data():
    return {
        "current_action": None,
        "action_timer": 0  
    }

def distance_x(fighter, opponent):
    return abs(fighter["x"] - opponent["x"])

def get_direction(fighter, opponent):
    return "right" if opponent["x"] > fighter["x"] else "left"

def heuristic(fighter, opponent):
    score = 0
    
    health_diff = fighter["health"] - opponent["health"]
    score +=  200 * health_diff
    
    dist = abs(fighter["x"] - opponent["x"])
    
    light_cd = 0
    heavy_cd = 0
    if "attack_cooldown" in fighter:
        light_cd = fighter["attack_cooldown"][0]
        heavy_cd = fighter["attack_cooldown"][1]

    # Kill pressure
    if opponent["health"] <= 20:
        score += 500

    # Strong aggression when attack ready
    if heavy_cd == 0 and dist < 180:
        score += 600

    if light_cd == 0 and dist < 180:
        score += 300

    # Distance fighting logic
    if dist < 170:
        score += 200
    elif dist < 300:
        score += 80
    else:
        score -= 200

    # Punish staying far
    if dist > 400:
        score -= 300

    # Small penalty if opponent attacking
    if opponent["attacking"] and dist < 180:
        score -= 50

    # Edge penalty
    if fighter["x"] < 80 or fighter["x"] > 920:
        score -= 100

    return score

def simulate_action(fighter, opponent, action):
    f = fighter.copy()
    if "attack_cooldown" in fighter:
        f["attack_cooldown"] = list(fighter["attack_cooldown"])
    o = opponent.copy()
    
    is_real_player = "attack_cooldown" in f
    dist = abs(f["x"] - o["x"])
    direction_val = 1 if o["x"] > f["x"] else -1

    if action == "APPROACH":
        f["x"] += direction_val * 60 

    elif action == "RETREAT":
        f["x"] -= direction_val * 40

    elif action == "LIGHT_ATTACK_SEQUENCE":
        can_attack = True
        if is_real_player:
            can_attack = (f["attack_cooldown"][0] == 0)

        if dist < 180 and can_attack:
            o["health"] -= 10
            if is_real_player:
                f["attack_cooldown"][0] = 25
        elif is_real_player:
            f["attack_cooldown"][0] = 25   #if not attacking cooldaown set to 25

    elif action == "HEAVY_ATTACK_OPPORTUNITY":
        can_attack = True
        if is_real_player:
            can_attack = (f["attack_cooldown"][1] == 0)

        if dist < 180 and can_attack:
            o["health"] -= 20
            if is_real_player:
                f["attack_cooldown"][1] = 100
        elif is_real_player:
            f["attack_cooldown"][1] = 100

    elif action == "WAIT_FOR_COOLDOWN":
        if is_real_player:
            f["attack_cooldown"][0] = max(0, f["attack_cooldown"][0] - 5)
            f["attack_cooldown"][1] = max(0, f["attack_cooldown"][1] - 5)

    return f, o

def minimax_decision(fighter, opponent):
    best_score = float("-inf")
    best_action = "WAIT_FOR_COOLDOWN"

    for my_action in ACTIONS:
        f_next, o_next = simulate_action(fighter, opponent, my_action)
        
        opp_move = "LIGHT_ATTACK_SEQUENCE" if distance_x(f_next, o_next) < 180 else "APPROACH"
        
        o_final, f_final = simulate_action(o_next, f_next, opp_move)
        score = heuristic(f_final, o_final)
        
        if score > best_score:
            best_score = score
            best_action = my_action

    return best_action

def execute_action(fighter, opponent, saved_data):
    action = {
        "move": None,
        "attack": None,
        "jump": False,
        "dash": None,
        "debug": None,
        "saved_data": saved_data
    }

    if not saved_data or "current_action" not in saved_data:
        action["saved_data"] = reset_saved_data()
        return action

    current = saved_data["current_action"]
    timer = saved_data["action_timer"]
    saved_data["action_timer"] += 1

    dist = distance_x(fighter, opponent)
    direction = get_direction(fighter, opponent)

    l_cd = fighter["attack_cooldown"][0]
    h_cd = fighter["attack_cooldown"][1]

    if h_cd == 0 and dist < 180:
        action["attack"] = 2
        action["saved_data"] = reset_saved_data()
        return action

    if l_cd == 0 and dist < 180:
        action["attack"] = 1
        action["saved_data"] = reset_saved_data()
        return action

    if current == "APPROACH":

        if dist < 120:
            action["saved_data"] = reset_saved_data()
            return action

        if fighter["dash_cooldown"] == 0 and dist > 250:
            action["dash"] = direction
        else:
            action["move"] = direction

        if timer > 12:
            action["saved_data"] = reset_saved_data()

    elif current == "RETREAT":

        opp_dir = "right" if direction == "left" else "left"
        action["move"] = opp_dir

        if timer > 6:
            action["saved_data"] = reset_saved_data()

    elif current == "LIGHT_ATTACK_SEQUENCE":

        if dist >= 180:
            action["move"] = direction

        if timer > 4:
            action["saved_data"] = reset_saved_data()

    elif current == "HEAVY_ATTACK_OPPORTUNITY":

        if dist >= 180:
            action["move"] = direction

        if timer > 4:
            action["saved_data"] = reset_saved_data()

    elif current == "WAIT_FOR_COOLDOWN":

        action["move"] = direction

        if timer > 1:
            action["saved_data"] = reset_saved_data()

    action["saved_data"] = saved_data
    return action

def make_move(fighter_info, opponent_info, saved_data):
    try:
        if saved_data and saved_data.get("current_action") is not None:
            return execute_action(fighter_info, opponent_info, saved_data)

        chosen_action = minimax_decision(fighter_info, opponent_info)
        
        saved_data = {
            "current_action": chosen_action,
            "action_timer": 0
        }
        return execute_action(fighter_info, opponent_info, saved_data)
        
    except Exception as e:
        return {
            "move": None,
            "attack": None,
            "jump": False,
            "dash": None,
            "debug": str(e),
            "saved_data": reset_saved_data()
        }

if __name__ == "__main__":
    try:
        input_data = input()
        if input_data:
            data = json.loads(input_data)
            result = make_move(
                data["fighter"],
                data["opponent"],
                data["saved_data"]
            )
            print(json.dumps(result))
    except Exception:
        pass
