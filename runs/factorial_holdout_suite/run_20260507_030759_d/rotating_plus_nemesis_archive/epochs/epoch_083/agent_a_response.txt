def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
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

    if not resources:
        return [0, 0]
    if (sx, sy) in resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # Choose the best resource by "lead" (we can arrive earlier than opponent),
    # then break ties by smaller distance and deterministic coordinate ordering.
    best_t = None
    best_key = None
    for tx, ty in resources:
        sd = cheb(sx, sy, tx, ty)
        od = cheb(ox, oy, tx, ty)
        lead = od - sd
        key = (lead, -sd, tx, ty)
        if best_key is None or key > best_key:
            best_key = key
            best_t = (tx, ty)

    tx, ty = best_t
    deltas = [(-1, -1), (0, -1), (1, -1),
              (-1, 0), (0, 0), (1, 0),
              (-1, 1), (0, 1), (1, 1)]
    # Prefer moves that reduce our distance to target while also reducing opponent advantage.
    best_move = [0, 0]
    best_move_key = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        nsd = cheb(nx, ny, tx, ty)
        nod = cheb(ox, oy, tx, ty)
        # slight penalty for moving away from target to avoid oscillation
        dist_pen = nsd
        # If we reach the target, pick immediately.
        reach_bonus = 1000 if nsd == 0 else 0
        key = (reach_bonus - dist_pen + (nod - nsd), -nsd, dx, dy)
        if best_move_key is None or key > best_move_key:
            best_move_key = key
            best_move = [dx, dy]
    return best_move