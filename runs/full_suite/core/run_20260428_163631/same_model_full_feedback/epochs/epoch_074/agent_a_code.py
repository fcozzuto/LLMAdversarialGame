def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        # Fallback: move to increase distance from opponent while staying on-board.
        best = (0, 0)
        bestv = -10**18
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            v = cheb(nx, ny, ox, oy)
            if v > bestv:
                bestv = v
                best = (dx, dy)
        return [best[0], best[1]]

    # Choose move maximizing (progress to best target - progress for opponent), with obstacle-safe constraint.
    best_move = (0, 0)
    best_val = -10**18
    # Pre-sort resources deterministically by a fixed key to stabilize ties.
    resources_sorted = sorted(resources, key=lambda r: (r[1], r[0]))
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        # Heuristic: pick target that we can reach relatively well and opponent poorly.
        # Value is computed from our and opponent distances at the resulting position.
        move_val = -10**18
        for rx, ry in resources_sorted:
            d_us = cheb(nx, ny, rx, ry)
            d_op = cheb(ox, oy, rx, ry)
            # Favor targets where opponent is farther; also prefer immediate closeness to us.
            # Reward being on/near a resource strongly.
            v = (d_op - d_us) * 3 - d_us
            if d_us == 0:
                v += 1000
            # Slightly bias towards resources closer to our current position to reduce wandering.
            v -= cheb(sx, sy, rx, ry) * 0.15
            if v > move_val:
                move_val = v
        # Extra: penalize moves that reduce our distance to opponent too much (avoid getting "blocked" or mirrored).
        move_val -= (cheb(nx, ny, ox, oy) < cheb(sx, sy, ox, oy)) * 2
        if move_val > best_val:
            best_val = move_val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]