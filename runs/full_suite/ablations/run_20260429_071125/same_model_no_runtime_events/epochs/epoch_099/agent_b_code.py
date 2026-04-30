def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_score = -10**18

    # If somehow out of bounds, just try to step into bounds.
    if not (0 <= sx < w and 0 <= sy < h):
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny):
                return [dx, dy]
        return [0, 0]

    # No resources: chase opponent by approaching their position while keeping distance from obstacles (via legality only).
    if not resources:
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            sdist = cheb(nx, ny, ox, oy)
            score = -sdist
            if score > best_score:
                best_score = score
                best_move = (dx, dy)
        return [best_move[0], best_move[1]]

    # Resource contest heuristic: favor resources we reach quickly and opponent reaches slowly.
    alpha = 1.15
    beta = 0.15  # slight preference to moves that reduce "global" distance to all resources
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        total_improve = 0
        score = 0.0
        for rx, ry in resources:
            d_us = cheb(nx, ny, rx, ry)
            d_op = cheb(ox, oy, rx, ry)
            # higher is better: we want small d_us, large d_op
            us_term = 12.0 / (d_us + 1)
            op_term = 12.0 / (d_op + 1)
            score += us_term - alpha * op_term
            # encourage shortening nearest-resource distance
            total_improve += 1.0 / (d_us + 1)
        score += beta * total_improve
        # small anti-stagnation bias towards moves that change position when tied
        if score == best_score:
            if (dx, dy) != (0, 0):
                best_score = score
                best_move = (dx, dy)
        elif score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]