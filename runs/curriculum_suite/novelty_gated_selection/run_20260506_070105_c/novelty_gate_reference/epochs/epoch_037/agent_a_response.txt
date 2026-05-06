def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def man(ax, ay, bx, by):
        d = ax - bx
        if d < 0:
            d = -d
        e = ay - by
        if e < 0:
            e = -e
        return d + e

    def interior_bias(x, y):
        # Favor interior targets (edge_patrol opponent tends to stay near edges)
        dleft, dright = x, w - 1 - x
        ddown, dup = y, h - 1 - y
        return min(dleft, dright, ddown, dup)

    best = [0, 0]
    best_val = -10**18

    # Break ties deterministically by a fixed direction order
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        val = -man(nx, ny, ox, oy)  # discourage wandering toward opponent
        for tx, ty in resources:
            my_d = man(nx, ny, tx, ty)
            opp_d = man(ox, oy, tx, ty)
            adv = opp_d - my_d  # positive means we're closer
            # Prefer wins/denial; also prefer interior targets.
            tval = 12 * adv - my_d + 2 * interior_bias(tx, ty)
            val = max(val, tval)
        if val > best_val:
            best_val = val
            best = [dx, dy]

    return best