def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    obstacles = set()
    for p in observation.get("obstacles", []):
        try:
            obstacles.add((p[0], p[1]))
        except Exception:
            pass
    resources = []
    for p in observation.get("resources", []):
        try:
            resources.append((p[0], p[1]))
        except Exception:
            pass

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist2(a, b, c, d):
        dx = a - c
        dy = b - d
        return dx * dx + dy * dy

    def nearest_resource(x, y):
        best = None
        bestd = None
        for rx, ry in resources:
            d = dist2(x, y, rx, ry)
            if bestd is None or d < bestd:
                bestd = d
                best = (rx, ry)
        return best, bestd

    target, trd = nearest_resource(sx, sy)
    to_op = dist2(sx, sy, ox, oy)
    use_resource = (target is not None) and (trd is not None) and trd <= to_op

    def score_for(dx, dy):
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            return -10**18, -10**9
        if dx == 0 and dy == 0:
            stay_pen = 1
        else:
            stay_pen = 0
        if use_resource:
            d = dist2(nx, ny, target[0], target[1])
        else:
            d = dist2(nx, ny, ox, oy)
        mobility = 0
        for mdx, mdy in moves:
            ax, ay = nx + mdx, ny + mdy
            if valid(ax, ay):
                mobility += 1
        return (-d - stay_pen, mobility)

    best_move = (0, 0)
    best_s = None
    best_m = None
    for dx, dy in moves:
        s, m = score_for(dx, dy)
        if best_s is None or s > best_s or (s == best_s and m > best_m):
            best_s, best_m = s, m
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]