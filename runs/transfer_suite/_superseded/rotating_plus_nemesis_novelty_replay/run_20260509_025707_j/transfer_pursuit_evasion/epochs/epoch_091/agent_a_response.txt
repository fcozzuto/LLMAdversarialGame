def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for t in observation.get("obstacles") or []:
        if isinstance(t, (list, tuple)) and len(t) >= 2:
            x, y = int(t[0]), int(t[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    def manh(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    target_corner = min(corners, key=lambda c: manh((ox, oy), c))
    tx, ty = target_corner

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def open_neighbors(x, y):
        cnt = 0
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                cnt += 1
        return cnt

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    best = None
    best_score = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        if nx == ox and ny == oy:
            return [dx, dy]

        d_me = manh((nx, ny), (ox, oy))
        d_my_corner = manh((nx, ny), (tx, ty))
        d_op_corner = manh((ox, oy), (tx, ty))

        # If we can reach the corner no later than the opponent, prioritize corner-blocking.
        block_term = (d_my_corner - d_op_corner)
        # Prefer positions with more mobility to avoid getting funneled near corner obstacles.
        mob = open_neighbors(nx, ny)

        # Maximize: (closer to opponent) and (tighter corner block), while staying mobile.
        score = (-2.3 * d_me) + (-1.2 * block_term) + (0.12 * mob)

        if score > best_score:
            best_score = score
            best = (dx, dy)

    return [0, 0] if best is None else [int(best[0]), int(best[1])]