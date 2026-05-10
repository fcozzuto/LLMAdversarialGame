def choose_move(observation):
    ax, ay = observation["self_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    obstacles = observation.get("obstacles") or []
    obs = set((x, y) for x, y in obstacles if inb(x, y))
    unclaimed = observation.get("unclaimed_cells") or []
    my_t = observation.get("self_territory") or []
    op_t = observation.get("opponent_territory") or []
    my_set = set((x, y) for x, y in my_t if inb(x, y))
    op_set = set((x, y) for x, y in op_t if inb(x, y))
    un_set = set((x, y) for x, y in unclaimed if inb(x, y))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def md(p, q): return abs(p[0]-q[0]) + abs(p[1]-q[1])

    # Use a small deterministic sample of targets to guide expansion.
    targets = list(un_set)[:25]
    if not targets:
        targets = list(op_set)[:25]
    if not targets:
        targets = [(ax, ay)]

    best = None
    bestv = None
    for dx, dy in moves:
        nx, ny = ax + dx, ay + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            nx, ny = ax, ay
            dx, dy = 0, 0
        score = 0
        if (nx, ny) in un_set:
            score += 10
        elif (nx, ny) in op_set:
            score += 7
        elif (nx, ny) in my_set:
            score += 2
        else:
            score += 0

        dmin = 10**9
        for t in targets:
            d = md((nx, ny), t)
            if d < dmin:
                dmin = d
        score += max(0, 6 - dmin)

        # Prefer moving (not just staying) if tied.
        score += 0 if (dx == 0 and dy == 0) else 1

        # Deterministic tie-breaking by move order.
        key = (score, -dx, -dy)
        if bestv is None or key > bestv:
            bestv = key
            best = [dx, dy]
    return best if best is not None else [0, 0]