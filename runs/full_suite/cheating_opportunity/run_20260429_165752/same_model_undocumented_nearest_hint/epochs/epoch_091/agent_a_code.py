def choose_move(observation):
    W = int(observation.get("grid_width") or 8)
    H = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [W - 1, H - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obs = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H:
                obs.add((x, y))

    res = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < W and 0 <= y < H and (x, y) not in obs:
                res.append((x, y))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def ok(nx, ny):
        return 0 <= nx < W and 0 <= ny < H and (nx, ny) not in obs

    def dist(a, b):
        dx = a[0] - b[0]
        if dx < 0: dx = -dx
        dy = a[1] - b[1]
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def best_resource_move():
        best = (10**9, -10**9)
        best_dxdy = (0, 0)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            if not res:
                continue
            dmin = 10**9
            for t in res:
                dt = dist((nx, ny), t)
                if dt < dmin:
                    dmin = dt
            val = -dmin
            if val > best[1]:
                best = (dmin, val)
                best_dxdy = (dx, dy)
        return best_dxdy

    if res:
        dxdy = best_resource_move()
        return [int(dxdy[0]), int(dxdy[1])]

    # No visible resources: move toward opponent while avoiding obstacles deterministically.
    target = (ox, oy)
    best_d = 10**9
    best_dxdy = (0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        d = dist((nx, ny), target)
        if d < best_d or (d == best_d and (dx, dy) < best_dxdy):
            best_d = d
            best_dxdy = (dx, dy)
    return [int(best_dxdy[0]), int(best_dxdy[1])]