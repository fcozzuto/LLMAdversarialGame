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
    if not self_purs and opp_purs:
        pursuer = False

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_score = None

    def dist2(x, y):
        dx = x - ox
        dy = y - oy
        return dx * dx + dy * dy

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        d = dist2(nx, ny)

        if pursuer:
            score = -d
            if d == 0:
                score = 1e9
            # Small bias to avoid being blocked: penalize moves where next step options are low.
            nxt_opts = 0
            for ddx, ddy in moves:
                tx, ty = nx + ddx, ny + ddy
                if inside(tx, ty):
                    nxt_opts += 1
            score += 0.01 * nxt_opts
        else:
            # Evader: maximize distance; add corner/edge preference and obstacle-avoidance gradient.
            score = d
            edge = (nx == 0) or (nx == w - 1) or (ny == 0) or (ny == h - 1)
            score += 0.25 if edge else 0.0
            # Repel from nearby obstacles to reduce accidental block-by-turns.
            rep = 0
            for ddx in (-1, 0, 1):
                for ddy in (-1, 0, 1):
                    if ddx == 0 and ddy == 0:
                        continue
                    if (nx + ddx, ny + ddy) in obs_set:
                        rep += 1
            score -= 0.2 * rep
            if d == 0:
                score = -1e9  # avoid capture if possible

        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]