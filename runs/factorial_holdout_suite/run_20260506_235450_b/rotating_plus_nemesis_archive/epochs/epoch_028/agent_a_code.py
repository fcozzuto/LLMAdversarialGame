def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))

    obs_list = observation.get("obstacles") or []
    obstacles = set()
    for p in obs_list:
        if p is not None and len(p) >= 2:
            obstacles.add((p[0], p[1]))

    res_list = observation.get("resources") or []
    resources = []
    for r in res_list:
        if r is not None and len(r) >= 2:
            x, y = r[0], r[1]
            if (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_key = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        key = None
        for tx, ty in resources:
            ds = cheb(nx, ny, tx, ty)
            do = cheb(ox, oy, tx, ty)
            # Prefer positions that make us reach earlier; then maximize margin (do-ds); then closer to target
            k = (0 if ds < do else 1, -(do - ds), ds + tx * 0 + ty * 0)
            if key is None or k < key:
                key = k
        if key is not None:
            if best_key is None or key < best_key:
                best_key = key
                best_move = (dx, dy)

    return [best_move[0], best_move[1]]