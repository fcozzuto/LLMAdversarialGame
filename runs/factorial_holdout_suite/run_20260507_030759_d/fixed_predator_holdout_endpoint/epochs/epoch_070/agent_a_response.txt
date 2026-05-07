def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obst = set()
    for p in (observation.get("obstacles") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obst.add((int(p[0]), int(p[1])))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    def dist(a, b, c, d):
        return abs(a - c) + abs(b - d)

    resources = observation.get("resources") or []
    targets = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if ok(rx, ry):
                ds = dist(sx, sy, rx, ry)
                do = dist(ox, oy, rx, ry)
                targets.append((rx, ry, ds, do))

    if not targets:
        return [0, 0]

    # Choose a "deny-worthy" target: prefer resources we can reach no later than opponent,
    # otherwise pick where we most reduce their lead.
    can_reach = [t for t in targets if t[2] <= t[3]]
    if can_reach:
        rx, ry, ds, do = min(can_reach, key=lambda t: (t[2], t[3], t[0], t[1]))
    else:
        rx, ry, ds, do = max(targets, key=lambda t: (t[3] - t[2], -t[2], t[0], t[1]))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        nds = dist(nx, ny, rx, ry)
        ndo = dist(nx, ny, rx, ry)  # self next distance; used for tie structure below
        od = dist(ox, oy, rx, ry)
        # Primary: minimize our distance to the target; Secondary: maximize opponent separation from it after move
        # (approx via current opponent distance; deterministic tie-breaks).
        key = (nds, -od, dx, dy)
        if best is None or key < best:
            best = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]