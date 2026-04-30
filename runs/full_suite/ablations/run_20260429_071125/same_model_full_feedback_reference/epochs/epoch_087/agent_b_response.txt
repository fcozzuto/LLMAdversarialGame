def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in (observation.get("resources") or []):
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def pick_target(ax, ay, bx, by):
        best = None
        for rx, ry in resources:
            myd = cheb(ax, ay, rx, ry)
            opd = cheb(bx, by, rx, ry)
            secure = 1 if myd <= opd else 0
            # Prefer secure resources; among them, prioritize earlier/closer; then deterministic tie.
            key = (secure, -myd, -opd, -(rx + ry), rx, ry)
            if best is None or key > best:
                best = key
        return (best[4], best[5])

    tx, ty = pick_target(sx, sy, ox, oy)
    ptx, pty = pick_target(ox, oy, sx, sy)

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    candidates = []
    same_target = (tx == ptx and ty == pty)
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny):
            continue
        d_to_t = cheb(nx, ny, tx, ty)
        d_to_op_t = cheb(nx, ny, ptx, pty)
        d_to_opp = cheb(nx, ny, ox, oy)
        # If both want same target, add pressure to also approach opponent (interception).
        score = (d_to_t, 0)
        if same_target:
            score = (d_to_t, d_to_opp)
        else:
            # Otherwise, discourage moving toward where opponent is likely heading.
            score = (d_to_t, d_to_op_t)
        candidates.append((score, dx, dy))
    if not candidates:
        return [0, 0]
    candidates.sort()
    return [int(candidates[0][1]), int(candidates[0][2])]