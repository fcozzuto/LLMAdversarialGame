def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    obstacles = set(map(tuple, observation.get("obstacles", []) or []))
    def inb(x, y): return 0 <= x < w and 0 <= y < h

    self_terr = set(map(tuple, observation.get("self_territory", []) or []))
    opp_terr = set(map(tuple, observation.get("opponent_territory", []) or []))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells", []) or []))

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    def center_dist(p): return abs(p[0] - cx) + abs(p[1] - cy)

    # Pick a strategic target: unclaimed first, otherwise opponent territory.
    target = None
    if unclaimed:
        best_key = None
        for tx, ty in unclaimed:
            if not inb(tx, ty) or (tx, ty) in obstacles: 
                continue
            ds = abs(tx - sx) + abs(ty - sy)
            do = abs(tx - ox) + abs(ty - oy)
            key = (ds, center_dist((tx, ty)), -do)  # closer for us, towards center, farther for opp
            if best_key is None or key < best_key:
                best_key, target = key, (tx, ty)
    if target is None and opp_terr:
        best_key = None
        for tx, ty in opp_terr:
            if not inb(tx, ty) or (tx, ty) in obstacles:
                continue
            ds = abs(tx - sx) + abs(ty - sy)
            do = abs(tx - ox) + abs(ty - oy)
            key = (do - ds, center_dist((tx, ty)), ds)  # go where we can get there relatively first
            if best_key is None or key < best_key:
                best_key, target = key, (tx, ty)
    if target is None:
        # fallback: head towards center while avoiding obstacles
        target = (int(round(cx)), int(round(cy)))

    tx, ty = target

    dirs = [(0, 0), (1, 0), (0, 1), (-1, 0), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    # Prefer moves that claim unclaimed / steal opponent, and reduce distance to target; penalize being closer to opponent than necessary.
    best = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        if (nx, ny) in self_terr:
            gain = 0
        elif (nx, ny) in opp_terr:
            gain = 5
        elif (nx, ny) in unclaimed:
            gain = 3
        else:
            gain = 1  # likely boundary/unknown treated modestly

        dist_to_t = abs(nx - tx) + abs(ny - ty)
        dist_to_opp = abs(nx - ox) + abs(ny - oy)
        # If we can challenge, prioritize; otherwise keep pressure low.
        pressure = dist_to_opp - (abs(sx - ox) + abs(sy - oy))
        key = (-gain, dist_to_t, pressure, center_dist((nx, ny)))
        if best is None or key < best[0]:
            best = (key, [dx, dy])

    return best[1] if best is not None else [0, 0]