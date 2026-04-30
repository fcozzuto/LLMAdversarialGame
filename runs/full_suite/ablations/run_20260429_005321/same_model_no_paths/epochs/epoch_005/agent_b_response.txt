def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = [tuple(p) for p in observation.get("resources", [])]
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def md(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def adj_obstacle_pen(x, y):
        pen = 0
        for dx, dy in moves:
            if dx == 0 and dy == 0:
                continue
            if (x + dx, y + dy) in obstacles:
                pen += 2
        return pen

    # Pick a target resource maximizing our distance advantage; if none, go center.
    if resources:
        best_t = None
        best_k = None
        for rx, ry in resources:
            myd = md(sx, sy, rx, ry)
            opd = md(ox, oy, rx, ry)
            # Higher means we are closer than opponent and likely to secure.
            k = (-(opd - myd), myd, -((rx - cx) ** 2 + (ry - cy) ** 2), rx, ry)
            if best_k is None or k < best_k:
                best_k = k
                best_t = (rx, ry)
        tx, ty = best_t
    else:
        tx, ty = int(round(cx)), int(round(cy))

    # Evaluate candidate next moves.
    best_move = (0, 0)
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obstacles:
            continue

        # Core: distance advantage at target (or center if no resources).
        myd_t = md(nx, ny, tx, ty)
        opd_t = md(ox, oy, tx, ty)
        adv = opd_t - myd_t  # bigger => we are closer to target than opponent

        # If we step onto a resource, huge.
        res = 1 if (nx, ny) in set(resources) else 0

        # Denial: consider the closest resource to us after the move; prefer moves that keep opponent farther.
        denial = 0
        if resources:
            best_diff = None
            for rx, ry in resources:
                d_my = md(nx, ny, rx, ry)
                d_op = md(ox, oy, rx, ry)
                diff = d_op - d_my
                if best_diff is None or diff > best_diff or (diff == best_diff and d_my < md(sx, sy, rx, ry)):
                    best_diff = diff
            denial = best_diff

        # Avoid obstacle-adjacent squares; small center preference.
        center = -0.01 * (((nx - cx) ** 2) + ((ny - cy) ** 2))
        val = (res * 1e6) + (adv * 50) + (denial * 8) + center - adj_obstacle_pen(nx, ny)

        k = (-(val), dx, dy)  # deterministic tie-break: smallest dx then dy after neg
        if best_val is None or k < best_val:
            best_val = k
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]