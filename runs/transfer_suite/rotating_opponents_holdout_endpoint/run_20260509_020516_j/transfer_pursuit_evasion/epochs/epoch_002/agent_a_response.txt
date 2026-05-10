def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = int(observation["self_position"][0]), int(observation["self_position"][1])
    ox, oy = int(observation["opponent_position"][0]), int(observation["opponent_position"][1])

    obstacles = observation.get("obstacles", [])
    obs_set = set((int(p[0]), int(p[1])) for p in obstacles)

    self_role = observation.get("self_role", "") or ""
    opp_role = observation.get("opponent_role", "") or ""
    self_lower, opp_lower = self_role.lower(), opp_role.lower()
    pursuer = (("purs" in self_lower) or ("evad" in opp_lower and "evad" not in self_lower))

    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def free_neighbors(x, y):
        c = 0
        for dx, dy in deltas:
            nx, ny = x + dx, y + dy
            if in_bounds(nx, ny) and (nx, ny) not in obs_set:
                c += 1
        return c

    best_move = [0, 0]
    best_score = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obs_set:
            continue

        d2 = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
        neigh = free_neighbors(nx, ny)

        # Prefer safety against wall-run trapping when evading; prefer closing when pursuing.
        # Tie-break deterministically by order of deltas.
        if pursuer:
            score = -d2 + 0.05 * neigh
        else:
            score = d2 + 0.4 * neigh

        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move