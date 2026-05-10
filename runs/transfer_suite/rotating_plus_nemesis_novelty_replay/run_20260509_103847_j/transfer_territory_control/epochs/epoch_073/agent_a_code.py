def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    opT = set()
    for p in observation.get("opponent_territory") or []:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                opT.add((x, y))

    unC = []
    for p in observation.get("unclaimed_cells") or []:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                unC.append((x, y))
                if len(unC) >= 60:
                    break

    moves = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0)]
    best = None
    best_sc = -10**9

    def md(a, b, c, d):
        v = a - c
        if v < 0:
            v = -v
        u = b - d
        if u < 0:
            u = -u
        return v + u

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue
        sc = 0
        if unC:
            dmin = 10**9
            for tx, ty in unC:
                d = md(nx, ny, tx, ty)
                if d < dmin:
                    dmin = d
            sc += 200 - dmin
        else:
            sc += 150 - md(nx, ny, ox, oy)
        if (nx, ny) in opT:
            sc -= 80
        if nx == sx and ny == sy:
            sc -= 5
        if sc > best_sc:
            best_sc = sc
            best = [dx, dy]

    if best is None:
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                return [dx, dy]
        return [0, 0]
    return best