def choose_move(observation):
    W = int(observation.get("grid_width", 8) or 8)
    H = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or (0, 0)
    op = observation.get("opponent_position") or (0, 0)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obs = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H:
                obs.add((x, y))

    def inb(x, y):
        return 0 <= x < W and 0 <= y < H and (x, y) not in obs

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                resources.append((x, y))

    if not resources:
        tx, ty = (W - 1) // 2, (H - 1) // 2
        if not inb(tx, ty):
            tx, ty = 0, 0
        resources = [(tx, ty)]

    def man(ax, ay, bx, by):
        dx = ax - bx
        dy = ay - by
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx + dy

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_val = -10**18

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        local = -10**18
        for rx, ry in resources:
            ds = man(nx, ny, rx, ry)
            do = man(ox, oy, rx, ry)
            # Favor resources we can reach sooner than opponent; slight pull to nearer ones.
            v = (do - ds) * 10 - ds
            if v > local:
                local = v
        # Deterministic tie-break: prefer moves that reduce own distance to the best resource (then lexicographic).
        if local > best_val:
            best_val = local
            best_move = (dx, dy)
        elif local == best_val:
            def lex_key(m):
                mx, my = m
                ds0 = man(sx + mx, sy + my, resources[0][0], resources[0][1])
                return (ds0, mx, my)
            if lex_key((dx, dy)) < lex_key(best_move):
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]