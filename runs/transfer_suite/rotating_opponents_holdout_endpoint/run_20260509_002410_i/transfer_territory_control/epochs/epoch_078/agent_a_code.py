def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    sx, sy = int(sx), int(sy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    opp_t = set((int(p[0]), int(p[1])) for p in (observation.get("opponent_territory") or []) if p is not None and len(p) >= 2)
    self_t = set((int(p[0]), int(p[1])) for p in (observation.get("self_territory") or []) if p is not None and len(p) >= 2)
    unclaimed = set((int(p[0]), int(p[1])) for p in (observation.get("unclaimed_cells") or []) if p is not None and len(p) >= 2)

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    ox, oy = int(ox), int(oy)

    preferred_targets = []
    for tset in (unclaimed, opp_t):
        for (tx, ty) in tset:
            dcent = abs(tx - cx) + abs(ty - cy)
            if dcent <= 6.0:
                preferred_targets.append((dcent, tx, ty))
    if preferred_targets:
        preferred_targets.sort()
        _, tx, ty = preferred_targets[0]
    else:
        tx, ty = int(round(cx)), int(round(cy))

    moves = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1), (0, 0)]
    best = None
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        d_target = abs(nx - tx) + abs(ny - ty)
        d_center = abs(nx - cx) + abs(ny - cy)
        d_opp = abs(nx - ox) + abs(ny - oy)
        val = 0

        if (nx, ny) in opp_t:
            val += 1200 - 6 * d_target
            val += 20 - 2 * d_opp
        elif (nx, ny) in unclaimed:
            val += 180 - 10 * d_center - 3 * d_target
        elif (nx, ny) in self_t:
            val += 40 - 2 * d_center - d_target
        else:
            val += 5 - 2 * d_center - d_target

        if d_target == 0:
            val += 200
        if dx == 0 and dy == 0:
            val -= 3

        if val > best_val or (val == best_val and (dx, dy) < best):
            best_val = val
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]