def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]

    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    unclaimed = [tuple(p) for p in (observation.get("unclaimed_cells") or [])]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    if unclaimed:
        best_t = None
        best_tv = -10**18
        for tx, ty in unclaimed:
            if (tx, ty) in obstacles:
                continue
            v = (man(ox, oy, tx, ty) - man(sx, sy, tx, ty))  # prefer targets closer than opponent
            if v > best_tv:
                best_tv = v
                best_t = (tx, ty)
            elif v == best_tv and best_t is not None:
                if (tx, ty) < best_t:
                    best_t = (tx, ty)
        tx, ty = best_t if best_t is not None else (sx, sy)
        best_move = (0, 0)
        best_mv = -10**18
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inside(nx, ny):
                continue
            v = -man(nx, ny, tx, ty) + 0.1 * man(nx, ny, ox, oy)  # closer to target, farther from opponent
            if v > best_mv or (v == best_mv and (dx, dy) < best_move):
                best_mv = v
                best_move = (dx, dy)
        return [int(best_move[0]), int(best_move[1])]

    # No unclaimed: move to maximize distance from opponent while staying safe (prefer nearer to center slightly)
    cx, cy = (w - 1) // 2, (h - 1) // 2
    best_move = (0, 0)
    best_mv = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        v = man(nx, ny, ox, oy) - 0.01 * man(nx, ny, cx, cy)
        if v > best_mv or (v == best_mv and (dx, dy) < best_move):
            best_mv = v
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]