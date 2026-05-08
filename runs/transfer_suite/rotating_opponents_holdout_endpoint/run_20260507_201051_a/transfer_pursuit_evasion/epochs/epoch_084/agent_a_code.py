def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    role = (observation.get("self_role") or "").lower()
    is_pursuer = ("purs" in role) or ("chaser" in role) or ("hunter" in role) or ("seeker" in role) or ("pursuer" in role)

    # Repulsion from obstacles to avoid cornering into dead-ends.
    neigh = [(-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def obstacle_pressure(x, y):
        p = 0
        for dx, dy in neigh:
            if (x + dx, y + dy) in obstacles:
                p += 1
        return p

    # Evader target: farthest corner deterministically.
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    if is_pursuer:
        tx, ty = ox, oy
    else:
        # Prefer corner farthest from opponent; break ties by farthest from self (deterministic).
        tx, ty = max(corners, key=lambda c: (abs(c[0] - ox) + abs(c[1] - oy), abs(c[0] - sx) + abs(c[1] - sy)))

    best_move = (0, 0)
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        d_op = abs(nx - ox) + abs(ny - oy)  # manhattan
        d_t = abs(nx - tx) + abs(ny - ty)
        press = obstacle_pressure(nx, ny)

        # Also add a small "mobility" term: count valid moves from candidate to prevent trapping.
        mob = 0
        for mdx, mdy in moves:
            x2, y2 = nx + mdx, ny + mdy
            if inb(x2, y2):
                mob += 1

        if is_pursuer:
            score = -d_op * 100 - d_t * 5 - press * 20 + mob
        else:
            score = d_op * 100 - d_t * 5 - press * 20 + mob

        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]