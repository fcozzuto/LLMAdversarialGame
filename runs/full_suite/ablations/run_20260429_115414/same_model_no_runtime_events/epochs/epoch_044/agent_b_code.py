def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    rem = observation.get("remaining_resource_count", 0)
    try:
        rem = int(rem)
    except:
        rem = 0
    late = rem <= 4

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def man(ax, ay, bx, by):
        d = ax - bx
        if d < 0: d = -d
        e = ay - by
        if e < 0: e = -e
        return d + e

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    # Main target: nearest resource early, otherwise chase opponent (or still prefer resource if present)
    target_is_resource = bool(resources) and not late

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        if target_is_resource:
            dres = 10**9
            for rx, ry in resources:
                dd = man(nx, ny, rx, ry)
                if dd < dres:
                    dres = dd
            primary = dres
        else:
            primary = man(nx, ny, ox, oy)

        # Tie-break: keep distance from opponent if chasing, or approach opponent if protecting resource
        dop = man(nx, ny, ox, oy)
        if target_is_resource:
            # In resource mode, prefer making opponent farther
            secondary = -dop
        else:
            # In chase mode, prefer closer
            secondary = dop

        cand = (primary, secondary, nx, ny)
        if best is None or cand < best:
            best = cand

    if best is None:
        return [0, 0]
    # Recover movement from best position
    nx, ny = best[2], best[3]
    dx, dy = nx - sx, ny - sy
    if dx < -1: dx = -1
    if dx > 1: dx = 1
    if dy < -1: dy = -1
    if dy > 1: dy = 1
    return [int(dx), int(dy)]