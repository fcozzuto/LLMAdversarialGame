def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    res = observation.get("resources") or []
    obs = observation.get("obstacles") or []

    obstacles = set()
    for p in obs:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((p[0], p[1]))

    resources = []
    for r in res:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            resources.append((r[0], r[1]))

    def dist(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx + dy

    def blocked(x, y):
        return x < 0 or x >= w or y < 0 or y >= h or (x, y) in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = [0, 0]
    best_score = -10**18

    close = dist(sx, sy, ox, oy) <= 2
    center_x = (w - 1) // 2
    center_y = (h - 1) // 2

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if blocked(nx, ny):
            continue

        score = 0
        if resources:
            dres = min(dist(nx, ny, rx, ry) for rx, ry in resources)
            score += 1000 - 20 * dres
        else:
            score += -dist(nx, ny, center_x, center_y)

        dop = dist(nx, ny, ox, oy)
        if close:
            score += 2000 - 50 * dop
        else:
            score += -5 * dop

        if dx == 0 and dy == 0:
            score -= 1

        if score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move