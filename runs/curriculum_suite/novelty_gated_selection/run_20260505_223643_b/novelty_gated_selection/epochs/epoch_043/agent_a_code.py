def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))

    def clamp(x, y):
        if x < 0:
            x = 0
        elif x >= w:
            x = w - 1
        if y < 0:
            y = 0
        elif y >= h:
            y = h - 1
        return x, y

    def manh(ax, ay, bx, by):
        a = ax - bx
        if a < 0:
            a = -a
        b = ay - by
        if b < 0:
            b = -b
        return a + b

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = observation.get("resources", []) or []
    res = []
    for p in resources:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                res.append((x, y))
    if not res:
        return [0, 0]

    def nearest_dist(x, y):
        best = 10**9
        for rx, ry in res:
            d = manh(x, y, rx, ry)
            if d < best:
                best = d
        return best

    opp_near = nearest_dist(int(ox), int(oy))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_score = -10**18
    best_move = (0, 0)

    for dx, dy in moves:
        nx, ny = clamp(int(sx) + dx, int(sy) + dy)
        if (nx, ny) in obstacles:
            nx, ny = int(sx), int(sy)
        my_near = nearest_dist(nx, ny)
        score = (opp_near - my_near) * 1000 - my_near
        if score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]