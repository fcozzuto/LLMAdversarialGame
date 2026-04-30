def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(a, b):
        dx = a[0] - b[0]
        if dx < 0: dx = -dx
        dy = a[1] - b[1]
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    resources = []
    for p in observation.get("resources", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inside(x, y) and (x, y) not in obstacles:
                resources.append((x, y))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def best_move(tgt):
        best = (-10**18, 0, 0)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inside(nx, ny) or (nx, ny) in obstacles:
                continue
            d_t = cheb((nx, ny), tgt)
            d_o = cheb((nx, ny), (ox, oy))
            # Prefer getting closer to target while staying farther from opponent.
            # Also reward immediate capture-ish (d_t small).
            score = -d_t * 10 + d_o + (-1 if d_t == 0 else 0)
            if score > best[0]:
                best = (score, dx, dy)
        return [best[1], best[2]]

    if not resources:
        # Drift away deterministically
        best = (-10**18, 0, 0)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inside(nx, ny) or (nx, ny) in obstacles:
                continue
            score = cheb((nx, ny), (ox, oy))
            if score > best[0]:
                best = (score, dx, dy)
        return [best[1], best[2]]

    # Choose a resource we are relatively closer to than the opponent.
    best_tgt = None
    best_key = None
    for r in resources:
        ds = cheb((sx, sy), r)
        do = cheb((ox, oy), r)
        key = ds - 0.35 * do  # lower is better
        if best_key is None or key < best_key:
            best_key = key
            best_tgt = r

    return best_move(best_tgt)