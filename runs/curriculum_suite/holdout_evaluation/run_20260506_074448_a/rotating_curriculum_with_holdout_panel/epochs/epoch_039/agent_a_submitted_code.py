def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]

    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    cx = (w - 1) / 2.0
    cy = (h - 1) / 2.0

    best_move = (0, 0)
    best_val = -10**18

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        val = 0
        if (nx, ny) in set(resources):
            val += 10**6

        if resources:
            dres = 10**9
            for rx, ry in resources:
                d = man(nx, ny, rx, ry)
                if d < dres:
                    dres = d
            val += 5000 / (1 + dres)

        dop = man(nx, ny, ox, oy)
        val += 1200 / (1 + dop)

        # slight preference toward center to break ties deterministically
        ddx, ddy = nx - cx, ny - cy
        val -= 0.01 * (ddx * ddx + ddy * ddy)

        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]