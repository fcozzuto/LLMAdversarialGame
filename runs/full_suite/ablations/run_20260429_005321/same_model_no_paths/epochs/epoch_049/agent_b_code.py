def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
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
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def penalty_near_obs(x, y):
        # small deterministic penalty to keep mobility around obstacles
        p = 0
        for tx in (-1, 0, 1):
            for ty in (-1, 0, 1):
                if tx == 0 and ty == 0:
                    continue
                nx, ny = x + tx, y + ty
                if (nx, ny) in obstacles:
                    p += 1
        return p

    best_move = (0, 0)
    best_score = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            nx, ny = sx, sy

        # Choose move maximizing advantage against nearest contested resources
        score = 0
        for rx, ry in resources:
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # Strongly prefer resources where we are closer than opponent; also prefer closeness.
            advantage = (do - ds)  # positive if we can reach earlier
            val = 3 * advantage - ds
            # If both can reach in same time, slightly prefer the one closer to opponent (to break ties by disruption)
            if advantage == 0:
                val -= 0.5 * do
            score += val

        # Additional small mobility term: prefer reducing distance to best single target
        best_single = -10**18
        for rx, ry in resources:
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            a = do - ds
            v = 5 * a - ds
            if v > best_single:
                best_single = v
        score = 0.7 * score + 0.3 * best_single
        score -= 0.08 * penalty_near_obs(nx, ny)

        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]