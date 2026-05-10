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

    self_role = (observation.get("self_role") or "").lower()
    opp_role = (observation.get("opponent_role") or "").lower()
    is_evader = ("evader" in self_role) or (("evader" in opp_role) and ("pursuer" not in self_role))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def nearest_ob_dist(x, y):
        if not obstacles:
            return 99
        best = 99
        for bx, by in obstacles:
            d = cheb(x, y, bx, by)
            if d < best:
                best = d
        return best

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_score = -10**9 if not is_evader else 10**9

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        d = cheb(nx, ny, ox, oy)
        od = nearest_ob_dist(nx, ny)
        # pursuer: minimize distance, keep away from obstacles
        if not is_evader:
            score = -d * 1000 + od
            if score > best_score:
                best_score = score
                best_move = (dx, dy)
        else:
            # evader: maximize distance, avoid being pinned too close to obstacles/edges
            edge_pen = min(nx, w - 1 - nx, ny, h - 1 - ny)
            score = d * 1000 + od + edge_pen
            if score < best_score:
                best_score = score
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]