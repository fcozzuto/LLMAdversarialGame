def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obs.add((int(p[0]), int(p[1])))

    unclaimed = observation.get("unclaimed_cells") or []
    self_count = int(observation.get("self_territory_count") or 0)
    opp_count = int(observation.get("opponent_territory_count") or 0)
    opp_terr = observation.get("opponent_territory") or []

    dirs8 = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def legal(x, y):
        return inside(x, y) and (x, y) not in obs

    def man(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx + dy

    def edge_bonus(x, y):
        if x == 0 or y == 0 or x == w - 1 or y == h - 1:
            return 0.15
        return 0.0

    # If behind, apply pressure: target nearby opponent territory to enable flipping.
    pressure = self_count <= opp_count
    candidates = []
    if pressure and opp_terr:
        for x, y in opp_terr:
            x, y = int(x), int(y)
            if legal(x, y):
                candidates.append((x, y))
    else:
        for p in unclaimed:
            if isinstance(p, (list, tuple)) and len(p) == 2:
                x, y = int(p[0]), int(p[1])
                if legal(x, y):
                    candidates.append((x, y))
        if not candidates:
            candidates = [(ox, oy)]  # last resort

    # Score targets by distance advantage; prefer positions we can reach sooner than opponent.
    best = None
    best_score = None
    for x, y in candidates[:32]:  # keep deterministic and cheap
        ds = man(sx, sy, x, y)
        do = man(ox, oy, x, y)
        # If flipping on entry helps, targets closer to us and farther from them are best.
        score = (do - ds) + edge_bonus(x, y) - (0.02 * (ds + do))
        # Slight preference for targets not behind us diagonally (reduces oscillation)
        if x == sx and y == sy:
            score -= 0.2
        if best_score is None or score > best_score:
            best_score = score
            best = (x, y)

    tx, ty = best if best is not None else (ox, oy)

    # Choose a legal one-step move that reduces distance to target, with a small tie-break.
    best_move = [0, 0]
    best_val = None
    for dx, dy in dirs8:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        ds1 = man(nx, ny, tx, ty)
        do1 = man(nx, ny, ox, oy)
        val = -ds1 + 0.03 * (do1)  # keep us moving toward target while slightly increasing opponent distance
        if best_val is None or val > best_val:
            best_val = val
            best_move = [dx, dy]

    return best_move if best_move != [None, None] else [0, 0]