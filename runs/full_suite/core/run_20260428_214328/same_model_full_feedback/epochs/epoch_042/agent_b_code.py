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
    if not resources:
        return [0, 0]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist_cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    best_move = (0, 0)

    for dxm, dym in moves:
        nx, ny = sx + dxm, sy + dym
        if not inside(nx, ny):
            continue

        # Evaluate by best resource for us starting from next position
        local_best = None
        local_best_r = None
        for rx, ry in resources:
            d_us = dist_cheb(nx, ny, rx, ry)
            d_op = dist_cheb(ox, oy, rx, ry)
            # Advantage: prefer resources where opponent is farther.
            # Penalize too-fast opponent claims; deterministic tie breaks.
            adv = d_op - d_us
            block_pen = 0
            if d_us == 0:
                block_pen = 1000
            elif d_us <= 1 and d_op <= 1 and (rx + ry) % 2 == 0:
                block_pen = -3
            val = (adv + block_pen, -d_us, -rx, -ry)
            if local_best is None or val > local_best:
                local_best = val
                local_best_r = (rx, ry)

        # If we can't reach any resource (shouldn't happen), fall back
        if local_best is None:
            continue

        # Also discourage moving into being closer to opponent's best target
        d_to_oppbest = dist_cheb(nx, ny, ox, oy)
        final_val = (local_best[0], local_best[1], -d_to_oppbest, local_best[2], local_best[3])
        if best is None or final_val > best:
            best = final_val
            best_move = (dxm, dym)

    return [int(best_move[0]), int(best_move[1])]