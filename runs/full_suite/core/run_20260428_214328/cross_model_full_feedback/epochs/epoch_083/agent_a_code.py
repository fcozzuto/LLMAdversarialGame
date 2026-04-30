def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obst = set()
    for p in (observation.get("obstacles") or []):
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    res = []
    for p in (observation.get("resources") or []):
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obst:
                res.append((x, y))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def score_cell(nx, ny):
        if (nx, ny) in obst:
            return None
        best_r = 10**9
        for rx, ry in res:
            d = abs(nx - rx)
            e = abs(ny - ry)
            dist = d if d > e else e
            if dist < best_r:
                best_r = dist
        if res:
            dx = abs(nx - ox)
            dy = abs(ny - oy)
            opp_dist = dx if dx > dy else dy
            return -best_r * 10 + opp_dist
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        dxc = abs(nx - cx)
        dyc = abs(ny - cy)
        center_dist = dxc if dxc > dyc else dyc
        return -center_dist - (abs(nx - ox) + abs(ny - oy)) * 0.001

    best_score = -10**30
    best_move = [0, 0]
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        sc = score_cell(nx, ny)
        if sc is None:
            continue
        if sc > best_score:
            best_score = sc
            best_move = [dx, dy]

    return best_move