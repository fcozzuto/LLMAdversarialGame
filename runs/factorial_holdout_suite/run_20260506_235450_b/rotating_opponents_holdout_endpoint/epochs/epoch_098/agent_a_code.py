def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    ap = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(ap[0]), int(ap[1])

    blocked = set()
    for ob in observation.get("obstacles") or []:
        if isinstance(ob, (list, tuple)) and len(ob) >= 2:
            x, y = int(ob[0]), int(ob[1])
        elif isinstance(ob, dict):
            if "x" in ob and "y" in ob:
                x, y = int(ob["x"]), int(ob["y"])
            else:
                p = ob.get("position")
                if not (isinstance(p, (list, tuple)) and len(p) >= 2):
                    continue
                x, y = int(p[0]), int(p[1])
        else:
            continue
        if 0 <= x < w and 0 <= y < h:
            blocked.add((x, y))

    resources = observation.get("resources") or []
    if not resources:
        return [0, 0]

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    my = (sx, sy)
    op = (ox, oy)
    targets = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            tx, ty = int(r[0]), int(r[1])
        elif isinstance(r, dict) and "x" in r and "y" in r:
            tx, ty = int(r["x"]), int(r["y"])
        else:
            continue
        t = (tx, ty)
        my_d = man(my, t)
        op_d = man(op, t)
        # Prefer resources where we are (or get) closer than opponent
        key = (my_d - op_d, my_d)
        targets.append((key, t))
    if not targets:
        return [0, 0]
    _, target = min(targets, key=lambda z: z[0])
    tx, ty = target

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    best_m = (0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in blocked:
            continue
        my_d = abs(nx - tx) + abs(ny - ty)
        op_d = abs(ox - tx) + abs(oy - ty)
        # minimize distance to target; then try to push opponent farther relative to us
        score = (my_d, -(op_d - my_d))
        if best is None or score < best:
            best = score
            best_m = (dx, dy)

    return [int(best_m[0]), int(best_m[1])]