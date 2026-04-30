def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set((int(p[0]), int(p[1])) for p in observation.get("obstacles", []))
    resources = [(int(p[0]), int(p[1])) for p in observation.get("resources", []) or []]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(a, b):
        ax, ay = a
        bx, by = b
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    if (int(sx), int(sy)) in obstacles:
        sx, sy = ox, oy

    if resources:
        # Deterministically pick a target resource: prefer ones we're closer to;
        # if tied, prefer lower (x,y) for determinism.
        best_r = None
        best_key = None
        for r in resources:
            r0, r1 = r
            sdist = cheb((sx, sy), (r0, r1))
            odist = cheb((ox, oy), (r0, r1))
            key = (sdist - odist, sdist, r0, r1)
            if best_key is None or key < best_key:
                best_key = key
                best_r = r
        tx, ty = best_r
    else:
        tx, ty = (w - 1) // 2, (h - 1) // 2

    best_score = -10**18
    best_move = (0, 0)

    for dx, dy in moves:
        nx, ny = int(sx) + dx, int(sy) + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        # Reward capturing resource immediately
        score = 0
        if (nx, ny) in set(resources):
            score += 10**6
        # Progress toward target
        score += (cheb((ox, oy), (tx, ty)) - cheb((nx, ny), (tx, ty))) * 50
        # Also keep ourselves from letting opponent become much closer
        score -= cheb((ox, oy), (nx, ny)) * 2
        # Slight deterministic tie-break: prefer lexicographically smaller move deltas
        key2 = (-(score), dx, dy)
        best_key2 = (-(best_score), best_move[0], best_move[1])
        if best_score == -10**18 or key2 < best_key2:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]