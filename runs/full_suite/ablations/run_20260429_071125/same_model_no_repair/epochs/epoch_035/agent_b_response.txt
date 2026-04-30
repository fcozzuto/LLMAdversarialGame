def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    occ = {(p[0], p[1]) for p in obstacles}

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def cell_score(x, y):
        if (x, y) in occ:
            return -10**18
        if resources:
            best = -10**18
            for rx, ry in resources:
                myd = cheb(x, y, rx, ry)
                opd = cheb(ox, oy, rx, ry)
                lead = opd - myd  # positive means we are closer to this resource
                # Encourage larger lead; break ties by being closer to the resource.
                s = lead * 1000 - myd
                # Small term: generally avoid drifting too far from center line to opponent.
                s += -0.05 * cheb(x, y, ox, oy)
                if s > best:
                    best = s
            return best
        tx, ty = (w - 1) // 2, (h - 1) // 2
        return -cheb(x, y, tx, ty)

    best_move = (0, 0)
    best_val = cell_score(sx, sy)
    # Deterministic tie-break: prefer moves in deltas order (as listed).
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in occ:
            continue
        v = cell_score(nx, ny)
        if v > best_val:
            best_val = v
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]