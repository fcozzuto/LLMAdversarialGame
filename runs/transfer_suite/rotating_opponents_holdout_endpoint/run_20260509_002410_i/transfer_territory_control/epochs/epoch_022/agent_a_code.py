def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))

    obstacles = set(map(tuple, observation.get("obstacles") or []))
    self_t = set(map(tuple, observation.get("self_territory") or []))
    opp_t = set(map(tuple, observation.get("opponent_territory") or []))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells") or []))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    best_val = None

    target_list = list(unclaimed)
    if not target_list:
        target_list = list(opp_t) if opp_t else [tuple(observation.get("opponent_position", (ox, oy)))]

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obstacles:
            continue

        cell = (nx, ny)
        d_opp = abs(nx - ox) + abs(ny - oy)
        d_best = 10**9
        for tx, ty in target_list:
            d = abs(nx - tx) + abs(ny - ty)
            if d < d_best:
                d_best = d

        val = -d_best  # closer to target is better
        if cell in unclaimed:
            val += 100
        if cell in self_t:
            val += 5
        if cell in opp_t:
            val += 2
        val += (d_opp * 0.3)  # slightly safer from opponent

        key = (dx, dy)
        if best is None or val > best_val or (val == best_val and key < best):
            best = key
            best_val = val

    if best is None:
        return [0, 0]
    return [best[0], best[1]]