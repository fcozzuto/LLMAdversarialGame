def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    env = observation.get("environment_name", "resource_collection")
    obs_cells = set((p[0], p[1]) for p in obstacles if p and len(p) >= 2)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    legal = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obs_cells:
                legal.append((dx, dy))
    if not legal:
        return [0, 0]

    res = [(r[0], r[1]) for r in resources if r and len(r) >= 2 and (r[0], r[1]) not in obs_cells]
    if not res:
        return [0, 0]

    def md(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    # Choose deterministically: evaluate moves for (1) immediate collection, (2) min distance,
    # (3) relative advantage vs opponent on contested resources.
    best_move = None
    best_score = -10**18

    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        on_res = 1 if (nx, ny) in set(res) else 0

        # Compute nearest self and opponent distances, plus "contested pressure"
        sd = 10**9
        od = 10**9
        contested_gain = 0
        near_count = 0

        for rx, ry in res:
            d_s = md(nx, ny, rx, ry)
            d_o = md(ox, oy, rx, ry)
            if d_s < sd:
                sd = d_s
            if d_o < od:
                od = d_o
            if d_s <= 2:
                near_count += 1
            # If we can be closer than opponent by a meaningful margin, prefer it.
            # Also penalize moving to areas where opponent is much closer to many resources.
            diff = d_o - d_s
            if diff >= 2:
                contested_gain += diff
            elif diff <= -2:
                contested_gain += diff * 0.5  # smaller penalty to avoid overfitting

        # Prefer moves that lead to a closer "race" position; also add slight bias to progress
        # in the direction away from opponent when ties occur.
        rel = (od - sd)  # positive means we're closer to some resource than opponent is
        dist_adv = rel * 10.0

        # If opponent already adjacent to some resource, we prioritize denial: move to any resource
        # where we can match or beat their distance.
        denial = 0
        for rx, ry in res:
            d_o = md(ox, oy, rx, ry)
            d_n = md(nx, ny, rx, ry)
            if d_o <= 1 and d_n <= 1:
                denial += 1
        score = 0.0
        score += on_res * 10000.0
        score += dist_adv
        score += (2.5 - sd) * 50.0  # closer is better
        score += near_count * 25.0
        score += contested_gain * 5.0
        score += denial * 200.0
        if env != "resource_collection":
            score *= 1.0

        # Deterministic tie-break: lexicographically by (dx,dy) after score.
        if score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]