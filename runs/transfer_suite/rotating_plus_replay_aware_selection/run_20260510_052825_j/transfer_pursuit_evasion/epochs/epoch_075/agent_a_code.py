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
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    def d2(x, y):
        dx, dy = x - ox, y - oy
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
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            nx, ny = sx, sy
            dx, dy = 0, 0

        if evader:
            # Run from pursuer; prefer moves that keep options.
            dd = d2(nx, ny)
            cand_open = open_neighbors(nx, ny)
            sc = dd + 0.15 * cand_open - 0.02 * d2(sx, sy)
        else:
            # Chase pursuer; prioritize landing on opponent and reducing distance.
            if nx == ox and ny == oy:
                sc = 1e9 + 10 * open_neighbors(nx, ny)
            else:
                cand_open = open_neighbors(nx, ny)
                sc = -(d2(nx, ny)) + 0.10 * cand_open - 0.01 * d2(sx, sy)

        if best_score is None or (sc > best_score) or (sc == best_score and (dx, dy) < (best_move[0], best_move[1])):
            best_score = sc
            best_move = [dx, dy]

    return best_move