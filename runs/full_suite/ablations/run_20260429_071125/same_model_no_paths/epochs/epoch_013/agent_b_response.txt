def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for p in (observation.get("obstacles", []) or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    resources = []
    for r in (observation.get("resources", []) or []):
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in blocked:
                resources.append((x, y))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def dist(a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))  # Chebyshev

    if not inside(sx, sy):
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if inside(nx, ny):
                return [dx, dy]
        return [0, 0]

    if not resources:
        target = (w - 1, h - 1) if (sx + sy) <= (ox + oy) else (0, 0)
        best_move, best_val = (0, 0), -10**9
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inside(nx, ny):
                continue
            val = -dist((nx, ny), target)
            if val > best_val:
                best_val, best_move = val, (dx, dy)
        return [best_move[0], best_move[1]]

    best_move, best_val = (0, 0), -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        my_pos = (nx, ny)
        # Evaluate best resource by "who's closer" advantage; prefer immediate closeness and outpacing opponent.
        best_r_val = -10**18
        for r in resources:
            d_my = dist(my_pos, r)
            d_op = dist((ox, oy), r)
            # If d_my is small, strongly good; if I'm not leading vs opponent, penalize.
            r_val = -2.0 * d_my + 1.0 * d_op
            # Slight tie-break favoring resources "in my direction" (toward opponent corner).
            r_val += -0.05 * dist(my_pos, (w - 1, h - 1))
            if r_val > best_r_val:
                best_r_val = r_val
        # Small preference for staying near center to reduce long detours when tied.
        center_bias = -0.01 * dist(my_pos, (w / 2 - 0.5, h / 2 - 0.5))
        total = best_r_val + center_bias
        if total > best_val:
            best_val, best_move = total, (dx, dy)

    return [best_move[0], best_move[1]]