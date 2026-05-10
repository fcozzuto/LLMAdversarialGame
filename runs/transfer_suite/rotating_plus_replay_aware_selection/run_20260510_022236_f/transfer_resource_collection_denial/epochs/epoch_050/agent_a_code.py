def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set((int(x), int(y)) for x, y in obstacles if 0 <= int(x) < w and 0 <= int(y) < h)

    res = []
    for x, y in resources:
        x, y = int(x), int(y)
        if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
            res.append((x, y))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def dist(a, b):
        ax, ay = a
        bx, by = b
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    if not res:
        tx, ty = ox, oy
    else:
        tx, ty = min(res, key=lambda p: dist((sx, sy), p))

    best = (10**9, 10**9, 0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obs:
            continue
        score = dist((nx, ny), (tx, ty))
        # tie-breaker: prefer staying closer to center of line between players (deterministic)
        opp_score = dist((nx, ny), (ox, oy))
        key = (score, opp_score, dx, dy)
        if key < best:
            best = key

    if best[2] == 0 and best[3] == 0:
        # if no legal moves found, fall back to staying put
        if (sx, sy) in obs:
            for dx, dy in moves:
                nx, ny = sx + dx, sy + dy
                if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs:
                    return [dx, dy]
            return [0, 0]
    return [int(best[2]), int(best[3])]