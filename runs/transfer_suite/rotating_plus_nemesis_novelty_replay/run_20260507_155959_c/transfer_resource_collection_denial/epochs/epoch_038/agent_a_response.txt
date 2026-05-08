def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        if len(p) >= 2:
            obs.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    if (sx, sy) in obs:
        return [0, 0]

    def dist(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    res = []
    for r in resources:
        if len(r) >= 2:
            rx, ry = r[0], r[1]
            if inb(rx, ry) and (rx, ry) not in obs:
                res.append((rx, ry))
    if not res:
        return [0, 0]

    best = None
    best_val = None
    for rx, ry in res:
        dself = dist(sx, sy, rx, ry)
        dopp = dist(ox, oy, rx, ry)
        # Prefer resources where we beat opponent (dopp-dself large); tie-break by shorter self distance
        val = (dopp - dself, -dself, -(dist(ox, oy, 0, 0) + 0))  # stable deterministic tie
        if best_val is None or val > best_val:
            best_val = val
            best = (rx, ry)

    rx, ry = best
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def score_for_step(nx, ny):
        if (nx, ny) in obs:
            return None
        dnew = dist(nx, ny, rx, ry)
        dself_after = dnew
        dopp_to_target = dist(ox, oy, rx, ry)
        # Keep us winning: maximize (dopp-dself_after), and then minimize distance to target.
        return (dopp_to_target - dself_after, -dself_after, -dnew)

    best_step = None
    best_step_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        v = score_for_step(nx, ny)
        if best_step_val is None or v > best_step_val:
            best_step_val = v
            best_step = (dx, dy)

    if best_step is None:
        return [0, 0]
    return [int(best_step[0]), int(best_step[1])]