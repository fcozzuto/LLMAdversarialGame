def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            blocked.add((int(p[0]), int(p[1])))

    role = str(observation.get("self_role", "pursuer") or "pursuer").lower()
    evade = ("evad" in role) or ("run" in role) or ("away" in role)

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    def dist_cheb(x, y):
        dx = x - ox
        dy = y - oy
        if dx < 0:
            dx = -dx
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    best_move = [0, 0]
    best_score = None

    for dx, dy in deltas:
        x1, y1 = sx + dx, sy + dy
        if not ok(x1, y1):
            continue

        # mobility tie-break: keep options open to counter zigzag
        mob = 0
        for adx, ady in deltas:
            if ok(x1 + adx, y1 + ady):
                mob += 1

        d = dist_cheb(x1, y1)
        # Pursuer minimizes distance; Evader maximizes distance.
        score = (-d if not evade else d) + (0.05 * mob)

        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move