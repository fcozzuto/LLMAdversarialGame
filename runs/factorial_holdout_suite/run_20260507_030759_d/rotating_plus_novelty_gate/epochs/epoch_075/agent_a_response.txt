def choose_move(observation):
    w = observation.get("grid_width", 8) or 8
    h = observation.get("grid_height", 8) or 8
    sx, sy = observation.get("self_position", (0, 0)) or (0, 0)
    ox, oy = observation.get("opponent_position", (0, 0)) or (0, 0)
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    obstacles = set((p[0], p[1]) for p in obstacles if isinstance(p, (list, tuple)) and len(p) >= 2)
    resset = set((p[0], p[1]) for p in resources if isinstance(p, (list, tuple)) and len(p) >= 2)

    if (sx, sy) in resset:
        return [0, 0]

    legal = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                legal.append((dx, dy))
    if not legal or not resset:
        return [0, 0]

    def mdist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    mypos = (sx, sy)
    opppos = (ox, oy)

    # Pick a resource where we are closer than the opponent; otherwise fall back to the closest.
    best_r = None
    best_key = None
    for r in resset:
        dm = mdist(mypos, r)
        do = mdist(opppos, r)
        # primary: we want dm-do very negative (we win contests). secondary: smaller dm.
        # small preference to break ties deterministically by coordinates.
        key = (dm - do, dm, r[0], r[1])
        if best_key is None or key < best_key:
            best_key = key
            best_r = r

    tx, ty = best_r
    opp_dist = mdist(opppos, (sx, sy))

    # Greedy step toward target, with tie-break to keep distance from opponent.
    best_move = None
    best_step_key = None
    # Deterministic ordering preference if still tied
    ordered = sorted(legal, key=lambda d: (d[0], d[1]))
    for dx, dy in ordered:
        nx, ny = sx + dx, sy + dy
        step_dm = mdist((nx, ny), (tx, ty))
        step_opp = mdist(opppos, (nx, ny))
        # prefer smaller distance to target; then larger opponent distance (avoid being swept/intercepted)
        key = (step_dm, -step_opp, dx, dy)
        if best_step_key is None or key < best_step_key:
            best_step_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]