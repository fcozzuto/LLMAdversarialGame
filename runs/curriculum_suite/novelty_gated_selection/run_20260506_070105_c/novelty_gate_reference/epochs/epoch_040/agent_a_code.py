def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    resources_sorted = sorted(resources, key=lambda t: (-(cheb(ox, oy, t[0], t[1])), t[0], t[1]))
    top = resources_sorted[:min(5, len(resources_sorted))]

    best_move = (0, 0)
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h): 
            continue
        if (nx, ny) in obstacles:
            continue

        # Interference-style: assume opponent can reduce cheb distance by ~1 toward the chosen resource.
        # Score favors resources where we keep an advantage even after that.
        vals = []
        for tx, ty in top:
            my_d = cheb(nx, ny, tx, ty)
            opp_d = cheb(ox, oy, tx, ty)
            opp_d_est = opp_d - 1
            if opp_d_est < 0: opp_d_est = 0
            advantage = opp_d_est - my_d
            # Secondary preference: not too far for us.
            vals.append((advantage, -my_d, tx, ty))
        # Choose move by best "guaranteed" advantage among top targets; tie-break deterministically.
        vals_sorted = sorted(vals, reverse=True)
        key = (vals_sorted[0][0], vals_sorted[0][1], vals_sorted[0][2], vals_sorted[0][3], dx, dy)
        if best_val is None or key > best_val:
            best_val = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]