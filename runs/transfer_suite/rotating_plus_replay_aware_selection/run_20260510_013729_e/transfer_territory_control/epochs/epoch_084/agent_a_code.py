def choose_move(observation):
    w = int(observation.get("grid_width", 0) or 0) or 8
    h = int(observation.get("grid_height", 0) or 0) or 8
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    blocked = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            blocked.add((int(p[0]), int(p[1])))

    un_set = set()
    for p in observation.get("unclaimed_cells") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            un_set.add((int(p[0]), int(p[1])))

    res = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            res.append((int(p[0]), int(p[1])))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(px, py):
        return 0 <= px < w and 0 <= py < h

    def md(a, b, c, d):
        x = a - c
        if x < 0: x = -x
        y = b - d
        if y < 0: y = -y
        return x + y

    best = (0, 0)
    best_sc = -10**9

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in blocked:
            continue
        sc = 0
        if (nx, ny) in un_set:
            sc += 10
        if res:
            dmin = 10**9
            for rx, ry in res:
                d = md(nx, ny, rx, ry)
                if d < dmin:
                    dmin = d
            sc += -dmin
        sc += md(nx, ny, ox, oy) * 0.1
        if sc > best_sc:
            best_sc = sc
            best = (dx, dy)

    return [int(best[0]), int(best[1])]