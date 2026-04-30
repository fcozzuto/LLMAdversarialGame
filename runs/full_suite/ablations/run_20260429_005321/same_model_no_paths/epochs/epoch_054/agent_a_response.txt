def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
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

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    # Choose deterministic target: closest by Chebyshev distance, tie by (x,y)
    resources_sorted = sorted(resources, key=lambda r: (cheb(sx, sy, r[0], r[1]), r[0], r[1]))
    tx, ty = resources_sorted[0]

    # Evaluate moves: prioritize reaching target, keep away from opponent, avoid dead ends
    best = None
    best_val = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d_to_t = cheb(nx, ny, tx, ty)
        d_from_o = cheb(nx, ny, ox, oy)

        # simple mobility estimate (more options -> better)
        mob = 0
        for adx, ady in deltas:
            mx, my = nx + adx, ny + ady
            if valid(mx, my):
                mob += 1

        # If move lands on target, heavily favor it
        score = (0 if (nx == tx and ny == ty) else 1, d_to_t, -mob, -d_from_o, dx, dy)
        if best is None or score < best_val:
            best_val = score
            best = (dx, dy)

    return [best[0], best[1]] if best is not None else [0, 0]