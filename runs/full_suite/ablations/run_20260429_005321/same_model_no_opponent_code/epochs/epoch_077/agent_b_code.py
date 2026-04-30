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

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def dist2(ax, ay, bx, by):
        dx, dy = ax - bx, ay - by
        return dx * dx + dy * dy

    target = None
    best = None
    for x, y in resources:
        d1 = dist2(sx, sy, x, y)
        d2 = dist2(ox, oy, x, y)
        # Prefer resources we can reach sooner; break ties by being closer.
        key = (d1 - d2, d1)
        if best is None or key < best:
            best = key
            target = (x, y)

    def legal(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    if target is None:
        # No resources: try to move away from opponent deterministically (or stay if blocked).
        best_move = (0, 0)
        best_score = -1
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            s = dist2(nx, ny, ox, oy)
            if s > best_score:
                best_score, best_move = s, (dx, dy)
        return list(best_move)

    tx, ty = target
    best_move = (0, 0)
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        my = dist2(nx, ny, tx, ty)
        opp = dist2(ox, oy, tx, ty)
        # Primary: get closer to target; Secondary: keep advantage over opponent.
        score = (my - opp, my)
        if best_score is None or score < best_score:
            best_score, best_move = score, (dx, dy)

    return [int(best_move[0]), int(best_move[1])]