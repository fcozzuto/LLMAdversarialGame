def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    resources = observation.get("resources") or []
    if not resources:
        return [0, 0]

    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles") or []))

    def man(a, b, c, d):
        x = a - c
        if x < 0:
            x = -x
        y = b - d
        if y < 0:
            y = -y
        return x + y

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    # pick what the opponent is likely to grab (nearest resource)
    best_r = None
    best_d = None
    for r in resources:
        rx, ry = int(r[0]), int(r[1])
        d = man(ox, oy, rx, ry)
        if best_d is None or d < best_d or (d == best_d and (rx, ry) < (int(best_r[0]), int(best_r[1]))):
            best_d = d
            best_r = (rx, ry)
    rx, ry = best_r

    # interception point near the midpoint of the opponent->resource shortest path
    dxs = 0 if rx == ox else (1 if rx > ox else -1)
    dys = 0 if ry == oy else (1 if ry > oy else -1)
    d0 = man(ox, oy, rx, ry)
    k = (d0 - 1) // 2
    tx, ty = ox, oy
    while k >= 0:
        candx = ox + dxs * k
        candy = oy + dys * k
        if inside(candx, candy):
            tx, ty = candx, candy
            break
        k -= 1
    if not inside(tx, ty):
        tx, ty = rx, ry if inside(rx, ry) else (sx, sy)

    # move toward intercept using best available neighboring step
    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    best_score = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        score = man(nx, ny, tx, ty)
        tie = (man(nx, ny, rx, ry), man(nx, ny, ox, oy), nx, ny)
        if best_score is None or score < best_score or (score == best_score and tie < best[0]):
            best_score = score
            best = (tie, [dx, dy])
    return best[1] if best is not None else [0, 0]