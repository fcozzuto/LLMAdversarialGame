def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obst = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obst.add((int(p[0]), int(p[1])))

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    def res_info(rx, ry):
        ds = man(sx, sy, rx, ry)
        do = man(ox, oy, rx, ry)
        return (do - ds, ds, do, rx, ry)

    valid = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if inside(rx, ry):
                valid.append(res_info(rx, ry))

    if not valid:
        return [0, 0]

    # Strategic target:
    # 1) Prefer a "swing" where opponent is farther than us (ds <= do) and diff is large (defensive control).
    # 2) Otherwise, take the maximum swing (do - ds), tie by smallest our distance.
    win_take = [v for v in valid if v[1] <= v[2]]
    if win_take:
        v = max(win_take, key=lambda t: (t[0], -t[1]))
    else:
        v = max(valid, key=lambda t: (t[0], -t[1]))
    _, _, _, tx, ty = v

    best = (10**9, 10**9, 0, 0)
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not inside(nx, ny):
                continue
            ns = man(nx, ny, tx, ty)
            no = man(nx, ny, ox, oy)
            # Primary: get closer to target. Secondary: reduce opponent distance (denial pressure).
            cand = (ns, no, dx, dy)
            if cand < best:
                best = cand
    dx, dy = best[2], best[3]
    return [int(dx), int(dy)]