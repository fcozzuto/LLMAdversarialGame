def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def man(a, b, c, d):
        dx = a - c
        if dx < 0:
            dx = -dx
        dy = b - d
        if dy < 0:
            dy = -dy
        return dx + dy

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    # Resource denial: pick a resource opponent is closer to; otherwise pick the nearest to self.
    best = None
    for rx, ry in resources:
        ds = man(sx, sy, rx, ry)
        do = man(ox, oy, rx, ry)
        if do < ds:  # deny if opponent is nearer
            key = (do - ds, ds, rx, ry)
            if best is None or key < best[0]:
                best = (key, (rx, ry))
    if best is None:
        for rx, ry in resources:
            ds = man(sx, sy, rx, ry)
            key = (ds, rx, ry)
            if best is None or key < best[0]:
                best = (key, (rx, ry))

    if best is None:
        return [0, 0]
    tx, ty = best[1]

    # Prefer a move that reduces distance to target, with a small bias to avoid approaching opponent too closely.
    best_move = (10**9, 0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        dist_t = man(nx, ny, tx, ty)
        dist_o = man(nx, ny, ox, oy)
        # When denying, don't step onto opponent-preferred zones; keep space proportional to target competition.
        ds_cur = man(sx, sy, tx, ty)
        do_cur = man(ox, oy, tx, ty)
        bias = 0 if do_cur >= ds_cur else -3
        score = dist_t * 100 + (-dist_o) * (1 if bias == 0 else 2)
        score += (0 if (nx, ny) == (sx, sy) else 0)
        if score < best_move[0]:
            best_move = (score, dx, dy)

    _, dx, dy = best_move
    return [int(dx), int(dy)]