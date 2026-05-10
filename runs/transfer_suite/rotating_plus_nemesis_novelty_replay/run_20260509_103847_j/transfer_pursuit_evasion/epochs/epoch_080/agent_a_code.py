def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or (0, 0)
    op = observation.get("opponent_position") or (0, 0)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for p in (observation.get("obstacles") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    role = str(observation.get("self_role") or "").lower()
    is_evader = ("evad" in role) or ("escap" in role) or ("run" in role)

    resources = []
    for r in (observation.get("resources") or []):
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in blocked:
                resources.append((x, y))

    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    if sx == ox and sy == oy:
        return [0, 0]

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    if resources:
        tx, ty = min(resources, key=lambda t: man(sx, sy, t[0], t[1]))
        has_res = True
    else:
        tx, ty = 0, 0
        has_res = False

    best = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        d_op = man(nx, ny, ox, oy)
        if has_res:
            d_t = man(nx, ny, tx, ty)
            score = (-10 * d_t) + (d_op if is_evader else -d_op)
        else:
            score = (d_op if is_evader else -d_op)
        key = (-score, dx, dy)
        if best is None or key < best[0]:
            best = (key, dx, dy)

    if best is None:
        for dx, dy in [(0,0),(1,0),(-1,0),(0,1),(0,-1),(1,1),(1,-1),(-1,1),(-1,-1)]:
            if ok(sx + dx, sy + dy):
                return [dx, dy]
        return [0, 0]

    return [best[1], best[2]]