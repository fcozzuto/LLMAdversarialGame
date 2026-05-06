def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = observation.get("obstacles") or []
    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            blocked.add((p[0], p[1]))

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1,  0), (0, 0), (1, 0),
             (-1,  1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny):
            legal.append((dx, dy))
    if not legal:
        return [0, 0]

    res_list = observation.get("resources") or []
    resources = []
    for r in res_list:
        if isinstance(r, (list, tuple)) and len(r) == 2:
            resources.append((r[0], r[1]))
    if not resources:
        return [0, 0]

    def man(x1, y1, x2, y2):
        a = x1 - x2
        if a < 0:
            a = -a
        b = y1 - y2
        if b < 0:
            b = -b
        return a + b

    best_move = None
    best_key = None
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        # Choose the resource that maximizes "I should be closer than opponent"
        # value ~ how much farther opponent is vs me, then my distance.
        best_margin = None
        best_myd = None
        best_oppd = None
        for rx, ry in resources:
            myd = man(nx, ny, rx, ry)
            oppd = man(ox, oy, rx, ry)
            margin = oppd - myd
            if best_margin is None or (margin, -myd, -oppd) > (best_margin, -best_myd, -best_oppd):
                best_margin, best_myd, best_oppd = margin, myd, oppd

        # If margin is positive, prioritize that; otherwise just minimize my distance.
        if best_margin is not None and best_margin > 0:
            key = (0, -best_margin, best_myd)
        else:
            # fallback: closest resource (deterministic tie-break)
            md = None
            for rx, ry in resources:
                myd = man(nx, ny, rx, ry)
                if md is None or myd < md:
                    md = myd
            key = (1, md, dx, dy)

        # Deterministic ordering
        if best_key is None or key < best_key:
            best_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]