def choose_move(observation):
    sx, sy = observation["self_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = set(observation.get("obstacles") or [])
    opp = observation.get("opponent_position")
    unclaimed = observation.get("unclaimed_cells") or []
    moves = [(dx, dy) for dy in (-1, 0, 1) for dx in (-1, 0, 1)]
    self_scores = observation.get("scores") or {}
    sscore = self_scores.get("self", self_scores.get("me", self_scores.get("player", 0)))
    oscore = self_scores.get("opponent", self_scores.get("opp", self_scores.get("enemy", 0)))
    if sscore is None:
        sscore = 0
    if oscore is None:
        oscore = 0
    behind = sscore < oscore

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    if behind and unclaimed:
        tx, ty = min(unclaimed, key=lambda p: (man((sx, sy), p), p[1], p[0]))
    elif opp is not None:
        tx, ty = opp
    else:
        tx, ty = (w - 1) / 2, (h - 1) / 2

    best = None
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        target_dist = man((nx, ny), (tx, ty))
        step_pen = 0 if (dx == 0 and dy == 0) else 1
        opp_dist = man((nx, ny), opp) if opp is not None else 0
        score = (target_dist * 10 + step_pen) + (0 if behind else -opp_dist)
        key = (score, dy, dx)
        if best_score is None or key < best_score:
            best_score = key
            best = (dx, dy)
    if best is None:
        return [0, 0]
    return [best[0], best[1]]