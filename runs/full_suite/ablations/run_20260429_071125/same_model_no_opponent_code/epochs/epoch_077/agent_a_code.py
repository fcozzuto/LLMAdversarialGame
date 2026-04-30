def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
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
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if resources:
        target = None
        bestd = 10**18
        for rx, ry in resources:
            d = cheb(sx, sy, rx, ry)
            do = cheb(ox, oy, rx, ry)
            if d < bestd or (d == bestd and (do - d) > 0):
                bestd = d
                target = (rx, ry)
    else:
        self_scores = observation.get("scores") or [0, 0]
        my_score = self_scores[0] if isinstance(self_scores, (list, tuple)) and len(self_scores) > 0 else 0
        opp_score = self_scores[1] if isinstance(self_scores, (list, tuple)) and len(self_scores) > 1 else 0
        if my_score >= opp_score:
            target = (w - 1, h - 1) if (sx + sy) <= (ox + oy) else (0, 0)
        else:
            target = (0, 0) if (sx + sy) <= (ox + oy) else (w - 1, h - 1)

    tx, ty = target
    best_move = (0, 0)
    best_val = 10**18

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        dist = cheb(nx, ny, tx, ty)
        opp_dist = cheb(nx, ny, ox, oy)
        val = dist * 1000 - opp_dist  # prefer getting closer to target; also slightly avoid proximity to opponent
        if val < best_val:
            best_val = val
            best_move = (dx, dy)
        elif val == best_val:
            if (dx, dy) < best_move:
                best_move = (dx, dy)

    return [best_move[0], best_move[1]]