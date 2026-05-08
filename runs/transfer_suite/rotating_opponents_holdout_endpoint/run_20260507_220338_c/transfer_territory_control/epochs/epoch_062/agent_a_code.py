def choose_move(observation):
    w = observation.get("grid_width") or 8
    h = observation.get("grid_height") or 8
    try:
        w = int(w); h = int(h)
    except:
        w = 8; h = 8
    sp = observation.get("self_position") or (0, 0)
    op = observation.get("opponent_position") or (w - 1, h - 1)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obs = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    targets = []
    for k in ("resources", "unclaimed_cells"):
        v = observation.get(k)
        if v:
            for p in v:
                if isinstance(p, (list, tuple)) and len(p) >= 2:
                    x, y = int(p[0]), int(p[1])
                    if inb(x, y) and (x, y) not in obs:
                        targets.append((x, y))
            if targets:
                break

    if not targets:
        return [0, 0]

    best = None
    best_d = 10**18
    for x, y in targets:
        d = (x - sx) * (x - sx) + (y - sy) * (y - sy)
        if d < best_d:
            best_d = d
            best = (x, y)

    tx, ty = best
    candidates = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = [0, 0]
    best_score = -10**18

    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        nd = (nx - tx) * (nx - tx) + (ny - ty) * (ny - ty)
        od = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
        score = -nd + 0.05 * od
        if score > best_score:
            best_score = score
            best_move = [int(dx), int(dy)]

    return best_move