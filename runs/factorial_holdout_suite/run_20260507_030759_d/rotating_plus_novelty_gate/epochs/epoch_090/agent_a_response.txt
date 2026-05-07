def choose_move(observation):
    w = observation.get("grid_width", 8) or 8
    h = observation.get("grid_height", 8) or 8
    sx, sy = observation.get("self_position", (0, 0)) or (0, 0)
    ox, oy = observation.get("opponent_position", (0, 0)) or (0, 0)

    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((p[0], p[1]))

    res = []
    for p in resources:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            res.append((p[0], p[1]))

    if not res:
        return [0, 0]

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    legal = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs:
                legal.append((dx, dy))
    if not legal:
        return [0, 0]

    # Pick resource that maximizes our advantage (ours closer than opponent).
    best_r = None
    best_key = None
    for r in res:
        d_me = man((sx, sy), r)
        d_opp = man((ox, oy), r)
        # prefer collectible soon and where opponent is least likely to arrive first
        key = (d_opp - d_me, -d_me, -abs(r[0] - (w - 1 if sy < h // 2 else 0)) - abs(r[1] - (h - 1 if sx < w // 2 else 0)))
        if best_key is None or key > best_key:
            best_key = key
            best_r = r

    tx, ty = best_r
    # One-step lookahead: move that improves advantage to target; tie-break by closer to target.
    best_move = None
    best_score = None
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        d_me2 = man((nx, ny), (tx, ty))
        d_opp2 = man((ox, oy), (tx, ty))
        score = (d_opp2 - d_me2, -d_me2, -man((nx, ny), best_r))
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]