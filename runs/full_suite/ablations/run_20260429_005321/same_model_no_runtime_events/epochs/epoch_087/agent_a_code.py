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

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx >= dy else dy

    # Safety if somehow off-grid/blocked
    if not valid(sx, sy):
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if valid(nx, ny):
                return [dx, dy]
        return [0, 0]

    if resources:
        # Choose move that improves our chance on a target resource:
        # Minimize (our dist) and (negative advantage), with small deterministic tie breaks.
        best = None
        best_move = [0, 0]
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            move_cheb_to_opp = cheb(nx, ny, ox, oy)
            best_for_move = None
            for rx, ry in resources:
                d_ours = cheb(nx, ny, rx, ry)
                d_op = cheb(ox, oy, rx, ry)
                # Prefer states where we are closer than opponent; also keep move_cheb_to_opp small
                # (slightly helps when resources are contested).
                score = (
                    d_ours,
                    -(d_op - d_ours),  # smaller is better => larger (d_op - d_ours)
                    move_cheb_to_opp,
                    rx, ry
                )
                if best_for_move is None or score < best_for_move:
                    best_for_move = score
            if best is None or best_for_move < best:
                best = best_for_move
                best_move = [dx, dy]
        return [int(best_move[0]), int(best_move[1])]

    # No resources: move toward opponent to potentially deny/pressure.
    # If invalid positions are all blocked, stay.
    best_d = None
    best_move = [0, 0]
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d = cheb(nx, ny, ox, oy)
        if best_d is None or d < best_d or (d == best_d and (dx, dy) < (best_move[0], best_move[1])):
            best_d = d
            best_move = [dx, dy]
    return [int(best_move[0]), int(best_move[1])]