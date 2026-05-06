def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or (0, 0)
    op = observation.get("opponent_position") or (w - 1, h - 1)
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

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    # Choose a resource that is close to us and relatively far from opponent
    if resources:
        best_t = None
        best_key = None
        for tx, ty in resources:
            ds = man(sx, sy, tx, ty)
            do = man(ox, oy, tx, ty)
            key = (ds - 0.6 * do, tx, ty)
            if best_key is None or key < best_key:
                best_key = key
                best_t = (tx, ty)
        tx, ty = best_t
    else:
        tx, ty = w // 2, h // 2

    best_move = (0, 0)
    best_score = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        ds = man(nx, ny, tx, ty)
        # Encourage capture path: prefer moving generally toward target
        toward = -(ds * 1.0)

        # Opponent pressure: when close, try to increase distance and avoid being blocked
        dop = man(nx, ny, ox, oy)
        cur_dop = man(sx, sy, ox, oy)
        threat = 0.0
        if cur_dop <= 3:
            threat = (cur_dop - dop) * 2.0  # penalize getting closer
        else:
            threat = -max(0, 3 - dop) * 1.5

        # Slight preference for moves that don't wander: discourage increasing target distance too much
        step_reg = -max(0, ds - man(sx, sy, tx, ty)) * 0.5

        score = toward + threat + step_reg

        if best_score is None or score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]