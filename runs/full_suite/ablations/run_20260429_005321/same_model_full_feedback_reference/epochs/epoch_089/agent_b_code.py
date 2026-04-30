def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
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

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def legal(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    def d2(ax, ay, bx, by):
        dx, dy = ax - bx, ay - by
        return dx * dx + dy * dy

    # Pick best target resource (prefer winning races; deterministic tie-break by distance, then coord)
    tx = ty = None
    if resources:
        best = None
        for rx, ry in resources:
            myt = d2(sx, sy, rx, ry)
            opt = d2(ox, oy, rx, ry)
            # Advantage: smaller myt - opt means we get there earlier (or tie)
            adv = myt - opt
            # secondary: prefer closer to us, then prefer closer to center
            center = (w - 1) / 2.0, (h - 1) / 2.0
            cdist = d2(rx, ry, int(center[0]), int(center[1]))
            key = (adv, myt, cdist, rx, ry)
            if best is None or key < best[0]:
                best = (key, rx, ry)
        tx, ty = best[1], best[2]

    # If no target, drift to more central and away from opponent
    if tx is None:
        cx, cy = (w - 1) // 2, (h - 1) // 2
        # Choose a "soft" target: move toward center but away from opponent
        # Deterministically pick among candidate centers/diagonals by evaluating step scores later anyway.
        tx, ty = cx, cy

    # Evaluate next moves greedily toward target, while maintaining safety from opponent.
    # Also slightly prefer moves that reduce opponent reachability (race pressure).
    best_move = (0, 0)
    best_score = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue

        # If stepping onto target resource, strongly prefer it
        on_resource = 1 if resources and (nx, ny) in set(resources) else 0

        dist_to_t = d2(nx, ny, tx, ty)
        dist_from_op = d2(nx, ny, ox, oy)
        dist_op_to_t = d2(ox, oy, tx, ty)

        # Race pressure: compare my next distance vs opponent's current distance to target
        my_to_t_next = dist_to_t
        adv_next = my_to_t_next - dist_op_to_t  # lower is better

        # Favor staying within bounds already satisfied; small tie-break toward lower dx, then dy for determinism
        center = ((w - 1) // 2, (h - 1) // 2)
        c_pen = d2(nx, ny, center[0], center[1])

        score = (
            100000 * on_resource
            - 3 * dist_to_t
            + 0.8 * dist_from_op
            - 5 * adv_next
            - 0.02 * c_pen
            - 0.001 * (dx * dx + dy * dy)
        )

        if best_score is None or score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]