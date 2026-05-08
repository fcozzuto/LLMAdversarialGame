def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    srole = (observation.get("self_role") or "").lower()
    orole = (observation.get("opponent_role") or "").lower()
    self_is_pursuer = ("purs" in srole) and ("evad" not in srole)
    if ("purs" not in srole) and ("purs" in orole):
        self_is_pursuer = False

    obs = set()
    for p in observation.get("obstacles") or []:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def man(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx + dy

    def free_neighbors(x, y):
        c = 0
        for mx, my in moves:
            nx, ny = x + mx, y + my
            if inb(nx, ny):
                c += 1
        return c

    best = (None, None, None)  # (score, dist, tie)
    for mx, my in moves:
        nx, ny = sx + mx, sy + my
        if not inb(nx, ny):
            continue
        d = man(nx, ny, ox, oy)
        fn = free_neighbors(nx, ny)
        # Deterministic tie-breaking: prefer (0,0) then -x/-y order via index
        idx = moves.index((mx, my))
        if self_is_pursuer:
            # minimize distance; slightly prefer higher mobility
            score = d * 1000 - fn * 5
        else:
            # maximize distance; also avoid low mobility
            score = (-d) * 1000 + fn * 3
        if best[0] is None or score < best[0] or (score == best[0] and (d < best[1] if self_is_pursuer else d > best[1])) or (score == best[0] and d == best[1] and idx < best[2]):
            best = (score, d, idx)

    if best[0] is None:
        return [0, 0]
    # Recover move from tie index
    chosen_idx = best[2]
    mx, my = moves[chosen_idx]
    return [int(mx), int(my)]