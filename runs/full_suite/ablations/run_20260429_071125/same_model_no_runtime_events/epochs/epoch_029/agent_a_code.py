def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    res = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            res.append((x, y))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if res:
        nearest = min(res, key=lambda t: abs(t[0] - sx) + abs(t[1] - sy))
    else:
        nearest = (sx, sy)

    best = None
    best_sc = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d_res = abs(nearest[0] - nx) + abs(nearest[1] - ny)
        d_opp = abs(ox - nx) + abs(oy - ny)
        on_res = 1 if (nx, ny) in res else 0
        sc = on_res * 10000 - d_res * 10 + d_opp
        if sc > best_sc or (sc == best_sc and best is None):
            best_sc = sc
            best = [dx, dy]

    if best is not None:
        return best
    return [0, 0]