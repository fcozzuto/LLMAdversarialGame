def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = observation.get("obstacles", [])
    obs = set()
    for p in obstacles:
        obs.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

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

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        myd0 = dist((nx, ny), (ox, oy))
        if resources:
            best_gain = None
            for r in resources:
                rx, ry = r
                myd = dist((nx, ny), (rx, ry))
                opd = dist((ox, oy), (rx, ry))
                gain = opd - myd  # prefer becoming closer than opponent
                if best_gain is None or gain > best_gain or (gain == best_gain and myd < dist((sx, sy), (rx, ry))):
                    best_gain = gain
            score = (best_gain, -dist((nx, ny), (ox, oy)), -dist((nx, ny), (sx, sy)))
        else:
            score = (myd0, -dist((nx, ny), (ox, oy)), -dist((nx, ny), (sx, sy)))
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]