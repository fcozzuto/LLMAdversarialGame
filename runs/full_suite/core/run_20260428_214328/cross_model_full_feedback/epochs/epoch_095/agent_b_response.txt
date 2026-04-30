def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    seen = set()
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles and (x, y) not in seen:
                resources.append((x, y))
                seen.add((x, y))

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist_cheb(a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    if resources:
        # Move toward closest resource, avoid opponent's immediate capture
        best = None
        best_score = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not in_bounds(nx, ny):
                continue
            if (nx, ny) in obstacles:
                continue
            # distance to nearest resource
            d = min(dist_cheb((nx, ny), r) for r in resources)
            # penalize proximity to opponent
            d_op = dist_cheb((nx, ny), (ox, oy))
            score = -d + (0 if d_op <= 0 else 0) - d_op * 0  # simple: prefer closer to resource
            if best is None or score > best_score:
                best = (dx, dy)
                best_score = score
        if best is not None:
            return [best[0], best[1]]

    # No resources or all blocked: simple defensive/neutral rules
    best = (0, 0)
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue
        # stay away from opponent if possible
        d_op = dist_cheb((nx, ny), (ox, oy))
        score = d_op
        if best_score is None or score > best_score:
            best = (dx, dy)
            best_score = score
    return [best[0], best[1]]