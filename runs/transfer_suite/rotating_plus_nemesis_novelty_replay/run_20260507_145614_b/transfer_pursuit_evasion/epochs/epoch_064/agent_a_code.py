def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or (0, 0)
    op = observation.get("opponent_position") or (0, 0)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obst = set()
    for p in (observation.get("obstacles") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    resources = observation.get("resources") or []
    best_t = None
    best_val = None
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            tx, ty = int(r[0]), int(r[1])
            if not (0 <= tx < w and 0 <= ty < h) or (tx, ty) in obst:
                continue
            ds = (sx - tx) * (sx - tx) + (sy - ty) * (sy - ty)
            do = (ox - tx) * (ox - tx) + (oy - ty) * (oy - ty)
            # Prefer resources closer to us; tie-break against opponent
            val = (ds - do, ds, tx, ty)
            if best_val is None or val < best_val:
                best_val = val
                best_t = (tx, ty)

    if best_t is None:
        best_t = (ox, oy)

    tx, ty = best_t
    best_move = (0, 0)
    best_d = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d = (nx - tx) * (nx - tx) + (ny - ty) * (ny - ty)
        cand = (d, abs(dx) + abs(dy), dx, dy)
        if best_d is None or cand < best_d:
            best_d = cand
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]