def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or [0, 0]
    ox, oy = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

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
    if not resources:
        return [0, 0]

    def cheb(a, b):
        dx = a[0] - b[0]
        if dx < 0: dx = -dx
        dy = a[1] - b[1]
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    best = None
    best_key = None
    for r in resources:
        sd = cheb((sx, sy), r)
        od = cheb((ox, oy), r)
        key = (od - sd, -sd, -(abs(r[0]) + abs(r[1])), -(r[0] * 16 + r[1]))
        if best_key is None or key > best_key:
            best_key = key
            best = r

    tx, ty = best
    dirs = [(-1, -1), (0, -1), (1, -1),
            (-1, 0),  (0, 0),  (1, 0),
            (-1, 1),  (0, 1),  (1, 1)]

    cand = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            d = cheb((nx, ny), (tx, ty))
            # Prefer moving to reduce distance; break ties deterministically with opponent distance and coordinates
            oppd = cheb((ox, oy), (tx, ty))
            key = (-(d), (oppd - d), -(abs(nx - tx) + abs(ny - ty)), -(nx * 16 + ny), dx, dy)
            cand.append((key, dx, dy))
    if not cand:
        return [0, 0]

    cand.sort(reverse=True)
    return [int(cand[0][1]), int(cand[0][2])]