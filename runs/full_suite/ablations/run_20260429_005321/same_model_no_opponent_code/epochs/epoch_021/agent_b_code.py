def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obst = set((p[0], p[1]) for p in obstacles if p is not None and len(p) >= 2)

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    best_val = None

    def inside(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obst

    # If no resources, head away from opponent deterministically.
    if not resources:
        for dx, dy in deltas:
            nx, ny = x + dx, y + dy
            if not inside(nx, ny):
                continue
            md = abs(nx - ox) + abs(ny - oy)
            val = (-md, dx, dy)
            if best_val is None or val < best_val:
                best_val, best = val, [dx, dy]
        return best if best is not None else [0, 0]

    # Prefer moves that get closer to some resource while not letting opponent get much closer.
    res = [(r[0], r[1]) for r in resources if r is not None and len(r) >= 2]
    if not res:
        return [0, 0]

    for dx, dy in deltas:
        nx, ny = x + dx, y + dy
        if not inside(nx, ny):
            continue
        d_self = 10**9
        d_opp = 10**9
        for rx, ry in res:
            ds = abs(nx - rx) + abs(ny - ry)
            if ds < d_self:
                d_self = ds
            do = abs(ox - rx) + abs(oy - ry)
            if do < d_opp:
                d_opp = do
        # Higher is better: make opponent "worse" relative to us, tie-break deterministically.
        val = (d_self - d_opp, d_self, d_opp, dx, dy)
        if best_val is None or val < best_val:
            best_val, best = val, [dx, dy]

    return best if best is not None else [0, 0]