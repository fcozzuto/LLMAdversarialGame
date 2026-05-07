def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or (0, 0)
    op = observation.get("opponent_position") or (0, 0)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            px, py = int(p[0]), int(p[1])
            if 0 <= px < w and 0 <= py < h:
                obstacles.add((px, py))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obstacles:
                resources.append((rx, ry))

    if not resources:
        dx, dy = 0, 0
        if ox > sx and (sx + 1, sy) not in obstacles and sx + 1 < w:
            dx, dy = 1, 0
        elif ox < sx and (sx - 1, sy) not in obstacles and sx - 1 >= 0:
            dx, dy = -1, 0
        elif oy > sy and (sx, sy + 1) not in obstacles and sy + 1 < h:
            dx, dy = 0, 1
        elif oy < sy and (sx, sy - 1) not in obstacles and sy - 1 >= 0:
            dx, dy = 0, -1
        return [dx, dy]

    def md(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    best = None
    best_sc = -10**18
    for rx, ry in resources:
        sd = abs(rx - sx) + abs(ry - sy)
        od = abs(rx - ox) + abs(ry - oy)
        sc = (2000 if sd <= od else 0) + (od - sd) * 40 - sd * 5
        if sd == 0:
            sc += 500
        if sc > best_sc:
            best_sc = sc
            best = (rx, ry)

    tx, ty = best
    moves = [(1, 0), (-1, 0), (0, 1), (0, -1), (0, 0)]
    best_d = None
    best_move = [0, 0]
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            d = abs(tx - nx) + abs(ty - ny)
            if best_d is None or d < best_d or (d == best_d and (dx, dy) != (0, 0) and best_move == [0, 0]):
                best_d = d
                best_move = [dx, dy]
    return best_move