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
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx + dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if resources:
        # Prefer resources I can reach sooner than the opponent (deterministic tie-break via coordinates).
        best = None
        best_score = None
        for rx, ry in resources:
            myd = dist(sx, sy, rx, ry)
            opd = dist(ox, oy, rx, ry)
            # Lower is better: my distance with a reward for being relatively closer than opponent.
            score = (myd, -opd, rx, ry)
            if best is None or score < best_score:
                best, best_score = (rx, ry), score
        tx, ty = best

        # Pick move that reduces distance to target, but avoid stepping into dead ends near obstacles.
        bestm = None
        bestv = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            v = dist(nx, ny, tx, ty)
            # Small penalty if adjacent (8-neighborhood) has many obstacles (encourage open paths)
            adj_obs = 0
            for ax in (-1, 0, 1):
                for ay in (-1, 0, 1):
                    if ax == 0 and ay == 0:
                        continue
                    xx, yy = nx + ax, ny + ay
                    if not (0 <= xx < w and 0 <= yy < h) or (xx, yy) in obstacles:
                        adj_obs += 1
            v = (v, adj_obs, abs((nx - tx)) + abs((ny - ty)) + 0, nx, ny)
            if bestm is None or v < bestv:
                bestm, bestv = (dx, dy), v
        if bestm is not None:
            return [int(bestm[0]), int(bestm[1])]

    # No resources: head toward center while keeping distance from opponent.
    cx, cy = (w - 1) // 2, (h - 1) // 2
    bestm = None
    bestv = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        v = (dist(nx, ny, cx, cy), -dist(nx, ny, ox, oy), nx, ny)
        if bestm is None or v < bestv:
            bestm, bestv = (dx, dy), v
    if bestm is None:
        return [0, 0]
    return [int(bestm[0]), int(bestm[1])]