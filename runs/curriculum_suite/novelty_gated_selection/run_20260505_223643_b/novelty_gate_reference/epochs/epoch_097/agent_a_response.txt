def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def md(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    moves = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1), (0, 0)]

    lead = []
    best_margin = -10**9
    best_margin_res = None
    for (rx, ry) in resources:
        sd = md(sx, sy, rx, ry)
        od = md(ox, oy, rx, ry)
        margin = od - sd
        if margin >= 2:
            lead.append((sd, rx, ry))
        if margin > best_margin or (margin == best_margin and (best_margin_res is None or sd < md(sx, sy, best_margin_res[0], best_margin_res[1]))):
            best_margin = margin
            best_margin_res = (rx, ry)

    if lead:
        lead.sort()
        tx, ty = lead[0][1], lead[0][2]
    else:
        tx, ty = best_margin_res

    best = None
    best_step = [0, 0]
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        nsd = md(nx, ny, tx, ty)
        nod = md(nx, ny, ox, oy)  # keep away from opponent when close to target
        val = (-nsd, nod)  # lexicographic: minimize distance to target, then maximize spacing from opponent
        if best is None or val > best:
            best = val
            best_step = [dx, dy]

    return best_step