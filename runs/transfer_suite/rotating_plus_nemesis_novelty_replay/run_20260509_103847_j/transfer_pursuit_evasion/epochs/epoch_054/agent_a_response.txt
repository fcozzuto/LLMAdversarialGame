def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obs_set = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs_set.add((x, y))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs_set

    sr = (observation.get("self_role") or "").lower()
    pr = (observation.get("opponent_role") or "").lower()
    self_purs = any(k in sr for k in ("purs", "catch", "hunt", "chaser", "pursuer"))
    opp_purs = any(k in pr for k in ("purs", "catch", "hunt", "chaser", "pursuer"))
    pursuer = self_purs and not (opp_purs and not self_purs)
    if (not self_purs) and opp_purs:
        pursuer = False

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    best_val = None

    def score(nx, ny):
        dx = nx - ox
        dy = ny - oy
        d2 = dx * dx + dy * dy
        # Encourage/avoid obstacles implicitly (disallow via inside); add boundary safety.
        cx = 0.0 if w <= 1 else (nx / (w - 1))
        cy = 0.0 if h <= 1 else (ny / (h - 1))
        edge = min(cx, 1 - cx, cy, 1 - cy)  # higher is more central
        # small tie-breaker: prefer deterministic motion not stuck
        moved = 1 if (nx != sx or ny != sy) else 0
        if pursuer:
            # minimize distance; prefer central if tied
            return (-d2, edge, moved)
        else:
            # maximize distance; prefer central if tied
            return (d2, edge, moved)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        val = score(nx, ny)
        if best is None or val > best_val:
            best, best_val = (dx, dy), val

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]