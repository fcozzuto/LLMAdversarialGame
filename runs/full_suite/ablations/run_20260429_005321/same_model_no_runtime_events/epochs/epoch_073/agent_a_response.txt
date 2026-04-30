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

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    if not valid(sx, sy):
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0), (-1, -1), (1, 1), (-1, 1), (1, -1)]:
            nx, ny = sx + dx, sy + dy
            if valid(nx, ny):
                return [dx, dy]
        return [0, 0]

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    tx, ty = (w - 1) // 2, (h - 1) // 2
    if resources:
        best = None
        for rx, ry in resources:
            ds = dist(sx, sy, rx, ry)
            do = dist(ox, oy, rx, ry)
            adv = do - ds
            # Prefer a resource we can reach at least as fast as opponent; break ties by closer ds.
            score = (adv, -ds, -(rx + ry), -rx)
            if best is None or score > best[0]:
                best = (score, rx, ry)
        _, tx, ty = best

    best_move = (None, None, None, None)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        ds_next = dist(nx, ny, tx, ty)
        # If aiming for a resource, also consider opponent's ability to take it next.
        if resources:
            d_op = dist(ox, oy, tx, ty)
            # Encourage moves that reduce our distance and (when close) increase their distance.
            local = (-(ds_next), (d_op - ds_next), -(nx + ny))
        else:
            # No resources: drift toward center while keeping distance from opponent.
            local = (-(ds_next), dist(nx, ny, ox, oy), -(nx + ny))
        if best_move[0] is None or local > best_move[0]:
            best_move = (local, dx, dy, nx)
    if best_move[1] is None:
        return [0, 0]
    return [int(best_move[1]), int(best_move[2])]