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
            bx, by = int(p[0]), int(p[1])
            if 0 <= bx < w and 0 <= by < h:
                blocked.add((bx, by))

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    role = str(observation.get("self_role") or "").lower()
    is_evader = ("evader" in role) or ("escape" in role) or ("runner" in role) or ("flee" in role) or ("defender" in role)

    def legal(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    def sqdist(x, y):
        dx, dy = x - ox, y - oy
        return dx * dx + dy * dy

    def mobility(x, y):
        c = 0
        for dx, dy in deltas:
            nx, ny = x + dx, y + dy
            if legal(nx, ny):
                c += 1
        return c

    best = None
    best_score = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        d = sqdist(nx, ny)
        m = mobility(nx, ny)
        edge = (nx == 0 or nx == w - 1 or ny == 0 or ny == h - 1)

        if is_evader:
            # Prefer larger distance, then higher mobility; lightly avoid edges.
            score = (d, m, -int(edge))
        else:
            # Pursuer: minimize distance, then higher mobility; slight avoid edges to prevent collisions with obstacles.
            score = (-d, m, -int(edge))

        if best_score is None or score > best_score:
            best_score = score
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]