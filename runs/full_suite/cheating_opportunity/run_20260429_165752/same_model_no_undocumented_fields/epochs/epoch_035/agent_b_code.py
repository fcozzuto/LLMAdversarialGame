def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    s = observation.get("self_position") or [0, 0]
    o = observation.get("opponent_position") or [0, 0]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

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

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def best_valid_dir(scoring):
        best = None
        best_key = None
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if valid(nx, ny):
                key = scoring(nx, ny)
                if best_key is None or key > best_key:
                    best_key = key
                    best = (dx, dy)
        return best if best is not None else (0, 0)

    if resources:
        tx, ty = min(resources, key=lambda r: (cheb(sx, sy, r[0], r[1]), cheb(ox, oy, r[0], r[1]), r[0], r[1]))
        def score(nx, ny):
            d_self = cheb(nx, ny, tx, ty)
            d_opp = cheb(nx, ny, ox, oy)
            return (-d_self, d_opp, -nx, -ny)
        dx, dy = best_valid_dir(score)
        return [dx, dy]

    cx, cy = w // 2, h // 2
    def score(nx, ny):
        d_opp = cheb(nx, ny, ox, oy)
        d_ctr = cheb(nx, ny, cx, cy)
        return (d_opp, -d_ctr, -nx, -ny)
    dx, dy = best_valid_dir(score)
    return [dx, dy]