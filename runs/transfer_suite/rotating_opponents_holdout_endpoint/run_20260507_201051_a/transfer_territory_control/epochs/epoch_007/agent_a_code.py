def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])

    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    self_terr = set(tuple(p) for p in (observation.get("self_territory", []) or []))
    opp_terr = set(tuple(p) for p in (observation.get("opponent_territory", []) or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells", []) or []))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    unq = list(unclaimed)
    if unq:
        targets = unq
    else:
        opp_list = list(opp_terr) if opp_terr else [(ox, oy)]
        targets = opp_list if opp_list else [(ox, oy)]

    def step_score(cell):
        x, y = cell
        s = 0
        if cell in opp_terr:
            s += 18
        if cell in unclaimed:
            s += 10
        if cell in self_terr:
            s += 2
        if cell == (ox, oy):
            s += 1
        # prefer moving closer to best target
        bestd = 10**9
        for tx, ty in targets:
            d = abs(tx - x) + abs(ty - y)
            if d < bestd:
                bestd = d
        s -= 0.5 * bestd
        # discourage adjacency to obstacles
        adj_obs = 0
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if inb(nx, ny) and (nx, ny) in obstacles:
                adj_obs += 1
        s -= 0.25 * adj_obs
        return s

    best = (-10**18, 0, 0)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        sc = step_score((nx, ny))
        # deterministic tie-break: smallest dx then dy order as listed
        if sc > best[0] or (sc == best[0] and (dx, dy) < (best[1], best[2])):
            best = (sc, dx, dy)

    # fallback: move towards opponent if possible
    if best[0] <= -10**17:
        dx = 0 if ox == sx else (1 if ox > sx else -1)
        dy = 0 if oy == sy else (1 if oy > sy else -1)
        for cand in [(dx, dy), (dx, 0), (0, dy), (0, 0)]:
            cx, cy = sx + cand[0], sy + cand[1]
            if inb(cx, cy) and (cx, cy) not in obstacles:
                return [cand[0], cand[1]]
        return [0, 0]

    return [best[1], best[2]]