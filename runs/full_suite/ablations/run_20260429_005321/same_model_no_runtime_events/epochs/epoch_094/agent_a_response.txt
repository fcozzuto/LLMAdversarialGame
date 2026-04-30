def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx >= dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        return [0, 0]

    # Choose the resource where we are most competitive (minimize (us-opponent) distance gap).
    best_target = None
    best_comp = None
    for rx, ry in resources:
        if (rx, ry) == (sx, sy):
            return [0, 0]
        us = cheb(sx, sy, rx, ry)
        them = cheb(ox, oy, rx, ry)
        comp = us - them
        # tie-break by closer to us, then lexicographic
        key = (comp, us, rx, ry)
        if best_comp is None or key < best_comp:
            best_comp = key
            best_target = (rx, ry)

    tx, ty = best_target

    # Pick the move that maximizes our advantage after the move; keep deterministic tie-breaking.
    best_move = (0, 0)
    best_val = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        us = cheb(nx, ny, tx, ty)
        them = cheb(ox, oy, tx, ty)
        advantage = them - us  # higher is better
        # slight bias to reduce distance to target to progress
        prog = -us
        # deterministic tie-break: prefer lexicographically smallest move among equals by score then move order
        val = (advantage, prog, dx, dy)
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]