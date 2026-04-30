def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    s = observation.get("self_position") or [0, 0]
    o = observation.get("opponent_position") or [w - 1, h - 1]
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

    def cheb(a, b):
        dx = a[0] - b[0]
        if dx < 0: dx = -dx
        dy = a[1] - b[1]
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = (None, -10**9)

    res_set = set(resources)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        if not resources:
            # If no visible resources, move to reduce distance to opponent to contest capture zones.
            val = -cheb((nx, ny), (ox, oy))
            if val > best[1] or (val == best[1] and (dx, dy) < best[0]):
                best = ((dx, dy), val)
            continue

        my = (nx, ny)
        my_d = 10**9
        best_gap = -10**9
        best_res = None
        for t in resources:
            dmy = cheb(my, t)
            dop = cheb((ox, oy), t)
            gap = dop - dmy  # positive means we are closer (or opponent farther)
            if gap > best_gap or (gap == best_gap and dmy < my_d) or (gap == best_gap and dmy == my_d and (t[0], t[1]) < (best_res[0], best_res[1] if best_res else (10**9, 10**9))):
                best_gap = gap
                my_d = dmy
                best_res = t

        val = 1000 * int((nx, ny) in res_set) + 20 * best_gap - my_d
        # Mild center preference to reduce oscillation.
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        val -= 0.1 * (abs(nx - cx) + abs(ny - cy))

        if val > best[1] or (val == best[1] and (dx, dy) < best[0] if best[0] is not None else True):
            best = ((dx, dy), val)

    return [int(best[0][0]), int(best[0][1])]