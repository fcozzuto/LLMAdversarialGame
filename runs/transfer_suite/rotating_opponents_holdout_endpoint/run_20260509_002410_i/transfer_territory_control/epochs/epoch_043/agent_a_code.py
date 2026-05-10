def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or [0, 0]
    ox, oy = observation.get("opponent_position") or [w - 1, h - 1]

    obs = observation.get("obstacles") or []
    obstacles = set(map(tuple, obs))

    res = observation.get("resources") or []
    resources = set(map(tuple, res))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist(a, b):
        ax, ay = a
        bx, by = b
        return abs(ax - bx) + abs(ay - by)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    cur = (sx, sy)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        n = (nx, ny)
        score = 0
        if n in resources:
            score += 100
        score += 20 if dist(n, (ox, oy)) < dist(cur, (ox, oy)) else 0
        score -= 5 if dist(n, (ox, oy)) > dist(cur, (ox, oy)) else 0
        if best is None or score > best[0] or (score == best[0] and (dx, dy) < best[1]):
            best = (score, (dx, dy))
    return list(best[1]) if best else [0, 0]