def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    opp_set = set()
    for p in observation.get("opponent_territory", []) or []:
        if p and len(p) >= 2:
            opp_set.add((int(p[0]), int(p[1])))

    # Primary targets: unclaimed/resources; fallback: opponent
    targets = []
    for key in ("resources", "unclaimed_cells"):
        for p in observation.get(key, []) or []:
            if p and len(p) >= 2:
                x, y = int(p[0]), int(p[1])
                if inb(x, y):
                    targets.append((x, y))
        if targets:
            break
    if not targets:
        targets = [(ox, oy)]

    # Choose a best target by distance with deterministic tie-breaks
    def man(a, b, c, d): return abs(a - c) + abs(b - d)
    targets.sort(key=lambda t: (man(sx, sy, t[0], t[1]), abs(t[0] - ox) + abs(t[1] - oy), t[0], t[1]))
    tx, ty = targets[0]

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        d_target = man(nx, ny, tx, ty)
        d_opp = man(nx, ny, ox, oy)

        # If move captures opponent territory, heavily prioritize it
        is_capture = (nx, ny) in opp_set
        capture_bonus = -100000 if is_capture else 0

        # Prefer expanding away from edges a bit to avoid getting pinned: use remaining neighbors count
        neigh = 0
        for ex in (-1, 0, 1):
            for ey in (-1, 0, 1):
                if ex == 0 and ey == 0:
                    continue
                xx, yy = nx + ex, ny + ey
                if inb(xx, yy):
                    neigh += 1

        # Score tuple: minimize
        score = (
            capture_bonus + d_target * 10 + d_opp,
            -neigh,
            abs(ny - ty),
            abs(nx - tx),
            dx, dy
        )
        if best is None or score < best[0]:
            best = (score, [dx, dy])

    if best is None:
        return [0, 0]
    return best[1]