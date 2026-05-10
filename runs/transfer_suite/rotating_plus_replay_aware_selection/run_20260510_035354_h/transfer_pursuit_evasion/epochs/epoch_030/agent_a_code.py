def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        try:
            obs.add((int(p[0]), int(p[1])))
        except Exception:
            pass

    role = (observation.get("self_role") or "").lower()
    opp_role = (observation.get("opponent_role") or "").lower()
    evade = ("evad" in role) or ("purs" not in role and "evad" in opp_role)

    corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    best_move = [0, 0]

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obs:
            continue

        d = abs(nx - ox) + abs(ny - oy)
        # Higher is better for evader; lower is better for pursuer
        base = d if evade else -d

        corner_dist = min(abs(nx - cx) + abs(ny - cy) for cx, cy in corners)

        # Pursuer: additionally avoid moves that put us into the "same direction" alignment with evader.
        # Evader: additionally avoid moves that reduce our safety margin toward the nearest corner.
        align = (nx - sx) * (nx - ox) + (ny - sy) * (ny - oy)  # deterministic scalar

        # Prefer staying off obstacles influence by preferring moves that keep more adjacent free cells.
        free = 0
        for adx in (-1, 0, 1):
            for ady in (-1, 0, 1):
                if adx == 0 and ady == 0:
                    continue
                tx, ty = nx + adx, ny + ady
                if 0 <= tx < w and 0 <= ty < h and (tx, ty) not in obs:
                    free += 1

        # Construct lexicographic key
        # Tie-breaker biases toward corner runs: evader toward far corner, pursuer toward near corner.
        if evade:
            key = (base, corner_dist, free, -abs(dx) - abs(dy), -align)
        else:
            key = (base, -corner_dist, free, -abs(dx) - abs(dy), align)

        if best is None or key > best:
            best = key
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]