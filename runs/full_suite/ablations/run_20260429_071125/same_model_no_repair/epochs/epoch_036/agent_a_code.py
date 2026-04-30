def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    occ = {(p[0], p[1]) for p in obstacles}

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def eval_cell(x, y):
        if (x, y) in occ:
            return -10**18
        if resources:
            best = -10**18
            for rx, ry in resources:
                myd = cheb(x, y, rx, ry)
                opd = cheb(ox, oy, rx, ry)
                lead = opd - myd  # positive if we are closer than opponent
                s = lead * 2000 - myd
                # Prefer breaking toward the opponent-side resources / general progress
                s += -0.05 * cheb(x, y, (w - 1) // 2, (h - 1) // 2)
                # If we can reach this resource sooner, strongly value it
                s += 5000 if lead > 0 and myd == min(myd, 999999) else 0
                if s > best:
                    best = s
            return best
        # No visible resources: move to center line between agents
        cx = (sx + ox) // 2
        cy = (sy + oy) // 2
        return -cheb(x, y, cx, cy)

    best_move = [0, 0]
    best_val = -10**18
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in occ:
            v = eval_cell(nx, ny)
        else:
            v = -10**18
        if v > best_val:
            best_val = v
            best_move = [dx, dy]

    if best_val <= -10**17:
        # Fallback: deterministic stay if boxed or invalid moves
        return [0, 0]
    return best_move