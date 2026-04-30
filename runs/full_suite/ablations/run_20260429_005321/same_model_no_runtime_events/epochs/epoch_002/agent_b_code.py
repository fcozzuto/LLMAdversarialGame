def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set((p[0], p[1]) for p in observation["obstacles"])
    resources = observation["resources"] or []

    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    if not resources:
        tx, ty = (w - 1) / 2.0, (h - 1) / 2.0
        best = (0, 0)
        bestv = -10**18
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inside(nx, ny) or (nx, ny) in obstacles:
                continue
            dist_center = max(abs(nx - tx), abs(ny - ty))
            dist_opp = max(abs(nx - ox), abs(ny - oy))
            v = -dist_center + 0.10 * dist_opp
            if v > bestv or (v == bestv and (dx, dy) < best):
                bestv, best = v, (dx, dy)
        return [best[0], best[1]]

    best_res = None
    best_key = None
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        ds = abs(rx - sx) + abs(ry - sy)
        do = abs(rx - ox) + abs(ry - oy)
        # Prefer being closer; break ties toward nearer/lexicographically smaller resource
        key = (do - ds, -min(ds, do), rx, ry)
        if best_key is None or key > best_key:
            best_key = key
            best_res = (rx, ry)

    tx, ty = best_res

    # Decide move by maximizing immediate advantage on target; add small opponent-separation term
    best = (0, 0)
    bestv = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obstacles:
            continue
        ds = abs(tx - nx) + abs(ty - ny)
        do = abs(tx - ox) + abs(ty - oy)
        # Advantage = opponent distance - our distance (bigger is better)
        adv = do - ds
        sep = max(abs(nx - ox), abs(ny - oy))
        # If we are already at/very near target, prioritize holding it
        at = 1.0 if (nx, ny) == (tx, ty) else 0.0
        v = 5.0 * adv + 0.03 * sep + 10.0 * at - 0.001 * (ds)
        if v > bestv or (v == bestv and (dx, dy) < best):
            bestv, best = v, (dx, dy)

    return [best[0], best[1]]