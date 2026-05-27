def choose_move(observation):
    pos = observation.get("position", [0, 0])

    # Resource collection
    resource_pos = observation.get("resource", None)
    if resource_pos:
        dx = 1 if resource_pos[0] > pos[0] else -1 if resource_pos[0] < pos[0] else 0
        dy = 1 if resource_pos[1] > pos[1] else -1 if resource_pos[1] < pos[1] else 0
        return [dx, dy]

    # Pursuit or evasion
    enemies = observation.get("enemies", [])
    if enemies:
        closest_enemy = min(enemies, key=lambda e: (e[0]-pos[0])**2 + (e[1]-pos[1])**2)
        dx = -1 if closest_enemy[0] > pos[0] else 1 if closest_enemy[0] < pos[0] else 0
        dy = -1 if closest_enemy[1] > pos[1] else 1 if closest_enemy[1] < pos[1] else 0
        return [dx, dy]

    # Territory control
    goal = observation.get("territory_goal", None)
    if goal:
        dx = 1 if goal[0] > pos[0] else -1 if goal[0] < pos[0] else 0
        dy = 1 if goal[1] > pos[1] else -1 if goal[1] < pos[1] else 0
        return [dx, dy]

    # Default fallback
    return [0, 0]
