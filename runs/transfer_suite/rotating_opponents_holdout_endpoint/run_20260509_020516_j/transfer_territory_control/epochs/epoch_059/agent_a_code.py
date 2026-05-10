def choose_move(observation):
    W = int(observation.get("grid_width", 8) or 8)
    H = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])

    def to_set(v):
        s = set()
        for p in v or []:
            if p and len(p) >= 2:
                x, y = int(p[0]), int(p[1])
                if 0 <= x < W and 0 <= y < H:
                    s.add((x, y))
        return s

    obstacles = to_set(observation.get("obstacles"))
    resources = to_set(observation.get("resources"))
    unclaimed = to_set(observation.get("unclaimed_cells"))
    self_path = to_set(observation.get("self_path"))
    opp_pos = observation.get("opponent_position") or [sx, sy]
    ox, oy = int(opp_pos[0]), int(opp_pos[1])

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < W and 0 <= y < H

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def blocked_around(x, y):
        c = 0
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                c += 1
        return c

    targets = resources if resources else unclaimed
    best_t = None
    best_d = 10**9
    for (tx, ty) in targets:
        d = man(sx, sy, tx, ty)
        if d < best_d:
            best_d = d
            best_t = (tx, ty)
    if best_t is None:
        best_t = (ox, oy)

    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        d_to_t = man(nx, ny, best_t[0], best_t[1])
        d_to_opp = man(nx, ny, ox, oy)
        score = -2 * d_to_t + (1 if d_to_opp > 1 else -1) + (1 if (nx, ny) in resources else 0)
        score -= 0.2 * blocked_around(nx, ny)
        if (nx, ny) in self_path:
            score -= 0.3
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]