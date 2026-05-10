def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    W, H = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs_set = {(p[0], p[1]) for p in obstacles}

    def inb(x, y):
        return 0 <= x < W and 0 <= y < H

    if not resources:
        # Counter-sweep: align our y with opponent row direction tendency, else drift to center.
        tx, ty = (W - 1 if sx < ox else 0), oy
        # If blocked or out of bounds, fallback to center.
        if not inb(tx, ty) or (tx, ty) in obs_set:
            tx, ty = (W - 1) // 2, (H - 1) // 2
        best = (0, 0)
        bestv = -10**9
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                nx, ny = sx + dx, sy + dy
                if not inb(nx, ny) or (nx, ny) in obs_set:
                    continue
                v = - (abs(nx - tx) + abs(ny - ty)) - 0.05 * (abs(nx - ox) + abs(ny - oy))
                if v > bestv:
                    bestv = v
                    best = (dx, dy)
        return [best[0], best[1]]

    # Choose a target where we are closer than the opponent (opportunity).
    best_t = None
    best_key = None
    for r in resources:
        rx, ry = r[0], r[1]
        sd = abs(rx - sx) + abs(ry - sy)
        od = abs(rx - ox) + abs(ry - oy)
        # Primary: advantage for us; Secondary: minimize our distance; Tertiary: deterministic coord.
        key = (od - sd, -sd, -rx, -ry)
        if best_key is None or key > best_key:
            best_key = key
            best_t = (rx, ry)

    tx, ty = best_t
    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    # Move one step toward target while also stealing timing vs opponent if possible.
    best = (0, 0)
    bestv = -10**9
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs_set:
            continue
        sd2 = abs(tx - nx) + abs(ty - ny)
        od2 = abs(tx - ox) + abs(ty - oy)  # opponent position static for move scoring
        # Encourage getting closer to target; discourage letting opponent be closer immediately.
        v = -sd2 + 0.35 * (od2 - sd2) - 0.01 * (abs(nx - ox) + abs(ny - oy))
        # If our move doesn't improve target distance, still allow it when it increases safety.
        if sd2 == abs(tx - sx) + abs(ty - sy):
            v += 0.02 * (-abs(ny - oy))  # mild row-steal against sweep_rows
        if v > bestv:
            bestv = v
            best = (dx, dy)

    return [best[0], best[1]]