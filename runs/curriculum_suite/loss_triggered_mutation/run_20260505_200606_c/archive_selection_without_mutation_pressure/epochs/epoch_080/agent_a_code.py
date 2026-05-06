def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation["grid_width"]
    h = observation["grid_height"]

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            rx, ry = int(p[0]), int(p[1])
            if (rx, ry) not in obstacles:
                resources.append((rx, ry))
    if not resources:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    def legal(x, y):
        if x < 0 or x >= w or y < 0 or y >= h:
            return None
        if (x, y) in obstacles:
            return None
        return (x, y)

    best_move = (0, 0)
    best_val = -10**18

    for dx, dy in moves:
        ns = legal(sx + dx, sy + dy)
        if ns is None:
            continue
        nx, ny = ns
        cur_best = -10**18
        for rx, ry in resources:
            d_self = man(nx, ny, rx, ry)
            d_opp = man(ox, oy, rx, ry)
            # Prefer resources where we are closing the gap vs opponent; tie-break by closer.
            val = (d_opp - d_self) * 1000 - d_self * 3
            if rx == ox and ry == oy:
                val += 1  # deterministic tiny bias
            if val > cur_best:
                cur_best = val
        # Mild preference to reduce distance to the currently best target, and keep stability.
        stability = -man(nx, ny, sx, sy) * 0.1
        cur = cur_best + stability + (-abs(nx - (w - 1)) - abs(ny - (h - 1))) * 0.0001
        if cur > best_val:
            best_val = cur
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]