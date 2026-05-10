def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", (0, 0)) or (0, 0)
    op = observation.get("opponent_position", (0, 0)) or (0, 0)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                obs.add((x, y))

    resources = observation.get("resources", []) or []
    res = []
    for p in resources:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y) and (x, y) not in obs:
                res.append((x, y))
    if not res:
        return [0, 0]

    def cheb(a, b):
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # Score target by: (opponent_time - my_time), prefer I can reach earlier; then prefer higher margin; then nearer
    best = None
    best_key = None
    for r in res:
        st = cheb((sx, sy), r)
        ot = cheb((ox, oy), r)
        # If I can arrive earlier or same, prioritize; otherwise still consider but down-rank.
        key = (-(0 if st <= ot else 1000),  # ensure st<=ot comes first
               -(ot - st),                # larger advantage first
               st,                         # nearer first
               r[0], r[1])               # deterministic tie-break
        if best_key is None or key < best_key:
            best_key = key
            best = r

    tx, ty = best[0], best[1]

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]
    # Deterministically choose the move that maximizes (my improvement minus opponent improvement), while avoiding obstacles
    bestm = [0, 0]
    bestmk = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        myd = cheb((nx, ny), (tx, ty))
        opd = cheb((nx, ny), (ox, oy))  # small deterrent: avoid stepping toward opponent too aggressively
        cur_my = cheb((sx, sy), (tx, ty))
        cur_opd = cheb((sx, sy), (ox, oy))
        improve = cur_my - myd
        opp_push = cur_opd - opd
        mk = (-improve, -(opp_push), dx, dy)  # prefer larger improve/opp_push; deterministic tie
        if bestmk is None or mk < bestmk:
            bestmk = mk
            bestm = [dx, dy]

    return [int(bestm[0]), int(bestm[1])]