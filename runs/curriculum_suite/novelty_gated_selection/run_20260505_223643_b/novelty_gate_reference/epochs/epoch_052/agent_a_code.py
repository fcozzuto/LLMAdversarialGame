def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
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

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    if not resources:
        # drift toward opponent side
        tx = w - 1 if ox < sx else 0
        ty = h - 1 if oy < sy else 0
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        return [dx, dy]

    best_move = [0, 0]
    best_val = -10**9
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        # Choose target that maximizes our advantage over opponent, then encourages closeness to it.
        local_best = -10**9
        for rx, ry in resources:
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            adv = (do - ds)  # positive means we are closer than opponent
            val = adv * 10 - ds  # primary: advantage, secondary: reach quickly
            # encourage also blocking by preferring resources currently "contested" near opponent
            val += (6 - do) * (1 if adv > 0 else 0)  # small deterministic boost
            if val > local_best:
                local_best = val
        # tie-break: prefer moving closer (overall) if values equal
        if local_best > best_val or (local_best == best_val and (abs(dx) + abs(dy), -dx, -dy) < (abs(best_move[0]) + abs(best_move[1]), -best_move[0], -best_move[1])):
            best_val = local_best
            best_move = [dx, dy]

    return best_move