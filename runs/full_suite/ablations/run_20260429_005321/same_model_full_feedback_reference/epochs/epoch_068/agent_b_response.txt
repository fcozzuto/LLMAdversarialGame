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

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist2(ax, ay, bx, by):
        dx, dy = ax - bx, ay - by
        return dx * dx + dy * dy

    # Choose best resource based on distance advantage and deterministic tie-break
    target = None
    best = None
    for rx, ry in resources:
        selfd = dist2(sx, sy, rx, ry)
        oppd = dist2(ox, oy, rx, ry)
        adv = oppd - selfd  # positive if we are closer
        key = (-1 if adv <= 0 else 0, -adv, selfd, (rx + ry) * 0 + (-rx) + (-ry))
        # Better key ordering: we want advantage resources first, then maximize adv, then minimize selfd.
        if best is None or key < best:
            best = key
            target = (rx, ry)

    if target is None:
        # No resources: drift toward opponent's corner or center, preferring safety
        tx, ty = (w - 1, 0) if (sx <= w // 2) else (0, h - 1)
    else:
        tx, ty = target

    best_move = (0, 0)
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        self_to_t = dist2(nx, ny, tx, ty)
        opp_to_t = dist2(ox, oy, tx, ty)
        self_to_o = dist2(nx, ny, ox, oy)
        # Score: primary reduce distance to target; secondary increase separation from opponent;
        # tertiary prevent giving opponent an immediate advantage by not moving toward them too much.
        score = (self_to_t, -self_to_o, dist2(nx, ny, ox, oy), -((opp_to_t - self_to_t) if target is not None else 0), dx * 0 + dy * 0)
        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]