def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or [0, 0]
    ox, oy = observation.get("opponent_position") or [0, 0]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    role = str(observation.get("self_role") or "")
    r = role.lower()
    we_pursuer = ("pursuer" in r) or ("pursue" in r and "evader" not in r)
    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    deltas.sort()
    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy
    def free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    def dist_to_closest_wall(x, y):
        return min(x, y, w - 1 - x, h - 1 - y)

    best = None
    best_score = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        d = cheb(nx, ny, ox, oy)
        if we_pursuer:
            # primary: reduce distance; secondary: stay away from walls to avoid easy evasion slips
            score = d * 100 + (-(dist_to_closest_wall(nx, ny)))
            # smaller is better; keep deterministic smallest score, then delta order already sorted
            if best_score is None or score < best_score:
                best_score = score
                best = (dx, dy)
        else:
            # evader: maximize distance; secondary: move toward farthest corner from pursuer
            corner = max(corners, key=lambda c: cheb(c[0], c[1], ox, oy))
            corner_bias = -cheb(nx, ny, corner[0], corner[1])  # prefer closer to that corner
            score = -d * 100 + corner_bias
            if best_score is None or score > best_score:
                best_score = score
                best = (dx, dy)

    if best is None:
        return [0, 0]
    return [best[0], best[1]]