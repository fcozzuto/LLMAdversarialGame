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

    # Choose a resource we can reach earlier than opponent (otherwise fallback).
    best_tx = None
    best_ty = None
    best_adv = None
    if resources:
        for tx, ty in resources:
            my = d2(sx, sy, tx, ty)
            opd = d2(ox, oy, tx, ty)
            adv = opd - my  # positive means we are closer (in squared distance)
            # Secondary tie-break: prefer resources that are closer to us (smaller my)
            key = (adv, -my, -tx, -ty)
            if best_adv is None or key > best_adv:
                best_adv = key
                best_tx, best_ty = tx, ty

    # If no resources or we're not realistically closer, aim to contest by moving toward midpoint.
    if best_tx is None:
        tx, ty = (sx + ox) / 2.0, (sy + oy) / 2.0
        best_tx, best_ty = int(round(tx)), int(round(ty))

    # Evaluate immediate moves with a contest/block heuristic: reduce our distance to target,
    # while increasing distance of opponent to that same target (simple interception).
    best_move = (0, 0)
    best_val = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue

        if resources:
            my_to = d2(nx, ny, best_tx, best_ty)
            op_to = d2(ox, oy, best_tx, best_ty)
            # Also prefer steps that move us into the "threat zone" closer than opponent next step.
            my_next = my_to
            op_next = d2(ox, oy, best_tx, best_ty)
            # Simple block: prefer moves that don't allow opponent to be significantly closer after it moves.
            block = -max(0, (op_to - my_next))
            # Slightly avoid moving into far-off corners when target is set
            corner_pen = 0.02 * (nx * nx + ny * ny)
            val = (1000000 - my_to) + 0.5 * (op_to) + block - corner_pen
        else:
            # Fallback: head to midpoint and slightly avoid opponent proximity
            mid_pen = d2(nx, ny, (ox + sx) / 2.0, (oy + sy) / 2.0)
            opp_pen = d2(nx, ny, ox, oy)
            val = (-mid_pen) + 0.1 * opp_pen

        # Deterministic tie-break: prefer lexicographically smallest (dx,dy)
        key = (val, -dx, -dy)
        if best_val is None or key > best_val:
            best_val = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]