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

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, dict):
            rx = r.get("x", r.get("pos", [None, None])[0])
            ry = r.get("y", r.get("pos", [None, None])[1])
            if rx is not None and ry is not None:
                resources.append((int(rx), int(ry)))
        elif isinstance(r, (list, tuple)) and len(r) >= 2:
            resources.append((int(r[0]), int(r[1])))

    if resources:
        best = None
        bestd = None
        for (tx, ty) in resources:
            if not ok(tx, ty):
                continue
            d = max(abs(tx - sx), abs(ty - sy))
            if best is None or d < bestd or (d == bestd and (tx, ty) < best):
                best = (tx, ty)
                bestd = d
        if best is not None:
            tx, ty = best
            bestmove = None
            bestkey = None
            for dx, dy in dirs:
                nx, ny = sx + dx, sy + dy
                if not ok(nx, ny):
                    continue
                nd = max(abs(tx - nx), abs(ty - ny))
                key = (nd, abs(dx) + abs(dy), dx, dy)
                if bestkey is None or key < bestkey:
                    bestkey = key
                    bestmove = [dx, dy]
            return bestmove if bestmove is not None else [0, 0]

    opp_best = None
    opp_key = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        d = max(abs(ox - nx), abs(oy - ny))
        key = (-d, abs(dx) + abs(dy), dx, dy)
        if opp_key is None or key < opp_key:
            opp_key = key
            opp_best = [dx, dy]
    return opp_best if opp_best is not None else [0, 0]