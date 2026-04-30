def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = observation.get("obstacles", [])
    res = observation.get("resources", [])
    obs_set = set((x, y) for x, y in obstacles)
    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h
    if not res:
        best = (0, 0)
        bestv = None
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obs_set:
                continue
            v = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
            if bestv is None or v > bestv:
                bestv = v
                best = (dx, dy)
        return [best[0], best[1]]

    targets = res
    def nearest_dist2(nx, ny):
        md = None
        for tx, ty in targets:
            if (tx, ty) in obs_set:
                continue
            d = (tx - nx) * (tx - nx) + (ty - ny) * (ty - ny)
            if md is None or d < md:
                md = d
        return md if md is not None else 10**18

    best_delta = (0, 0)
    best_val = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs_set:
            continue
        d2 = nearest_dist2(nx, ny)
        opp_d2 = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
        on_resource = 1 if (nx, ny) in set((x, y) for x, y in targets) else 0
        # Prefer stepping onto a resource; otherwise minimize distance to nearest resource,
        # while slightly keeping away from opponent.
        val = (-(on_resource * 10**12) + d2 - 0.03 * opp_d2, dx, dy)
        if best_val is None or val < best_val:
            best_val = val
            best_delta = (dx, dy)
    return [best_delta[0], best_delta[1]]