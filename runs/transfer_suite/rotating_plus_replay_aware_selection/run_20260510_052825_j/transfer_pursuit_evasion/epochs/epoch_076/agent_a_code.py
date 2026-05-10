def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = observation.get("obstacles") or []
    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    role = str(observation.get("self_role") or "").lower()
    evader = ("evader" in role) or ("escape" in role)
    pursuer = ("purs" in role) or (not evader)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    def dist2(x, y):
        dx = x - ox
        dy = y - oy
        return dx * dx + dy * dy

    def open_neighbors(x, y):
        c = 0
        for ax, ay in moves:
            nx, ny = x + ax, y + ay
            if free(nx, ny):
                c += 1
        return c

    best_score = None
    best_move = [0, 0]

    for ax, ay in moves:
        nx, ny = sx + ax, sy + ay
        if not free(nx, ny):
            nx, ny = sx, sy
            ax, ay = 0, 0

        d = dist2(nx, ny)
        mob = open_neighbors(nx, ny)

        # Evader: maximize distance, avoid dead-ends (higher mobility).
        # Pursuer: minimize distance, seek constrained positions for self/opponent (lower mobility).
        score = (d if evader else -d) + (0.35 * mob if evader else -0.35 * mob)

        if best_score is None or score > best_score or (score == best_score and (ax, ay) < (best_move[0], best_move[1])):
            best_score = score
            best_move = [ax, ay]

    return [int(best_move[0]), int(best_move[1])]