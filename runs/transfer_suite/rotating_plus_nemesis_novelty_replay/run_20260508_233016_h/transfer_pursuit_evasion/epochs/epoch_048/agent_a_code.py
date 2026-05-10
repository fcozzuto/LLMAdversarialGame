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

    role = str(observation.get("self_role") or "").lower()
    wants_avoid = any(k in role for k in ("evader", "flee", "escape")) or (role == "")

    resources = observation.get("resources") or []
    res_list = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in blocked:
                res_list.append((x, y))
    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def best_toward(tx, ty, avoid=False):
        best = None
        bestv = None
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            d = abs(nx - tx) + abs(ny - ty)
            v = d if avoid else -d
            if bestv is None or v > bestv or (v == bestv and (dx, dy) < best):
                bestv = v
                best = (dx, dy)
        return best if best is not None else (0, 0)

    if res_list:
        best_res = None
        best_d = None
        for x, y in res_list:
            d = abs(x - sx) + abs(y - sy)
            if best_d is None or d < best_d or (d == best_d and (x, y) < best_res):
                best_d = d
                best_res = (x, y)
        return list(best_toward(best_res[0], best_res[1], avoid=False))

    if wants_avoid:
        mv = best_toward(ox, oy, avoid=True)
    else:
        mv = best_toward(ox, oy, avoid=False)
    return [int(mv[0]), int(mv[1])]