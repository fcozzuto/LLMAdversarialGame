def choose_move(observation):
    w = observation.get("grid_width", 8) or 8
    h = observation.get("grid_height", 8) or 8
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        best = (10**9, 0, 0)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            d = abs(nx - tx) + abs(ny - ty)
            if d < best[0] or (d == best[0] and (dx, dy) < (best[1], best[2])):
                best = (d, dx, dy)
        return [best[1], best[2]] if best[0] != 10**9 else [0, 0]

    best_res = None
    best_key = None
    for rx, ry in resources:
        ourd = abs(rx - sx) + abs(ry - sy)
        oppd = abs(rx - ox) + abs(ry - oy)
        adv = oppd - ourd  # bigger = better
        # If it's on opponent's current row, assume sweep_rows pressure -> devalue it.
        row_pen = 0
        if ry == oy:
            row_pen = 2 * (h + w)
        # Slightly prefer closer targets to reduce wandering.
        key = (-(adv - row_pen), ourd, abs(rx - (w - 1 - sx)) + abs(ry - (h - 1 - sy)), rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best_res = (rx, ry)

    tx, ty = best_res
    # Choose move that most reduces distance to target with light tie-breaks.
    best = (10**18, 10**18, 10**18, 0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        d = abs(nx - tx) + abs(ny - ty)
        # Prefer also moving off opponent's row if possible (avoid getting swept/contested).
        off_row = 0 if ny == oy else -1
        # Tie-break deterministically by smaller dx, then dy.
        cand = (d, -off_row, abs(nx - ox) + abs(ny - oy), dx, dy)
        if cand < best:
            best = cand
    if best[-2] == 0 and best[-1] == 0 and (sx, sy) in obstacles:
        return [0, 0]
    return [int(best[-2]), int(best[-1])] if best[0] != 10**18 else [0, 0]