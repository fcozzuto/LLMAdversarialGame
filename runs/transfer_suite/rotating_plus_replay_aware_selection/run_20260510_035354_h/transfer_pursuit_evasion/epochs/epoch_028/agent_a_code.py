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

    best_move = [0, 0]
    best_score = None

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obs:
            continue

        d = abs(nx - ox) + abs(ny - oy)
        score = d if evade else -d

        # When tied, prefer moving toward/away from nearest corner to reduce opponent alignment.
        corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
        corner_dist = min(abs(nx - cx) + abs(ny - cy) for cx, cy in corners)
        if evade:
            tiebreak = (score, corner_dist, -abs(dx) - abs(dy))
        else:
            tiebreak = (score, -corner_dist, -abs(dx) - abs(dy))

        if best_score is None or tiebreak > best_score:
            best_score = tiebreak
            best_move = [dx, dy]

    # If all moves blocked, stay put (engine will reject invalid moves by keeping position).
    if best_score is None:
        return [0, 0]
    return best_move