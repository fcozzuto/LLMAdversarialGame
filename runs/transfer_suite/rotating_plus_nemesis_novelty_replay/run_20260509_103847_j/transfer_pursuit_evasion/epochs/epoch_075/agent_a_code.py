def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    resources = observation.get("resources") or []
    res_pos = []
    for p in resources:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in blocked:
                res_pos.append((x, y))
    if not res_pos:
        res_pos = [(ox, oy)]

    dirs = [(0, 0), (1, 0), (0, 1), (-1, 0), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]

    def legal(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in blocked

    best = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        tx, ty = min(res_pos, key=lambda r: (r[0] - nx) * (r[0] - nx) + (r[1] - ny) * (r[1] - ny))
        d = (tx - nx) * (tx - nx) + (ty - ny) * (ty - ny)
        away_from_opp = (ox - nx) * (ox - nx) + (oy - ny) * (oy - ny)
        cand = (d, -away_from_opp, dx, dy)
        if best is None or cand < best:
            best = cand

    if best is None:
        return [0, 0]
    return [int(best[2]), int(best[3])]