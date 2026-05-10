def choose_move(observation):
    w = int(observation["grid_width"]); h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    obs_cells = set((p[0], p[1]) for p in (observation.get("obstacles") or []))

    self_set = set((p[0], p[1]) for p in (observation.get("self_territory") or []))
    opp_set = set((p[0], p[1]) for p in (observation.get("opponent_territory") or []))
    unclaimed = [(p[0], p[1]) for p in (observation.get("unclaimed_cells") or [])]

    def md(a, b): return abs(a[0] - b[0]) + abs(a[1] - b[1])
    opp_list = list(opp_set); self_list = list(self_set)

    turn = int(observation.get("turn_index", 0))
    parity = turn & 1

    if unclaimed:
        nearest_un = min(unclaimed, key=lambda p: md((sx, sy), p))
    else:
        nearest_un = None
    if opp_list:
        nearest_opp = min(opp_list, key=lambda p: md((sx, sy), p))
    else:
        nearest_opp = None

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    best_score = -10**18

    un_set = set(unclaimed)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h or (nx, ny) in obs_cells:
            continue

        cell = (nx, ny)
        score = 0
        if cell in opp_set:
            score += 120  # direct flipping pressure
        if cell in un_set:
            score += 30   # claim unclaimed
        if cell in self_set:
            score += 8    # stable territory

        # Directional pressure: move toward nearest unclaimed, else toward opponent.
        if nearest_un is not None:
            score += 6 * (md((sx, sy), nearest_un) - md((nx, ny), nearest_un))
        elif nearest_opp is not None:
            score += 8 * (md((sx, sy), nearest_opp) - md((nx, ny), nearest_opp))

        # Avoid hugging your own corner if no unclaimed: slight push toward center.
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        score += 0.5 * ((abs(sx - cx) + abs(sy - cy)) - (abs(nx - cx) + abs(ny - cy)))

        # Deterministic tie-breaker: prefer moves that alternate among equivalent options.
        tie = (dx + 2 * dy + parity) % 3
        score += 0.01 * (2 - tie)

        if score > best_score:
            best_score = score
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]