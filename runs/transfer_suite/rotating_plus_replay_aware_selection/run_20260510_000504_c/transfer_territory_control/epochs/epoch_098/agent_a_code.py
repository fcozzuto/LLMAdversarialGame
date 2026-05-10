def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    obstacles = set(map(tuple, observation.get("obstacles") or []))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells") or []))
    self_terr = set(map(tuple, observation.get("self_territory") or []))
    opp_terr = set(map(tuple, observation.get("opponent_territory") or []))
    scores = observation.get("scores") or {}
    self_name = observation.get("self_name", "agent_a")
    opp_name = observation.get("opponent_name", "agent_b")
    my_score = float(scores.get(self_name, 0.0) or 0.0)
    op_score = float(scores.get(opp_name, 0.0) or 0.0)

    cx, cy = (w - 1) // 2, (h - 1) // 2
    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def legal(nx, ny): return inb(nx, ny) and (nx, ny) not in obstacles
    def md(a, b, c, d): return abs(a - c) + abs(b - d)

    # Build a deterministic local target: nearest unclaimed toward center, else toward center.
    if unclaimed:
        best = None
        for tx, ty in unclaimed:
            key = (md(tx, ty, cx, cy), md(sx, sy, tx, ty), md(tx, ty, ox, oy))
            if best is None or key < best[0] or (key == best[0] and (tx, ty) < best[1]):
                best = (key, (tx, ty))
        tx, ty = best[1]
    else:
        tx, ty = cx, cy

    # If losing, prioritize steals (enter opponent territory). If winning, expand safely.
    aggressive = my_score <= op_score
    best_move = (0, 0)
    best_key = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue

        on_opp = (nx, ny) in opp_terr
        on_self = (nx, ny) in self_terr
        on_un = (nx, ny) in unclaimed

        # Estimate gain and strategic pressure.
        gain = 0
        if on_opp:
            gain = 12 if aggressive else 9
        elif on_un:
            gain = 7 if aggressive else 8
        elif on_self:
            gain = 2
        else:
            gain = 0

        # Prefer moves that reduce distance to target, and when losing, increase distance from opponent target.
        toward = md(nx, ny, tx, ty)
        away_from_opp = md(nx, ny, ox, oy)

        # Tie-breakers: deterministic ordering preference closer to center, then smaller dx/dy lexicographic.
        center_dist = md(nx, ny, cx, cy)
        key = (-gain, toward, -away_from_opp if aggressive else away_from_opp, center_dist, dx, dy)

        if best_key is None or key < best_key:
            best_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]