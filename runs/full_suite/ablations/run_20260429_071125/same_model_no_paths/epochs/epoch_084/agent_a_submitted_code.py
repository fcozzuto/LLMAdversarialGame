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

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in blocked:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    resources.sort()
    best = None
    best_key = None
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # Prefer resources where we are closer; then higher opponent advantage; then nearer to us; deterministic tie-break.
        key = (ds > do, do - ds, -ds, -ry, -rx)
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best
    dx = 0
    if tx > sx: dx = 1
    elif tx < sx: dx = -1
    dy = 0
    if ty > sy: dy = 1
    elif ty < sy: dy = -1

    moves = []
    target_move = (dx, dy)
    for mx in (-1, 0, 1):
        for my in (-1, 0, 1):
            if mx == 0 and my == 0:
                continue
            moves.append((mx, my))
    # Order: prefer direct toward target, then by resulting distance to target, then deterministic.
    ordered = []
    for m in moves:
        if m == target_move:
            ordered.append(m)
        else:
            ordered.append(m)
    # Build unique order deterministically: try 8 dirs, then stay.
    cand = []
    seen = set()
    for m in ordered:
        if m not in seen:
            seen.add(m)
            cand.append(m)
    cand.append((0, 0))

    def step_score(m):
        nx, ny = sx + m[0], sy + m[1]
        if not ok(nx, ny):
            return None
        return -cheb(nx, ny, tx, ty), -(m[0] != target_move[0] or m[1] != target_move[1]), -m[0], -m[1]

    best_m = None
    best_s = None
    for m in cand:
        s = step_score(m)
        if s is None:
            continue
        if best_s is None or s > best_s:
            best_s = s
            best_m = m

    if best_m is None:
        return [0, 0]
    return [int(best_m[0]), int(best_m[1])]