def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def d2(a, b, c, d):
        dx, dy = a - c, b - d
        return dx * dx + dy * dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = (0, (0, 0))
    if resources:
        # Prefer resources that are closer to us, but don't ignore contested ones.
        # Score target: (our_dist - opp_dist) so we lean towards winning claims.
        targets = []
        for tx, ty in resources:
            sd = d2(sx, sy, tx, ty)
            od = d2(ox, oy, tx, ty)
            tie = (sx + sy + tx + ty) & 3
            targets.append((sd - od, sd, tie, (tx, ty)))
        targets.sort()
        # Deterministically pick the top target; if tie, closest by distance.
        _, _, _, (tx, ty) = targets[0]
    else:
        # No visible resources: move toward opponent's side to pressure lanes.
        tx = 0 if ox > sx else (w - 1 if ox < sx else sx)
        ty = 0 if oy > sy else (h - 1 if oy < sy else sy)
    # Choose a move that reduces distance to chosen target (with slight anti-opponent bias)
    best_val = None
    best_move = (0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        myd = d2(nx, ny, tx, ty)
        opd = d2(nx, ny, ox, oy)
        # Minimize my distance; if close, prefer moving away from opponent
        val = myd * 1000 + (-(opd))  # higher opd => smaller negative => preferred
        if best_val is None or val < best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]