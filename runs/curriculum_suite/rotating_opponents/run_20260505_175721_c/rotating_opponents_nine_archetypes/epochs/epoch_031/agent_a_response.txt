def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", (0, 0)) or (0, 0)
    op = observation.get("opponent_position", (0, 0)) or (0, 0)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def dist(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    def clamp_step(a, b):
        if b > a:
            return 1
        if b < a:
            return -1
        return 0

    cx, cy = (w - 1) // 2, (h - 1) // 2

    # Choose resource where we beat opponent's arrival time most.
    if resources:
        best = None
        best_key = None
        for rx, ry in resources:
            myd = dist(sx, sy, rx, ry)
            opd = dist(ox, oy, rx, ry)
            # Prefer: we are closer; then also prefer closer overall (faster secure).
            key = (opd - myd, -myd)
            if best_key is None or key > best_key:
                best_key = key
                best = (rx, ry)
        # If opponent is significantly closer everywhere, head toward center to contest lanes.
        if best_key[0] < 0:
            target = (cx, cy)
        else:
            target = best
    else:
        target = (cx, cy)

    tx, ty = target
    dx, dy = clamp_step(sx, tx), clamp_step(sy, ty)

    nx, ny = sx + dx, sy + dy
    if (nx, ny) in obstacles:
        # Try axis-aligned alternatives deterministically.
        options = [(dx, 0), (0, dy), (0, 0)]
        for adx, ady in options:
            ax, ay = sx + adx, sy + ady
            if 0 <= ax < w and 0 <= ay < h and (ax, ay) not in obstacles:
                return [int(adx), int(ady)]
        return [0, 0]
    return [int(dx), int(dy)]