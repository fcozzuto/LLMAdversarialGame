def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    s = observation.get("self_position") or [0, 0]
    o = observation.get("opponent_position") or [w - 1, h - 1]
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

    if not resources:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_adv = -10**18
    best_sd = 10**18

    # Evaluate each move by its best reachable target advantage (opp - self).
    for mdx, mdy in moves:
        nx, ny = sx + mdx, sy + mdy
        if not valid(nx, ny):
            continue
        # Slightly penalize moves that increase separation from opponent's likely race line.
        local_best_adv = -10**18
        local_best_sd = 10**18
        for rx, ry in resources:
            sd = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            adv = od - sd
            if adv > local_best_adv or (adv == local_best_adv and sd < local_best_sd):
                local_best_adv = adv
                local_best_sd = sd
        # Tie-break prefers smaller self distance, then lexicographic move order.
        if (local_best_adv > best_adv or
            (local_best_adv == best_adv and local_best_sd < best_sd)):
            best_adv = local_best_adv
            best_sd = local_best_sd
            best_move = (mdx, mdy)

    return [int(best_move[0]), int(best_move[1])]