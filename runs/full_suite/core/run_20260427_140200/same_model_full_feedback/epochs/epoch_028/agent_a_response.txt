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

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    # If resources exist: pick move that maximizes "capture advantage" on the best target.
    if resources:
        best_move = (0, 0)
        best_score = -10**18
        for dxm, dym in dirs:
            nx, ny = sx + dxm, sy + dym
            if not valid(nx, ny):
                continue

            self_best = -10**18
            for rx, ry in resources:
                sd = cheb(nx, ny, rx, ry)
                od = cheb(ox, oy, rx, ry)
                # Prefer higher advantage (opponent slower), then closer self.
                # Small deterministic tie-breakers based on coordinates.
                score = (od - sd) * 1000 - sd
                score += (rx * 3 + ry) * 1e-6
                if score > self_best:
                    self_best = score

            # If multiple moves yield same best target score, prefer moves that reduce distance to that best target.
            if self_best > best_score:
                best_score = self_best
                best_move = (dxm, dym)
            elif self_best == best_score:
                # tie-break deterministically: prefer staying toward center-ish by Manhattan to center
                cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
                cur = abs((sx + best_move[0]) - cx) + abs((sy + best_move[1]) - cy)
                cand = abs(nx - cx) + abs(ny - cy)
                if cand < cur:
                    best_move = (dxm, dym)
        return [int(best_move[0]), int(best_move[1])]

    # No resources: move to maximize distance from opponent while avoiding obstacles.
    # Deterministic: lexicographic preference on dirs order.
    best_move = (0, 0)
    best_val = -10**18
    for dxm, dym in dirs:
        nx, ny = sx + dxm, sy + dym
        if not valid(nx, ny):
            continue
        val = cheb(nx, ny, ox, oy) * 1000 - abs((nx - (w - 1)) * 0 + (ny - (h - 1)) * 0)
        if val > best_val:
            best_val = val
            best_move = (dxm, dym)
    return [int(best_move[0]), int(best_move[1])]