def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    W = int(observation.get("grid_width", 8) or 8)
    H = int(observation.get("grid_height", 8) or 8)
    obs = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H:
                obs.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H and (x, y) not in obs:
                resources.append((x, y))

    if resources:
        def dist(ax, ay, bx, by):
            dx = abs(ax - bx)
            dy = abs(ay - by)
            return dx if dx > dy else dy

        resources.sort()
        best_t = resources[0]
        best_d = dist(sx, sy, best_t[0], best_t[1])
        for rx, ry in resources[1:]:
            d = dist(sx, sy, rx, ry)
            if d < best_d or (d == best_d and (rx, ry) < best_t):
                best_d, best_t = d, (rx, ry)

        tx, ty = best_t
        cand = [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1), (0, 0)]
        best = None
        best_key = None
        for dx, dy in cand:
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < W and 0 <= ny < H) or (nx, ny) in obs:
                continue
            d = dist(nx, ny, tx, ty)
            key = (d, dx, dy)
            if best_key is None or key < best_key:
                best_key, best = key, [dx, dy]
        if best is not None:
            return best
        return [0, 0]

    cand = [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1), (0, 0)]
    def dist_to_opp(x, y):
        dx = abs(x - ox)
        dy = abs(y - oy)
        return dx if dx > dy else dy
    best = None
    best_key = None
    for dx, dy in cand:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < W and 0 <= ny < H) or (nx, ny) in obs:
            continue
        key = (dist_to_opp(nx, ny), dx, dy)
        if best_key is None or key < best_key:
            best_key, best = key, [dx, dy]
    return best if best is not None else [0, 0]