def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    role = (str(observation.get("self_role", "")) + " " + str(observation.get("opponent_role", ""))).lower()
    self_is_pursuer = "pursuer" in role and "evader" not in role
    obs = set()
    for p in (observation.get("obstacles") or []):
        if p is not None and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    obstacles_list = list(obs)

    def dist(x, y):
        return abs(x - ox) + abs(y - oy)

    def obstacle_pressure(x, y):
        # Prefer moving away from blocked cells (creates smoother paths around obstacles)
        near = 0
        for (px, py) in obstacles_list:
            d = abs(px - x) + abs(py - y)
            if d == 0:
                return 10**9
            if d == 1:
                near += 3
            elif d == 2:
                near += 1
        return near

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d = dist(nx, ny)
        op_pressure = obstacle_pressure(nx, ny)
        # If pursuer: minimize distance; if evader: maximize distance.
        score = (-d if self_is_pursuer else d) - op_pressure * (1 if self_is_pursuer else 2)
        if best is None or score > best_score or (score == best_score and (dx, dy) < tuple(best)):
            best_score = score
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]