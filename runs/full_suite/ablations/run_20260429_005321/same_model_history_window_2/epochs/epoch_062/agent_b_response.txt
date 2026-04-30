def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
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
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def obs_pen(x, y):
        pen = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                if (x + dx, y + dy) in obstacles:
                    pen += 2 if dx != 0 and dy != 0 else 1
        return pen

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_score = None
    best_move = (0, 0)

    # Choose a "threat" resource: maximize (opponent distance - self distance), tie-break by self closeness.
    target = None
    if resources:
        best_t = None
        bt = -10**9
        for rx, ry in resources:
            ds = cheb(sx, sy, rx, ry)
            do = cheb(ox, oy, rx, ry)
            val = (do - ds) * 10 - ds
            if val > bt:
                bt = val
                best_t = (rx, ry)
        target = best_t

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        p = obs_pen(nx, ny)

        if target is not None:
            tx, ty = target
            ds2 = cheb(nx, ny, tx, ty)
            score = (cheb(ox, oy, tx, ty) - ds2) * 10 - ds2 - p
        else:
            # Fallback: move toward center-ish while pushing opponent distance.
            center = (w // 2, h // 2)
            score = -cheb(nx, ny, center[0], center[1]) - p + (cheb(nx, ny, ox, oy) * 0.1)

        # Deterministic tie-break: prefer moves with smaller penalty, then lexicographic delta.
        if best_score is None or score > best_score or (score == best_score and (p < obs_pen(best_move[0]+sx, best_move[1]+sy) if inb(best_move[0]+sx, best_move[1]+sy) else True)):
            best_score = score
            best_move = (dx, dy)
        elif score == best_score:
            cand = (dx, dy)
            if cand < best_move:
                best_move = cand

    dx, dy = best_move
    return [int(dx), int(dy)]