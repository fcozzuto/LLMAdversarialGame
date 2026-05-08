def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])
    role = (observation.get("self_role") or "").lower()

    blocked = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            blocked.add((int(p[0]), int(p[1])))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def valid(x, y):
        return in_bounds(x, y) and (x, y) not in blocked

    def dist2(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        return dx * dx + dy * dy

    if "evad" in role:
        corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        away_corner = max(corners, key=lambda c: dist2(ox, oy, c[0], c[1]))
        tx, ty = away_corner[0], away_corner[1]

        best = (0, 0)
        best_score = None
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            d_op = dist2(nx, ny, ox, oy)
            d_goal = dist2(nx, ny, tx, ty)
            score = (d_op, d_goal)  # maximize both lexicographically
            if best_score is None or score > best_score:
                best_score = score
                best = (dx, dy)
        return [int(best[0]), int(best[1])]

    # Pursuer: greedily reduce distance to opponent with slight tie-break toward center
    center = ((w - 1) / 2.0, (h - 1) / 2.0)
    best = (0, 0)
    best_pair = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d = dist2(nx, ny, ox, oy)
        c = dist2(nx, ny, center[0], center[1])
        pair = (-d, -c)  # maximize (-d) => minimize d, then minimize c
        if best_pair is None or pair > best_pair:
            best_pair = pair
            best = (dx, dy)
    return [int(best[0]), int(best[1])]