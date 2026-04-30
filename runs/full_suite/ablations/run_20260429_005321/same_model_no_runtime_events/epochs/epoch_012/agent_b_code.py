def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])

    obs_list = observation.get("obstacles") or []
    obstacles = set()
    for p in obs_list:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((p[0], p[1]))

    res_list = observation.get("resources") or []
    resources = []
    for p in res_list:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            t = (p[0], p[1])
            if t not in obstacles:
                resources.append(t)

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(a, b, c, d):
        dx = a - c
        if dx < 0:
            dx = -dx
        dy = b - d
        if dy < 0:
            dy = -dy
        return dx if dx >= dy else dy

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    legal = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inside(nx, ny) and (nx, ny) not in obstacles:
            legal.append((dx, dy, nx, ny))

    if not legal:
        return [0, 0]

    if resources:
        best = None
        for dx, dy, nx, ny in legal:
            best_res_key = None
            for rx, ry in resources:
                myd = cheb(nx, ny, rx, ry)
                opd = cheb(ox, oy, rx, ry)
                # Prefer smaller my distance; tie-break by larger opponent distance; deterministic by coord.
                key = (myd, -opd, rx, ry)
                if best_res_key is None or key < best_res_key:
                    best_res_key = key
            # Prefer move that bests resource; tie-break by distance to opponent; then by direction.
            key = (best_res_key[0], best_res_key[1], cheb(nx, ny, ox, oy), dx, dy)
            if best is None or key < best[0]:
                best = (key, [dx, dy])
        return best[1]

    # No resources: move toward opponent if path is clear, otherwise stay.
    target_is_better = cheb(sx, sy, ox, oy)
    best = [0, 0]
    best_key = (10**9, 0, 0)
    for dx, dy, nx, ny in legal:
        myd = cheb(nx, ny, ox, oy)
        key = (myd, dx, dy)
        if myd < best_key[0]:
            best_key = key
            best = [dx, dy]
        elif myd == best_key[0] and (dx, dy) < (best[0], best[1]):
            best = [dx, dy]
    return best