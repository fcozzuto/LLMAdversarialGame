def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", None) or []:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", None) or []:
        if r is not None and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        return [0, 0]

    opp_to = {}
    for r in resources:
        opp_to[r] = man((ox, oy), r)

    # Evaluate each immediate move by the best resource we can beat/contest,
    # plus a small term that discourages getting closer to opponent.
    best = None
    best_sc = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        my_pos = (nx, ny)

        my_score = -10**18
        for r in resources:
            md = man(my_pos, r)
            od = opp_to[r]
            # If we can arrive no later, prefer it; otherwise prefer denying by being close.
            if md <= od:
                sc = (od - md) * 6 + (20 - md) + (1 if r[0] in (0, w - 1) or r[1] in (0, h - 1) else 0)
            else:
                sc = (od - md) * 2 + (12 - md)  # negative if we fall behind, but still guide toward contested cells
            if sc > my_score:
                my_score = sc

        # Tension term: avoid walking into opponent's path too aggressively.
        tension = -man(my_pos, (ox, oy)) * 0.15
        sc_total = my_score + tension

        if sc_total > best_sc:
            best_sc = sc_total
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return best