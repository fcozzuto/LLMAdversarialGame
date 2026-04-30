def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    s = observation.get("self_position") or [0, 0]
    o = observation.get("opponent_position") or [0, 0]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

    obstacles = set()
    for b in observation.get("obstacles") or []:
        if b and len(b) >= 2:
            bx, by = int(b[0]), int(b[1])
            if 0 <= bx < w and 0 <= by < h:
                obstacles.add((bx, by))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obstacles:
                resources.append((rx, ry))

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        best = (0, 0)
        bestv = -10**9
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not in_bounds(nx, ny):
                continue
            # drift to center and away from opponent slightly (deterministic tie-break)
            v = -(abs(nx - (w - 1) / 2) + abs(ny - (h - 1) / 2)) - 0.2 * cheb(nx, ny, ox, oy)
            if v > bestv or (v == bestv and (dx, dy) < best):
                bestv = v
                best = (dx, dy)
        return [best[0], best[1]]

    # Target scoring: prefer resources we can reach sooner than opponent; deterministic ordering.
    res_sorted = sorted(resources, key=lambda r: (cheb(sx, sy, r[0], r[1]) - cheb(ox, oy, r[0], r[1]), r[0], r[1]))
    res_sorted = res_sorted[:8]

    best_move = (0, 0)
    best_val = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny):
            continue
        # Evaluate best target from this next position
        best_target_val = -10**18
        for rx, ry in res_sorted:
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # higher is better
            # big weight to being ahead in distance; small regularization to reduce absolute distance
            val = (do - ds) * 1000 - ds
            if (rx == nx and ry == ny):
                val += 50000
            if val > best_target_val or (val == best_target_val and (rx, ry) < (best_move[0], best_move[1])):
                best_target_val = val
        # tie-break deterministically by move order
        if best_target_val > best_val or (best_target_val == best_val and (dx, dy) < best_move):
            best_val = best_target_val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]