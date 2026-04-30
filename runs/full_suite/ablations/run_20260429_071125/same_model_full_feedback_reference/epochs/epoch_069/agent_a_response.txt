def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in (observation.get("resources") or []):
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    # If no resources, head to center to reduce distance to future spawns.
    if not resources:
        tx, ty = w // 2, h // 2
        best = None
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            score = cheb(nx, ny, tx, ty)
            if best is None or score < best[0]:
                best = (score, dx, dy)
        return [best[1], best[2]] if best else [0, 0]

    # Choose best move by maximizing expected control of a contested resource.
    best = None
    for mdx, mdy in dirs:
        nx, ny = sx + mdx, sy + mdy
        if not ok(nx, ny):
            continue
        my_best = -10**9
        for rx, ry in resources:
            our_d = cheb(nx, ny, rx, ry)
            opp_d = cheb(ox, oy, rx, ry)
            contested = our_d <= opp_d
            # Prefer immediate pickup (our_d==0), and prefer being closer than opponent.
            # Small tie-break by resource position for determinism.
            closer = (opp_d - our_d)
            val = (100 if our_d == 0 else 0) + (50 if contested else -5)
            val += closer * 3
            val -= cheb(nx, ny, rx, ry)  # slightly tighten
            val += -(rx * 0.01 + ry * 0.001)
            if val > my_best:
                my_best = val
        # Also include a mild "safety" term to avoid stepping into tight corners:
        safety = -((cheb(nx, ny, ox, oy)) == 0)  # only 0 if already on opponent, unlikely
        total = my_best + safety
        if best is None or total > best[0]:
            best = (total, mdx, mdy)
    return [best[1], best[2]] if best else [0, 0]