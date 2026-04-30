def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])
    ti = int(observation.get("turn_index", 0) or 0)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    resources = []
    for r in observation.get("resources", []) or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if inside(x, y):
                resources.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # Candidate moves
    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    # If no resources, reposition to a stable midpoint lane and avoid opponent by biasing away.
    if not resources:
        best = None
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not inside(nx, ny):
                continue
            d_center = cheb(nx, ny, cx, cy)
            d_opp = cheb(nx, ny, ox, oy)
            # alternate tiny bias to prevent getting stuck
            lane = (nx + ny + ti) % 2
            key = (d_center, -d_opp, lane)
            if best is None or key < best[0]:
                best = (key, [dx, dy])
        return best[1] if best else [0, 0]

    # Score targets: prioritize resources where we can beat opponent (d_opp - d_me large).
    # Then, tie-break by making that resource close after moving.
    best_move = None
    best_key = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue

        # Evaluate best target from this candidate position.
        best_target_key = None
        best_target = None
        for rx, ry in resources:
            d_me = cheb(nx, ny, rx, ry)
            d_op = cheb(ox, oy, rx, ry)
            tempo = d_op - d_me  # want positive
            # Slight center preference and mild "anti-follow": discourage moving directly onto opponent.
            key = (-tempo, d_me, cheb(nx, ny, cx, cy), cheb(nx, ny, ox, oy), (rx + ry) % 2)
            if best_target_key is None or key < best_target_key:
                best_target_key = key
                best_target = (rx, ry)

        rx, ry = best_target
        # Final move evaluation also considers not letting opponent get nearer to the same target.
        d_me_now = cheb(nx, ny, rx, ry)
        d_op_now = cheb(ox, oy, rx, ry)
        avoid_same = cheb(nx, ny, ox, oy)
        final_key = (-(d_op_now - d_me_now), d_me_now, avoid_same, cheb(nx, ny, cx, cy), (rx * 31 + ry * 17) %