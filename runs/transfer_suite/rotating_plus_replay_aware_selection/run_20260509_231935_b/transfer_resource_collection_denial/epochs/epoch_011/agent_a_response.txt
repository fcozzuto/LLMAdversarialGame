def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])

    resources = observation.get("resources", []) or []
    obstacles_list = observation.get("obstacles", []) or []
    obstacles = set((p[0], p[1]) for p in obstacles_list)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist8(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1))

    if not resources:
        cx, cy = w // 2, h // 2
        best = (10**9, 0, 0)
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                nx, ny = sx, sy
            d = dist8(nx, ny, cx, cy)
            cand = (d, dx, dy, nx, ny)
            if cand < best:
                best = cand
        return [best[1], best[2]]

    # Prioritize resources that are closer to us and farther from opponent (deterministic).
    k = 0.85  # opponent distance weight

    best_val = -10**18
    best = (0, 0)

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            nx, ny = sx, sy

        # If we can step onto a resource, take it decisively.
        if (nx, ny) in obstacles:
            continue

        best_target = None
        best_target_val = -10**18

        for rx, ry in resources:
            ds = dist8(nx, ny, rx, ry)
            do = dist8(ox, oy, rx, ry)
            val = (-ds) + k * (-do)  # maximize negative self dist and negative opp dist
            # Tie-break: prefer smaller self dist, then larger opp dist
            if val > best_target_val or (val == best_target_val and (ds, -do, rx, ry) < (best_target[0], best_target[1], best_target[2], best_target[3])):
                best_target_val = val
                best_target = (ds, -do, rx, ry)

        # Small preference for moves that decrease our nearest-resource distance.
        cur_ds = min(dist8(sx, sy, rx, ry) for rx, ry in resources)
        move_ds = best_target[0]
        adjust = 0.15 * (cur_ds - move_ds)
        total = best_target_val + adjust

        if total > best_val or (total == best_val and (dx, dy) < best):
            best_val = total
            best = (dx, dy)

    return [best[0], best[1]]