def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obst = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obst:
                resources.append((x, y))

    def manh(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    def best_race(xm, ym):
        if not resources:
            return -10**18, 10**18
        best = -10**18
        best_d = 10**18
        for rx, ry in resources:
            dm = manh(xm, ym, rx, ry)
            do = manh(ox, oy, rx, ry)
            race = do - dm
            if race > best:
                best = race
                best_d = dm
            elif race == best and dm < best_d:
                best_d = dm
        return best, best_d

    best_move = (0, 0)
    best_val = -10**18
    best_dm = 10**18
    best_center = 10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obst:
            continue
        race, dm = best_race(nx, ny)
        center = abs(nx - cx) + abs(ny - cy)
        val = race
        if val > best_val or (val == best_val and dm < best_dm) or (val == best_val and dm == best_dm and center < best_center):
            best_val = val
            best_dm = dm
            best_center = center
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]