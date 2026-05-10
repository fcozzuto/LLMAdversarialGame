def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    xp, yp = map(int, observation.get("self_position") or [0, 0])
    xo, yo = map(int, observation.get("opponent_position") or [0, 0])

    def to_set(key):
        s = set()
        for p in observation.get(key) or []:
            if isinstance(p, (list, tuple)) and len(p) == 2:
                s.add((int(p[0]), int(p[1])))
        return s

    obstacles = to_set("obstacles")
    unclaimed = to_set("unclaimed_cells")
    myt = to_set("self_territory")
    opt = to_set("opponent_territory")

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    moves.remove((0, 0))

    # Frontier targets: unclaimed cells adjacent to our territory (edge-claim behavior)
    targets = set()
    for (x, y) in myt:
        for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)):
            nx, ny = x + dx, y + dy
            if (nx, ny) in unclaimed and inb(nx, ny):
                targets.add((nx, ny))
    if not targets:
        # Fall back: any reachable unclaimed
        targets = set()
        for (x, y) in unclaimed:
            if inb(x, y):
                targets.add((x, y))
    if not targets:
        return [0, 0]

    def manh(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    best = None
    # Deterministic tie-break prefers smaller (dx,dy) ordering
    ordered_moves = sorted(moves, key=lambda t: (t[0], t[1]))
    for dx, dy in ordered_moves + [(0, 0)]:
        nx, ny = xp + dx, yp + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) not in unclaimed and (nx, ny) not in myt and (nx, ny) not in opt:
            pass

        # Score: prioritize stepping into unclaimed/our territory; discourage opponent
        # Also prefer moves that head toward the best target (deterministic nearest)
        nearest = None
        nd = 10**9
        for tx, ty in targets:
            d = abs(tx - nx) + abs(ty - ny)
            if d < nd or (d == nd and (tx, ty) < nearest):
                nd = d
                nearest = (tx, ty)
        score = 0
        if (nx, ny) in unclaimed:
            score += 60
            score -= manh((nx, ny), nearest) * 2
        elif (nx, ny) in myt:
            score += 10
        elif (nx, ny) in opt:
            score -= 80  # flipping allows loss of tempo; avoid if possible

        # Avoid giving the opponent a shorter path to the same region
        my_to = manh((nx, ny), nearest)
        op_to = manh((xo, yo), nearest)
        score += (op_to - my_to) * 3

        # Slight center bias to stabilize
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        score -= (abs(nx - cx) + abs(ny - cy)) * 0.1

        if best is None or score > best[0] or (score == best[0] and (dx, dy) < (best[1], best[2])):
            best = (score, dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[1]), int(best[2])]