def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    role = str(observation.get("self_role") or "").lower()
    i_am_evader = ("evader" in role) or ("escape" in role) or ("evade" in role) or ("runner" in role)

    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    dirs8 = [(1,0),(-1,0),(0,1),(0,-1),(1,1),(1,-1),(-1,1),(-1,-1)]

    def mobility(x, y):
        m = 0
        for dx, dy in dirs8:
            nx, ny = x + dx, y + dy
            if ok(nx, ny):
                m += 1
        return m

    best = None
    bestv = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        d = abs(ox - nx) + abs(oy - ny)
        # If roles swapped, the objective flips.
        mob = mobility(nx, ny)

        # Wall-run prevention / corridor awareness: favor positions with more options.
        # Pursuer tries to reduce distance and opponent space; evader tries opposite.
        if i_am_evader:
            # maximize distance, then maximize mobility
            v = d * 10 + mob
        else:
            # minimize distance, then minimize mobility (deny space)
            v = (-d) * 10 + (-mob)

        if bestv is None or v > bestv:
            bestv = v
            best = (dx, dy)

    if best is None:
        return [0, 0]

    # Tie-break: if best doesn't obviously move toward/away, keep diagonal when safe
    bx, by = best
    if bx == 0 and by == 0:
        # try a deterministic slight improvement
        for dx, dy in [(-1,-1),(1,-1),(-1,1),(1,1)]:
            nx, ny = sx + dx, sy + dy
            if ok(nx, ny):
                return [dx, dy]
        return [0, 0]
    return [int(bx), int(by)]