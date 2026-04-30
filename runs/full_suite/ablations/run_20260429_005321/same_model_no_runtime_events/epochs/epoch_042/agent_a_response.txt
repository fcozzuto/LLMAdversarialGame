def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
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

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist_cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx >= dy else dy

    def score_pos(nx, ny):
        if resources:
            best_gain = -10**18
            best_dist = 10**18
            for rx, ry in resources:
                sd = dist_cheb(nx, ny, rx, ry)
                od = dist_cheb(ox, oy, rx, ry)
                gain = od - sd  # positive means we are closer than opponent
                if gain > best_gain:
                    best_gain = gain
                    best_dist = sd
                elif gain == best_gain and sd < best_dist:
                    best_dist = sd
            # Encourage big lead; if no lead, still reduce opponent advantage and approach quickly.
            return best_gain * 100 - best_dist
        # No resources: deterministically contest by moving toward the opponent's diagonal lane and center.
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        d1 = dist_cheb(nx, ny, ox, oy)
        d2 = dist_cheb(nx, ny, int(cx), int(cy))
        return -d1 * 3 - d2

    best = None
    best_val = -10**18
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        v = score_pos(nx, ny)
        if v > best_val:
            best_val = v
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]