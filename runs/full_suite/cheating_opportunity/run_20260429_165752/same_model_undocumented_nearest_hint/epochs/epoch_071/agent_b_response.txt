def choose_move(observation):
    W = int(observation.get("grid_width") or 8)
    H = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [W - 1, H - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < W and 0 <= y < H and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def legal(nx, ny):
        return 0 <= nx < W and 0 <= ny < H and (nx, ny) not in obstacles

    if not resources:
        # Deterministic fallback: slightly reduce opponent approach while staying legal
        best = (-10**9, 0, 0)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny): 
                continue
            v = cheb(nx, ny, ox, oy)
            if v > best[0]:
                best = (v, dx, dy)
        return [best[1], best[2]]

    # Consider only the closest few resources to limit evaluation
    resources_sorted = sorted(resources, key=lambda p: cheb(sx, sy, p[0], p[1]))
    cand = resources_sorted[: min(6, len(resources_sorted))]

    best_val = -10**18
    best_dx, best_dy = 0, 0
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue

        cell_is_res = 1 if (nx, ny) in resources else 0
        # Evaluate best target for this move
        best_target = -10**18
        for rx, ry in cand:
            d_self = cheb(nx, ny, rx, ry)
            d_opp = cheb(ox, oy, rx, ry)
            # Prefer being closer than opponent; big reward if we step on it
            v = (-d_self) + 0.55 * d_opp + (7.0 * cell_is_res) - 0.06 * (abs((rx - nx) + (ry - ny)))
            if v > best_target:
                best_target = v

        # Mild deterrent to walk into opponent if no immediate resource
        opp_closeness = -0.15 * cheb(nx, ny, ox, oy)
        total = best_target + opp_closeness
        if total > best_val:
            best_val = total
            best_dx, best_dy = dx, dy

    return [int(best_dx), int(best_dy)]