def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p[:2]) for p in (observation.get("obstacles") or []) if p and len(p) >= 2)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    opp_cells = set(tuple(p[:2]) for p in (observation.get("opponent_territory") or []) if p and len(p) >= 2)
    my_cells = set(tuple(p[:2]) for p in (observation.get("self_territory") or []) if p and len(p) >= 2)
    unclaimed = [tuple(p[:2]) for p in (observation.get("unclaimed_cells") or []) if p and len(p) >= 2]
    resources = [tuple(p[:2]) for p in (observation.get("resources") or []) if p and len(p) >= 2]

    target = None
    if unclaimed:
        best_key = None
        for x, y in unclaimed:
            if not inb(x, y):
                continue
            adj = 0
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    if abs(dx) + abs(dy) == 1 and (x + dx, y + dy) in opp_cells:
                        adj = 2
                        break
                if adj:
                    break
            dself = abs(x - sx) + abs(y - sy)
            dop = abs(x - ox) + abs(y - oy)
            # Prefer stealing near opponent border; otherwise closer expansion.
            k = (0 if adj else 1, dself, -adj, dop, x, y)
            if best_key is None or k < best_key:
                best_key = k
                target = (x, y)

    if target is None:
        pool = resources if resources else ([(ox, oy)] if inb(ox, oy) else [])
        best_key = None
        for x, y in pool:
            if not inb(x, y):
                continue
            k = (abs(x - sx) + abs(y - sy), x, y)
            if best_key is None or k < best_key:
                best_key = k
                target = (x, y)

    if target is None:
        return [0, 0]

    tx, ty = target

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0),  (0, 0),  (1, 0),
             (-1, 1),  (0, 1),  (1, 1)]
    best = None
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        # Secondary objective: keep moving into unclaimed and away from obstacles implicitly by inb.
        next_unclaimed = 1 if (nx, ny) in set(unclaimed) else 0
        next_adv = 0
        if (nx, ny) not in my_cells and (nx, ny) in opp_cells:
            next_adv = 3  # entering opponent cell is profitable when flipping is enabled
        d = abs(nx - tx) + abs(ny - ty)
        k = (d, -next_unclaimed, -next_adv, abs(nx - ox) + abs(ny - oy), dx, dy)
        if best_key is None or k < best_key:
            best_key = k
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]