def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    deltas = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    def clamp(x, lo, hi):
        return lo if x < lo else hi if x > hi else x

    def dist2(a, b, c, d):
        dx = a - c
        dy = b - d
        return dx * dx + dy * dy

    # If resources exist: go for a resource where we gain relative proximity vs opponent.
    if resources:
        best_res = None
        best_adv = -10**18
        for rx, ry in resources:
            sd = dist2(sx, sy, rx, ry)
            od = dist2(ox, oy, rx, ry)
            adv = (od - sd) - 0.15 * (rx + ry)  # small tie-break toward upper-left-ish
            if adv > best_adv:
                best_adv = adv
                best_res = (rx, ry)
        tx, ty = best_res
        # Evaluate immediate move by resulting advantage toward that target.
        best_move = (0, 0)
        best_val = -10**18
        for dx, dy in deltas:
            nx = clamp(sx + dx, 0, w - 1)
            ny = clamp(sy + dy, 0, h - 1)
            if (nx, ny) in obstacles:
                continue
            myd = dist2(nx, ny, tx, ty)
            opd = dist2(ox, oy, tx, ty)
            val = (opd - myd) - 0.05 * (abs(nx - (w - 1) / 2) + abs(ny - (h - 1) / 2))
            # If target is close, bias even more toward it.
            val += 0.2 * (-myd)
            if val > best_val:
                best_val = val
                best_move = (dx, dy)
        return [int(best_move[0]), int(best_move[1])]

    # No resources: reposition to improve future chances by approaching center while not stepping into obstacles.
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in deltas:
        nx = clamp(sx + dx, 0, w - 1)
        ny = clamp(sy + dy, 0, h - 1)
        if (nx, ny) in obstacles:
            continue
        val = -((nx - cx) ** 2 + (ny - cy) ** 2) - 0.01 * dist2(nx, ny, ox, oy)
        if val > best_val:
            best_val = val
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]