def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if valid(x, y):
                resources.append((x, y))

    if not valid(sx, sy):
        for y in range(h):
            for x in range(w):
                if valid(x, y):
                    sx, sy = x, y
                    break
            else:
                continue
            break

    def dist_cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # Candidate move scoring: progress to good resource + keep distance from opponent + avoid edge patrol.
    candidates = [(0, 0)]
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx != 0 or dy != 0:
                candidates.append((dx, dy))

    def cell_score(x, y):
        if not valid(x, y):
            return -10**9
        if resources:
            best = -10**9
            for rx, ry in resources:
                # Prefer interior resources (edge patrol targets edges).
                edge_pen = (rx in (0, w - 1) or ry in (0, h - 1))
                d_self = dist_cheb(x, y, rx, ry)
                d_opp = dist_cheb(ox, oy, rx, ry)
                # If opponent is closer to a resource, discourage that direction unless we are also close.
                compete = -2.0 if d_opp < d_self else 0.0
                # Weighted by opponent distance to current location (stay safer while moving).
                best = max(best, (-1.5 * d_self) + (-0.35 * dist_cheb(x, y, ox, oy)) + (-1.0 * int(edge_pen)) + compete)
            return best
        # Fallback: just maximize distance from opponent while staying roughly central
        center = (w - 1) / 2.0, (h - 1) / 2.0
        cx, cy = center
        return (0.9 * dist_cheb(x, y, int(cx), int(cy))) - (1.2 * dist_cheb(x, y, ox, oy))

    best_move = (0, 0)
    best_val = -10**9
    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        val = cell_score(nx, ny)
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]