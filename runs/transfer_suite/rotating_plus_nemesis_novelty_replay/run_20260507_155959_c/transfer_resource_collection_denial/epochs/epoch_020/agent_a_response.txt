def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set((p[0], p[1]) for p in obstacles)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def md(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    legal = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obs:
                legal.append((dx, dy))
    if not legal:
        return [0, 0]

    res = [(r[0], r[1]) for r in resources if inb(r[0], r[1]) and (r[0], r[1]) not in obs]
    if not res:
        return [0, 0]

    # Choose move that maximizes how much closer we are than opponent to our best target.
    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        cur_best = -10**18
        for rx, ry in res:
            d_self = md(nx, ny, rx, ry)
            d_op = md(ox, oy, rx, ry)
            margin = d_op - d_self  # positive => we likely win this resource
            # Small preference for shorter travel among equal margins
            val = margin * 1000 - d_self
            if val > cur_best:
                cur_best = val
        # Mild preference to not drift: keep closer to our current best compared to staying
        if cur_best > best_val:
            best_val = cur_best
            best_move = (dx, dy)
        elif cur_best == best_val:
            # Deterministic tie-break: prefer move with smallest d_self to the best target
            # (recompute via current best target distance)
            # Find lexicographically smallest move among best values after comparing distances
            pass

    return [int(best_move[0]), int(best_move[1])]