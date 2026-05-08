def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = observation.get("obstacles", [])
    obs = {(x, y) for x, y in obstacles}

    role = (observation.get("self_role") or "").lower()
    opp_role = (observation.get("opponent_role") or "").lower()

    pursuer = ("pursuer" in role) or ("evader" in opp_role)
    if "pursuer" not in role and "evader" not in opp_role and "evader" in role and "pursuer" not in opp_role:
        pursuer = False

    deltas = [(0, 0), (1, 0), (0, 1), (-1, 0), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def dist2(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        return dx * dx + dy * dy

    best_val = None
    best_move = (0, 0)

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            nx, ny = sx, sy
            dx, dy = 0, 0
        d = dist2(nx, ny, ox, oy)
        move_cost = abs(dx) + abs(dy)
        # Pursuer: maximize negative distance (i.e., minimize distance). Evader: opposite.
        val = -d if pursuer else d
        val -= 0.01 * move_cost
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]