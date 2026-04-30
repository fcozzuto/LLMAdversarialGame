def choose_move(observation):
    W = observation.get("grid_width", 8) or 8
    H = observation.get("grid_height", 8) or 8
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [W - 1, H - 1]) or [W - 1, H - 1]
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        if p and len(p) >= 2:
            x, y = p[0], p[1]
            if 0 <= x < W and 0 <= y < H:
                obs.add((x, y))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < W and 0 <= ny < H and (nx, ny) not in obs:
            legal.append((dx, dy))
    if not legal:
        return [0, 0]

    def mindist(x, y, pts):
        if not pts:
            return 10**9
        m = 10**9
        for tx, ty in pts:
            d = abs(x - tx) + abs(y - ty)
            if d < m:
                m = d
        return m

    valid_res = []
    for r in resources:
        if r and len(r) >= 2:
            x, y = r[0], r[1]
            if 0 <= x < W and 0 <= y < H and (x, y) not in obs:
                valid_res.append((x, y))

    opp_d0 = abs(sx - ox) + abs(sy - oy)
    best = None
    best_key = None
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        ds = mindist(nx, ny, valid_res)
        do = mindist(ox, oy, valid_res)
        # Prefer reducing our distance to nearest resource while keeping advantage over opponent.
        # If no resources, prefer moving away from opponent.
        if valid_res:
            key = (do - ds, -ds, -nx, -ny)
        else:
            d1 = abs(nx - ox) + abs(ny - oy)
            key = (d1 - opp_d0, d1, -nx, -ny)
        if best_key is None or key > best_key:
            best_key = key
            best = (dx, dy)

    return [int(best[0]), int(best[1])]