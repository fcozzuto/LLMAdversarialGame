def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)

    obs_list = observation.get("obstacles", []) or []
    obstacles = set()
    for p in obs_list:
        try:
            obstacles.add((p[0], p[1]))
        except:
            pass

    resources = observation.get("resources", []) or []
    res_pos = []
    for p in resources:
        try:
            res_pos.append((p[0], p[1]))
        except:
            pass

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def king_dist(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    candidates = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            candidates.append((dx, dy, nx, ny))
    if not candidates:
        return [0, 0]

    if res_pos:
        tx, ty = min(res_pos, key=lambda p: (king_dist(sx, sy, p[0], p[1]), p[0], p[1]))
        best = None
        best_key = None
        for dx, dy, nx, ny in candidates:
            d_self = king_dist(nx, ny, tx, ty)
            d_opp = king_dist(nx, ny, ox, oy)
            key = (d_self, -d_opp, dx, dy)
            if best_key is None or key < best_key:
                best_key = key
                best = (dx, dy)
        return [best[0], best[1]]

    cx = (w - 1) // 2
    cy = (h - 1) // 2
    go_toward_center = (king_dist(sx, sy, cx, cy) <= king_dist(sx, sy, ox, oy))
    best = None
    best_key = None
    for dx, dy, nx, ny in candidates:
        if go_toward_center:
            d = king_dist(nx, ny, cx, cy)
            key = (d, dx, dy, nx, ny)
        else:
            d = -king_dist(nx, ny, ox, oy)
            key = (d, dx, dy, nx, ny)
        if best_key is None or key < best_key:
            best_key = key
            best = (dx, dy)
    return [best[0], best[1]]