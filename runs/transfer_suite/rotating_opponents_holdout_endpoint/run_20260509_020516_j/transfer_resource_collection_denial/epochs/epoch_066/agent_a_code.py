def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def md(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    opp_corner = 0
    # tie-break prefers resources more "toward opponent corner" than ours corner
    # ours start assumed opposite corners; use current opponent position as proxy.
    best = None
    best_key = None
    for rx, ry in resources:
        ds = md(sx, sy, rx, ry)
        do = md(ox, oy, rx, ry)
        lead = do - ds  # positive means we are closer
        # closer race: maximize lead; if tie, smaller ds; if tie, smaller distance for opponent (we want deny); then deterministic by coords
        corner_bias = md(rx, ry, ox, oy)  # smaller means closer to opponent
        key = (lead, -ds, -do, -corner_bias, -rx, -ry)
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best

    dx = 0
    if tx > sx:
        dx = 1
    elif tx < sx:
        dx = -1
    dy = 0
    if ty > sy:
        dy = 1
    elif ty < sy:
        dy = -1

    # small obstacle-aware fallback: try axis/diagonal alternatives that reduce distance
    cands = []
    for ndx in (-1, 0, 1):
        for ndy in (-1, 0, 1):
            if ndx == 0 and ndy == 0:
                cands.append((0, 0))
            nx, ny = sx + ndx, sy + ndy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                cands.append((ndx, ndy))
    # remove duplicates while keeping order
    seen = set()
    uniq = []
    for a in cands:
        if a not in seen:
            seen.add(a)
            uniq.append(a)

    # deterministic select: prefer moves that minimize md to target; then maximize lead (closer than opponent after move); then coords
    best_m = None
    best_k = None
    for ndx, ndy in uniq:
        nx, ny = sx + ndx, sy + ndy
        ds2 = md(nx, ny, tx, ty)
        do2 = md(ox, oy, tx, ty)
        lead2 = do2 - ds2
        k = (-ds2, -lead2, -abs(nx - tx), -abs(ny - ty), -nx, -ny)
        if best_k is None or k > best_k:
            best_k = k
            best_m = (ndx, ndy)

    return [int(best_m[0]), int(best_m[1])]