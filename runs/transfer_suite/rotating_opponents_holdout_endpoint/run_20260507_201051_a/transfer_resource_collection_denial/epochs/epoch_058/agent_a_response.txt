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
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    # Pick resource where we have the biggest reach advantage over the opponent.
    if resources:
        best = None
        best_key = None
        for x, y in resources:
            ds = cheb(sx, sy, x, y)
            do = cheb(ox, oy, x, y)
            adv = do - ds
            # Key: max advantage, then smaller our distance, then deterministic position ordering
            key = (adv, -ds, -x, -y)
            if best_key is None or key > best_key:
                best_key = key
                best = (x, y)
        tx, ty = best
    else:
        # No visible resources: move toward the most probable area near opponent (interference).
        tx, ty = (w - 1 - ox, h - 1 - oy)

    # Choose one-step move that reduces Chebyshev distance to target and avoids obstacles.
    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]
    bestm = (0, 0)
    bestk = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        d = cheb(nx, ny, tx, ty)
        # Prefer smaller distance; tie-break deterministically toward opponent direction.
        closer = -d
        press = (cheb(nx, ny, ox, oy) - cheb(sx, sy, ox, oy))
        key = (closer, -press, dx, dy)
        if bestk is None or key > bestk:
            bestk = key
            bestm = (dx, dy)

    return [int(bestm[0]), int(bestm[1])]