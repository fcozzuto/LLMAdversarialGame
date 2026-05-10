def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def man(ax, ay, bx, by):
        d = ax - bx
        if d < 0: d = -d
        e = ay - by
        if e < 0: e = -e
        return d + e

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if not resources:
        tx, ty = w // 2, h // 2
        best = [0, 0]
        best_d = 10**9
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                nx, ny = sx + dx, sy + dy
                if not inb(nx, ny) and not (nx == sx and ny == sy):
                    continue
                d = man(nx, ny, tx, ty)
                if d < best_d or (d == best_d and (dx, dy) < (best[0], best[1])):
                    best_d, best = d, [dx, dy]
        return best

    # Pick target we can reach first; break ties by alignment with opponent.
    best_r = None
    best_key = None
    for rx, ry in resources:
        sd = man(sx, sy, rx, ry)
        od = man(ox, oy, rx, ry)
        contest = od - sd  # positive => we are closer
        align = 0
        if ry == oy: align += 4
        if rx == ox: align += 1
        # small bias away from corners to reduce predictable stalling
        corner_pen = 0
        if (rx in (0, w - 1)) and (ry in (0, h - 1)): corner_pen = 1
        # Prefer larger contest; then smaller sd; then stable deterministic tie-break.
        key = (-(contest + align - corner_pen), sd, rx * 16 + ry)
        if best_key is None or key < best_key:
            best_key, best_r = key, (rx, ry)

    tx, ty = best_r

    # Move one step to minimize distance to target; avoid obstacles deterministically.
    deltas = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) or (nx == sx and ny == sy):
                deltas.append((dx, dy))
    # Deterministic ordering for tie-break
    deltas.sort()

    best_move = (0, 0)
    best_score = 10**9
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        d_to = man(nx, ny, tx, ty)
        # discourage stepping into positions where opponent would become much closer to target
        d_opp = man(ox, oy, tx, ty) - man(ox, oy, nx, ny)
        # prefer slight progress toward target even if already close
        score = d_to * 10 + (-d_opp) + (1 if (nx, ny) in obstacles else 0)
        if score < best_score:
            best_score, best_move = score, (dx, dy)

    return [int(best_move[0]), int(best_move[1])]