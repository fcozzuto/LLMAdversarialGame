def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    cand = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def dist2(ax, ay, bx, by):
        dx, dy = ax - bx, ay - by
        return dx * dx + dy * dy

    if not resources:
        corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        tx, ty = min(corners, key=lambda p: (dist2(p[0], p[1], ox, oy), p[0], p[1]))
        if (sx, sy) == (tx, ty):
            tx, ty = max(corners, key=lambda p: (dist2(p[0], p[1], ox, oy), -p[0], -p[1]))
        best = None
        for dx, dy in cand:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            key = (dist2(nx, ny, tx, ty), dist2(nx, ny, ox, oy), nx, ny)
            if best is None or key < best:
                best = key
                best_move = [dx, dy]
        return best_move if best is not None else [0, 0]

    best_res = None
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        sd = abs(rx - sx) + abs(ry - sy)
        od = abs(rx - ox) + abs(ry - oy)
        key = (-(od - sd), sd, rx, ry)  # maximize (od-sd) => minimize negative
        if best_res is None or key < best_res[0]:
            best_res = (key, (rx, ry))
    tx, ty = best_res[1]

    best = None
    for dx, dy in cand:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        sd = abs(tx - nx) + abs(ty - ny)
        od = abs(tx - ox) + abs(ty - oy)
        md = abs(tx - nx) + abs(ty - ny) - (abs(tx - ox) + abs(ty - oy))  # self lead smaller is better
        key = (md, sd, dist2(nx, ny, ox, oy), nx, ny)
        if best is None or key < best:
            best = key
            best_move = [dx, dy]
    return best_move if best is not None else [0, 0]