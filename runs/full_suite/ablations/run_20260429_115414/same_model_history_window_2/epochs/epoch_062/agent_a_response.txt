def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for b in observation.get("obstacles") or []:
        if b and len(b) >= 2:
            bx, by = int(b[0]), int(b[1])
            if 0 <= bx < w and 0 <= by < h:
                blocked.add((bx, by))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in blocked:
                resources.append((rx, ry))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    # Choose a contested resource where we can arrive earlier than opponent (deterministic tie-break).
    target = None
    best = None
    if resources:
        for rx, ry in resources:
            ds = cheb(sx, sy, rx, ry)
            do = cheb(ox, oy, rx, ry)
            score = (ds - do, ds, rx + 7 * ry)  # earlier than opponent is smaller ds-do; stable tie-break
            if best is None or score < best:
                best = score
                target = (rx, ry)
    else:
        target = (0, 0)

    tx, ty = target

    # If opponent is already very close to the target, try to sidestep toward same general direction but with perpendicular preference.
    opp_close = cheb(ox, oy, tx, ty) <= 1

    best_move = (0, 0)
    best_val = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d_self = cheb(nx, ny, tx, ty)

        # Obstacle pressure: avoid moving into/adjacent to obstacles.
        adj = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                px, py = nx + ax, ny + ay
                if (px, py) in blocked:
                    adj += 1

        # Gentle "contest" term: prefer actions that also increase opponent distance to our target.
        d_opp = cheb(ox, oy, tx, ty)
        contest = -d_opp  # constant w.r.t move, but keeps structure stable

        # Sidestep when opponent close: discourage moves that reduce our cheb distance too directly if opponent is adjacent to target.
        direct = abs(nx - tx) + abs(ny - ty)
        sidestep_penalty = 0
        if opp_close:
            # Prefer moves that change coordinate more orthogonally relative to vector to target.
            vx = tx - sx
            vy = ty - sy
            # If vector favors x strongly, penalize large dx; else penalize large dy.
            if abs(vx) >= abs(vy):
                sidestep_penalty = abs(dx)
            else:
                sidestep_penalty = abs(dy)

        val = (d_self, adj, sidestep_penalty, direct, dx, dy)
        if best_val is None or val < best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]