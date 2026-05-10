def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)

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
    obstacles = list(blocked)

    role = str(observation.get("self_role") or "").lower()
    evader = ("evader" in role) or ("escape" in role) or ("runner" in role)
    pursuer = ("pursuer" in role) or ("chaser" in role) or ("hunter" in role) or (not evader)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def dist2(ax, ay, bx, by):
        dx, dy = ax - bx, ay - by
        return dx * dx + dy * dy

    def free(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in blocked

    def obs_pen(nx, ny):
        if not obstacles:
            return 0
        md = 10**9
        for x, y in obstacles:
            dd = dist2(nx, ny, x, y)
            if dd < md:
                md = dd
        # Stronger penalty near obstacles (still deterministic).
        if md <= 1:
            return 2000
        if md <= 4:
            return 400
        if md <= 9:
            return 120
        if md <= 16:
            return 50
        return 10

    best = None
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue

        d_opp = dist2(nx, ny, ox, oy)
        # Edge bias for evasion (more room), slight for pursuit (reduce escape).
        edge = min(nx, ny, w - 1 - nx, h - 1 - ny)
        edge_bias = edge * (3 if evader else 1)

        # When roles are unclear, still chase/evade based on role.
        if evader:
            score = d_opp * 12 + edge_bias - obs_pen(nx, ny)
        else:
            score = (-d_opp) * 12 + edge_bias - obs_pen(nx, ny)

        # Tie-break deterministically: prefer lower dx, then lower dy, then staying still.
        key = (-(score), abs(dx) + abs(dy), dx, dy)  # smaller is better
        if best is None or key < best:
            best = key
            best_score = score

    if best is None:
        return [0, 0]

    # Recover move from tie-break key by re-scanning to keep deterministic.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        d_opp = dist2(nx, ny, ox, oy)
        edge = min(nx, ny, w - 1 - nx, h - 1 - ny)
        edge_bias = edge * (3 if evader else 1)
        if evader:
            score = d_opp * 12 + edge_bias - obs_pen(nx, ny)
        else:
            score = (-d_opp) * 12 + edge_bias - obs_pen(nx, ny)
        key = (-(score), abs(dx) + abs(dy), dx, dy)
        if best == key:
            return [dx, dy]
    return [0, 0]