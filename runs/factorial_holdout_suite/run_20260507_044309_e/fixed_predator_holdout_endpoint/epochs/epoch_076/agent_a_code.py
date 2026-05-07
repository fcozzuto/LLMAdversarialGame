def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            px, py = int(p[0]), int(p[1])
            if 0 <= px < w and 0 <= py < h:
                obstacles.add((px, py))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obstacles:
                resources.append((rx, ry))

    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = abs(ax - bx)
        dy = abs(ay - by)
        return dx if dx > dy else dy

    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    best_move = (0, 0)
    best_val = None

    # Prefer stepping toward resources where we can match or beat opponent in time.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue
        count_win = 0
        min_my = 10**9
        min_gap = 10**9
        for rx, ry in resources:
            myt = cheb(nx, ny, rx, ry)
            opt = cheb(ox, oy, rx, ry)
            gap = opt - myt
            if gap >= 0:
                count_win += 1
                if myt < min_my:
                    min_my = myt
                if gap < min_gap:
                    min_gap = gap
        center_bias = -abs(nx - (w - 1) // 2) - abs(ny - (h - 1) // 2)
        # If no winning resources this turn, still move to best "near win".
        if count_win == 0:
            for rx, ry in resources:
                myt = cheb(nx, ny, rx, ry)
                opt = cheb(ox, oy, rx, ry)
                gap = opt - myt
                if gap > -min_gap:
                    min_gap = -gap
                    min_my = myt
            val = (-1_000_000 + min_gap, -min_my, center_bias)
        else:
            val = (count_win, min_gap, -min_my, center_bias)

        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]