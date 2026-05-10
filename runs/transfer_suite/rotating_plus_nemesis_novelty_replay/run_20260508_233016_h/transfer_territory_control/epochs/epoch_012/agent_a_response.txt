def choose_move(observation):
    sx, sy = observation["self_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    self_terr = set(tuple(p) for p in (observation.get("self_territory") or []))
    opp_terr = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))
    cx, cy = (w - 1) // 2, (h - 1) // 2

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    def md(a, b):
        d = a - b
        return d if d >= 0 else -d

    def cell_dist(x, y, tx, ty):
        return md(x, tx) + md(y, ty)

    # Target choice: prefer stealing near opponent frontier; else expand toward center.
    opp_adj = []
    if opp_terr:
        for (ox, oy) in opp_terr:
            for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, 1), (-1, 1), (1, -1)):
                nx, ny = ox + dx, oy + dy
                if (0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles and (nx, ny) not in opp_terr):
                    opp_adj.append((nx, ny))
        # keep deterministic, limited
        opp_adj = sorted(set(opp_adj))[:12]

    candidates = []
    if opp_adj:
        # choose nearest frontier cell to our current position; break ties deterministically
        best = min(opp_adj, key=lambda t: (cell_dist(sx, sy, t[0], t[1]), t[1], t[0]))
        tx, ty = best
        candidates = [("front", tx, ty)]
    else:
        # pick unclaimed closest to center (or to us if none)
        if unclaimed:
            best_u = min(unclaimed, key=lambda t: (cell_dist(t[0], t[1], cx, cy), cell_dist(sx, sy, t[0], t[1]), t[1], t[0]))
            candidates = [("unclaimed_center", best_u[0], best_u[1])]
        else:
            candidates = [("center", cx, cy)]

    tx, ty = candidates[0][1], candidates[0][2]

    best_move = (0, 0)
    best_score = -10**18
    # Deterministic tie-break: higher score, then lexicographically smaller (dx,dy)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        # Reward capturing opponent-owned cell; bonus for moving closer to target.
        score = -cell_dist(nx, ny, tx, ty) * 2
        if (nx, ny) in opp_terr:
            score += 120
        if (nx, ny) in unclaimed:
            score += 25
        if (nx, ny) in self_terr:
            score += 8
        # Discourage stepping away from center if we don't have frontier target
        if not opp_adj:
            score += -cell_dist(nx, ny, cx, cy)
        # Prefer avoiding "traps" by mildly favoring staying off obstacles is already enforced; add mild penalty for not advancing.
        if (nx, ny) == (sx, sy):
            score -= 3

        if score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]