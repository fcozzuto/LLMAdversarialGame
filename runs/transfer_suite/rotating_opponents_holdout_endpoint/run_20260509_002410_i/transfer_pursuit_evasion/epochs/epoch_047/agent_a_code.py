def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
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

    self_role = str(observation.get("self_role") or "").lower()
    is_evader = ("evader" in self_role) or (self_role == "evader")

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def blocked(x, y):
        return (x, y) in obstacles

    def dist(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    # Choose a deterministic "corner" goal for evasion (far from opponent); for pursuit, chase opponent.
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    if is_evader:
        # Prefer farthest corner from opponent; ties by lexicographic.
        cx, cy = max(corners, key=lambda c: (dist(c[0], c[1], ox, oy), -c[0], -c[1]))  # deterministic tie
    else:
        cx, cy = ox, oy

    best = None
    best_score = None
    for d in deltas:
        nx, ny = sx + d[0], sy + d[1]
        if not inb(nx, ny) or blocked(nx, ny):
            continue

        # Mobility: count available next moves to avoid dead ends.
        mob = 0
        for d2 in deltas:
            tx, ty = nx + d2[0], ny + d2[1]
            if inb(tx, ty) and not blocked(tx, ty):
                mob += 1

        d_opp = dist(nx, ny, ox, oy)
        d_goal = dist(nx, ny, cx, cy)

        if is_evader:
            # Maximize distance from opponent; also progress toward chosen corner; prefer higher mobility.
            score = (d_opp * 10) + (-d_goal) + (mob)
        else:
            # Pursue: minimize distance to opponent; prefer moves with higher mobility.
            score = (-d_opp * 10) + (-d_goal * 0.2) + (mob * 0.5)

        tiebreak = (d[0], d[1])  # deterministic
        if best_score is None or score > best_score or (score == best_score and tiebreak < best):
            best_score = score
            best = tiebreak

    # If all moves blocked (highly unlikely), stay put.
    if best is None:
        return [0, 0]
    dx, dy = best[0], best[1]
    if dx not in (-1, 0, 1) or dy not in (-1, 0, 1):
        return [0, 0]
    return [dx, dy]