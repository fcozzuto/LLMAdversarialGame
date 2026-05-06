def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

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

    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def d2(ax, ay, bx, by):
        dx = ax - bx
        dy = ay - by
        return dx * dx + dy * dy

    if not resources:
        tx, ty = w // 2, h // 2
        best = (0, 0)
        bestv = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            v = d2(nx, ny, tx, ty)
            if bestv is None or v < bestv:
                bestv, best = v, (dx, dy)
        return [best[0], best[1]]

    # Resource-denial: move toward resources the opponent is likely to take first,
    # but where we can reduce the gap or at least move into contention.
    cx, cy = w // 2, h // 2
    opp_pref = [(d2(ox, oy, rx, ry), rx, ry) for rx, ry in resources]
    # Deterministic: tie-break by coordinates.
    opp_pref.sort(key=lambda t: (t[0], t[1], t[2]))
    # Focus on top K opponent-accessible resources.
    K = 4 if len(opp_pref) >= 4 else len(opp_pref)
    cand = opp_pref[:K]

    best_move = (0, 0)
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        # Prefer moves that maximize how much we close the opponent's advantage at contested resources.
        val = 0
        for od, rx, ry in cand:
            sd = d2(nx, ny, rx, ry)
            gap = od - sd  # positive means we are closer (good for denial)
            # Also slightly prefer resources closer overall and moves toward center.
            val += gap * 100 - sd - 2 * d2(nx, ny, cx, cy)
        # Mild keep-distance from opponent to avoid being blocked/forced (resource denial still seeks contention).
        val -= d2(nx, ny, ox, oy) * 0.01
        if best_val is None or val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val, best_move = val, (dx, dy)
    return [int(best_move[0]), int(best_move[1])]