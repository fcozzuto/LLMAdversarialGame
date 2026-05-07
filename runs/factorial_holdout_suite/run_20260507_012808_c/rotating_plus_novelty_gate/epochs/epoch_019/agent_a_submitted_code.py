def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    w = int(observation.get("grid_width", 0) or 0)
    h = int(observation.get("grid_height", 0) or 0)
    resources = observation.get("resources") or []
    obstacles_in = observation.get("obstacles") or []
    if w <= 0 or h <= 0:
        return [0, 0]
    obstacles = set()
    for p in obstacles_in:
        try:
            x, y = p
            obstacles.add((int(x), int(y)))
        except:
            pass

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def d(a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

    if not resources:
        return [0, 0]

    s = (int(sx), int(sy))
    o = (int(ox), int(oy))

    def pick_key(r):
        rx, ry = r
        r = (int(rx), int(ry))
        myd = d(s, r)
        opd = d(o, r)
        return (myd - opd, myd, r[0], r[1])

    target = min(resources, key=pick_key)
    tx, ty = int(target[0]), int(target[1])

    best_move = (0, 0)
    best_val = 10**9
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = s[0] + dx, s[1] + dy
            if not ok(nx, ny):
                continue
            nd = d((nx, ny), (tx, ty))
            # Primary: get closer to target; Secondary: if equal, keep away from opponent
            oppd = d((nx, ny), o)
            val = (nd, -oppd, dx, dy)
            if val < best_val:
                best_val = val
                best_move = (dx, dy)

    dx, dy = best_move
    return [int(dx), int(dy)]