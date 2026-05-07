def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    ox, oy = observation.get("opponent_position", [0, 0])

    obs = set()
    for p in obstacles:
        if p and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int):
                obs.add((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    if not resources:
        return [0, 0]

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = (0, 0)
    best_val = -10**18

    # Evaluate each possible move by best target value (deterministic).
    for dxm, dym in moves:
        nx, ny = sx + dxm, sy + dym
        if not free(nx, ny):
            continue

        immediate = 1 if any(nx == rx and ny == ry for rx, ry in resources) else 0
        val = immediate * 10**6

        # Choose resource that maximizes our advantage (earlier reach), with distance bias.
        for rx, ry in resources:
            us = cheb(nx, ny, rx, ry)
            opp = cheb(ox, oy, rx, ry)
            # If we can arrive sooner, prioritize strongly; if equal, still slightly prefer.
            adv = (opp - us)
            score = 0
            if adv > 0:
                score += adv * 2000
            else:
                score += adv * 200
            # Prefer closer-to-goal resources to commit.
            score += (12 - us) * 5
            # If opponent is extremely close, reduce commitment unless we are also close.
            if opp <= us and opp <= 2:
                score -= (2 - opp) * 50
            if score > val:
                val = score

        if val > best_val:
            best_val = val
            best = (dxm, dym)

    return [int(best[0]), int(best[1])]