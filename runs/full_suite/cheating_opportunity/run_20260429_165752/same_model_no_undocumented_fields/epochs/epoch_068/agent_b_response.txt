def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    s = observation.get("self_position") or [0, 0]
    o = observation.get("opponent_position") or [0, 0]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def free(x, y): return inb(x, y) and (x, y) not in obstacles
    def cd(x1, y1, x2, y2):
        a = x1 - x2
        if a < 0: a = -a
        b = y1 - y2
        if b < 0: b = -b
        return a if a > b else b

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not free(sx, sy):
        for dx, dy in moves:
            if free(sx + dx, sy + dy):
                return [dx, dy]
        return [0, 0]

    # Target selection: prefer resources where we are closer than opponent.
    best_r = None
    best_r_score = None
    for rx, ry in resources:
        du = cd(sx, sy, rx, ry)
        do_ = cd(ox, oy, rx, ry)
        rel = do_ - du  # positive means we have an advantage
        # Tie-break deterministically: closer to top-left, then by relative margin
        tie = -(rx + 2 * ry)
        sc = 1000 * rel + tie
        if best_r is None or sc > best_r_score:
            best_r, best_r_score = (rx, ry), sc
    if best_r is None:
        # No resources visible: move to increase distance from opponent while staying safe
        tx, ty = ox, oy
    else:
        tx, ty = best_r

    # Move choice: one-step lookahead toward target, while keeping away from opponent.
    best_m = (0, 0)
    best_ms = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        dcur = cd(sx, sy, tx, ty)
        dnext = cd(nx, ny, tx, ty)
        dopp_cur = cd(sx, sy, ox, oy)
        dnext_opp = cd(nx, ny, ox, oy)
        # Encourage capturing faster (reduce distance to target), discourage being too close to opponent.
        sc = 30 * (dcur - dnext) + 3 * dnext_opp - 0.2 * (abs(dx) + abs(dy))
        # Deterministic tie-break
        sc += -0.001 * (dx + 2 * dy)
        if best_ms is None or sc > best_ms:
            best_ms, best_m = sc, (dx, dy)
    return [int(best_m[0]), int(best_m[1])]