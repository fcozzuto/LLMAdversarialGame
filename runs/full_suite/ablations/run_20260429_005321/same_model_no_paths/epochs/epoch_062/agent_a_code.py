def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def neigh_obst(x, y):
        pen = 0
        for ddx in (-1, 0, 1):
            nx = x + ddx
            if nx < 0 or nx >= w:
                continue
            for ddy in (-1, 0, 1):
                if ddx == 0 and ddy == 0:
                    continue
                ny = y + ddy
                if 0 <= ny < h and (nx, ny) in obstacles:
                    pen += 1
        return pen

    if not resources:
        return [0, 0]

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    best_val = -10**18

    for dxm, dym in moves:
        nx, ny = sx + dxm, sy + dym
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue

        myd0 = cheb(nx, ny, ox, oy)
        base = -0.08 * neigh_obst(nx, ny) - 0.01 * myd0

        # Pick a target resource with deterministic scoring.
        target_score = -10**18
        for rx, ry in resources:
            myd = cheb(nx, ny, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            # Prefer resources where we are closer; if not, block by going toward the nearest contested one.
            lead = opd - myd
            # Encourage finishing (smaller myd), slight preference for central-ish resources.
            center = (abs(rx - (w - 1) / 2) + abs(ry - (h - 1) / 2))
            s = 30.0 * (1 if lead > 0 else 0) + 6.0 * lead - 1.5 * myd - 0.02 * center
            # If we can capture immediately, heavily reward.
            if myd == 0:
                s += 1000.0
            if s > target_score or (s == target_score and (rx, ry) < (best_rx, best_ry) if best else False):
                target_score = s
                best_rx, best_ry = rx, ry

        val = base + target_score
        if val > best_val:
            best_val = val
            best = [dxm, dym]

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]