def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", (0, 0)) or (0, 0)
    op = observation.get("opponent_position", (0, 0)) or (0, 0)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    resources = observation.get("resources", []) or []
    res = []
    for p in resources:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in blocked:
                res.append((x, y))
    if not res:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    # Decide on a resource to contest: prioritize winning access (my_dist < opp_dist),
    # then faster win, then proximity (tie-break via coordinates).
    best = None
    for r in res:
        tx, ty = r
        md = cheb(sx, sy, tx, ty)
        od = cheb(ox, oy, tx, ty)
        # bonus if I'm likely to arrive before opponent; penalize if opponent is closer
        win_flag = 0 if md < od else (1 if md == od else 2)
        # slight preference for resources that have nearer neighbors (density) to improve chain grabs
        dens = 0
        for rr in res:
            if rr != r:
                dens += 1 if cheb(tx, ty, rr[0], rr[1]) <= 2 else 0
        key = (win_flag, md, -dens, tx, ty)
        if best is None or key < best[0]:
            best = (key, tx, ty)
    _, tx, ty = best

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

    # If direct step hits obstacle, pick best alternative step (including stay).
    candidates = []
    for mx in (-1, 0, 1):
        for my in (-1, 0, 1):
            nx, ny = sx + mx, sy + my
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in blocked:
                # Favor moves that reduce distance to target and also don't approach opponent too much.
                candidates.append((cheb(nx, ny, tx, ty), cheb(nx, ny, ox, oy), mx, my))
    candidates.sort()
    return [candidates[0][2], candidates[0][3]]