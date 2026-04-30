def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    def inb(x, y): return 0 <= x < w and 0 <= y < h

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y) and (x, y) not in obstacles:
                resources.append((x, y))

    if not inb(sx, sy) or (sx, sy) in obstacles or not resources:
        return [0, 0]

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    best_dx, best_dy = 0, 0
    best_score = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        my_best = 10**9
        op_best_at_my = 10**9
        # Choose a target resource that favors "I'm closer than opponent" deterministically.
        for rx, ry in resources:
            dmy = man(nx, ny, rx, ry)
            dop = man(ox, oy, rx, ry)
            if dmy < my_best or (dmy == my_best and dop < op_best_at_my):
                my_best = dmy
                op_best_at_my = dop

        # Score: win the race; also encourage shorter my_best.
        score = (op_best_at_my - my_best) * 100 - my_best
        # Small deterministic tie-breaker to reduce oscillation: prefer not to worsen toward center-ish.
        score += -(abs((nx - (w - 1) / 2)) + abs((ny - (h - 1) / 2))) * 0.001

        if score > best_score:
            best_score = score
            best_dx, best_dy = dx, dy

    return [int(best_dx), int(best_dy)]