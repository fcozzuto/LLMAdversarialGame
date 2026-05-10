def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    obstacles = set()
    for p in (observation.get("obstacles", []) or []):
        try:
            obstacles.add((int(p[0]), int(p[1])))
        except Exception:
            pass
    resources = []
    for r in (observation.get("resources", []) or []):
        try:
            resources.append((int(r[0]), int(r[1])))
        except Exception:
            pass

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    ti = int(observation.get("turn_index", 0) or 0)

    if not resources:
        tx, ty = ((0, 0) if ((ox + oy + ti) & 1) == 0 else (w - 1, h - 1))
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obstacles:
            for ddx, ddy in moves:
                nx, ny = sx + ddx, sy + ddy
                if in_bounds(nx, ny) and (nx, ny) not in obstacles:
                    return [ddx, ddy]
        return [dx, dy]

    # Choose a resource that maximizes lead over opponent; then prefer shorter self distance.
    best = None
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        lead = do - ds
        # Encourage picking resources with small self distance when lead is similar.
        key = (lead, -ds, -(abs(rx - ox) + abs(ry - oy)), rx, ry)
        if best is None or key > best[0]:
            best = (key, rx, ry)
    _, tx, ty = best

    # Move one step toward target; avoid obstacles deterministically; break ties by fixed move order.
    best_move = (None, None)
    best_score = None
    for ddx, ddy in moves:
        nx, ny = sx + ddx, sy + ddy
        if not in_bounds(nx, ny) or (nx, ny) in obstacles:
            continue
        # Score: reduce distance to target most, then don't get closer to opponent too much.
        d1 = cheb(nx, ny, tx, ty)
        d2 = cheb(nx, ny, ox, oy)
        score = (-d1, d2, ddx, ddy)
        if best_score is None or score > best_score:
            best_score = score
            best_move = (ddx, ddy)

    if best_move[0] is None:
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]