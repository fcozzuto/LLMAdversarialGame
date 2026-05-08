def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])

    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obs.add((p[0], p[1]))

    self_terr = set(tuple(p) for p in (observation.get("self_territory", []) or []) if isinstance(p, (list, tuple)) and len(p) == 2)
    opp_terr = set(tuple(p) for p in (observation.get("opponent_territory", []) or []) if isinstance(p, (list, tuple)) and len(p) == 2)
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells", []) or []) if isinstance(p, (list, tuple)) and len(p) == 2)

    dirs = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h
    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    targets = list(unclaimed)
    if not targets:
        # Try to pressure opponent territory if nothing unclaimed is visible/available.
        targets = list(opp_terr) if opp_terr else list(self_terr)
    if not targets:
        return [0, 0]

    # Deterministic target selection: favor closer unclaimed, and also slightly bias away/toward opponent.
    # Since opponent is territory_center_claim, push toward their controlled area when possible.
    opp_center = (ox, oy)
    best_t = targets[0]
    best_score = None
    for t in targets:
        if not (inb(t[0], t[1])):
            continue
        d_self = dist((sx, sy), t)
        d_opp = dist(opp_center, t)
        # Lower is better: closer to us, and (if targeting opponent) farther from opponent to reduce their hold.
        score = 10 * d_self - (2 if t in opp_terr else 0) - (0.1 * d_opp)
        if best_score is None or score < best_score or (score == best_score and (t[0], t[1]) < (best_t[0], best_t[1])):
            best_score = score
            best_t = t

    # Choose best one-step move that approaches best_t while avoiding obstacles.
    best_move = (0, 0)
    best_val = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        step_to = dist((nx, ny), best_t)
        # Additional tie-breakers: prefer moving into unclaimed/opp territory (capture/flip) when aiming those.
        capture_bonus = 0.0
        if (nx, ny) in unclaimed:
            capture_bonus += 5.0
        if (nx, ny) in opp_terr:
            capture_bonus += 8.0
        if (nx, ny) in self_terr:
            capture_bonus -= 0.5
        # Slightly reduce distance to opponent to contest their center.
        opp_bias = -0.15 * dist((nx, ny), opp_center)
        val = -step_to + capture_bonus + opp_bias
        if best_val is None or val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]