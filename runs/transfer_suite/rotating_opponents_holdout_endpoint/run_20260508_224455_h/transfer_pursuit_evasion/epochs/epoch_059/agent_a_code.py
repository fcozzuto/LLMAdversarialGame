def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])
    role = (observation.get("self_role") or "").lower()

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    best = None
    best_key = None

    # Aim: pursuer minimizes distance; evader maximizes distance.
    # Tie-break: prefer moves that keep clear of obstacles by maximizing available next-steps.
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        d = cheb(nx, ny, ox, oy)
        mdx, mdy = abs(nx - ox), abs(ny - oy)
        man = mdx + mdy

        # Count legal neighbors from candidate (more freedom = better for evader; worse for pursuer).
        free = 0
        for ddx, ddy in deltas:
            tx, ty = nx + ddx, ny + ddy
            if inb(tx, ty) and (tx, ty) not in obstacles:
                free += 1

        if "evader" in role or role == "runner":
            # maximize distance, then maximize freedom, then move toward farthest corner deterministically
            far_corner = (w - 1, h - 1) if (ox < w // 2) == (oy < h // 2) else (0, 0)
            cc = cheb(nx, ny, far_corner[0], far_corner[1])
            key = (d, free, cc, -man, dx, dy)
            better = best_key is None or key > best_key
        else:
            # pursuer: minimize distance, then minimize opponent distance tie-break, then minimize freedom (to reduce escape)
            key = (-d, -man, -free, dx, dy)
            better = best_key is None or key > best_key

        if better:
            best_key = key
            best = [dx, dy]

    # Safety fallback
    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]