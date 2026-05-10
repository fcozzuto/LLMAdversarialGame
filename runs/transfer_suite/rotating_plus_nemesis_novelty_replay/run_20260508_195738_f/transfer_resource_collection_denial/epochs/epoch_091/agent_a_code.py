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

    def best_target():
        best = None
        for rx, ry in resources:
            ds = cheb(sx, sy, rx, ry)
            do = cheb(ox, oy, rx, ry)
            lead = do - ds  # positive if we are closer
            # Tie-break deterministically: prefer more lead, then smaller self distance, then closer to opponent (to block), then coords
            cand = (lead, -ds, -cheb(ox, oy, rx, ry), -abs(rx - ox) - abs(ry - oy), rx, ry)
            if best is None or cand > best:
                best = cand
        return best[4], best[5]

    def step_toward(tx, ty):
        best_move = None
        for dx, dy in [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]:
            nx, ny = sx + dx, sy + dy
            if nx < 0 or nx >= w or ny < 0 or ny >= h:
                continue
            if (nx, ny) in obstacles:
                continue
            # Prefer moves that reduce distance to target; slight preference to increase opponent distance.
            ds = cheb(nx, ny, tx, ty)
            do = cheb(ox, oy, tx, ty)
            mydist = cheb(nx, ny, ox, oy)
            score = (-ds, do - ds, -mydist, dx, dy)
            if best_move is None or score > best_move[0]:
                best_move = (score, dx, dy)
        if best_move is None:
            return 0, 0
        return best_move[1], best_move[2]

    if resources:
        tx, ty = best_target()
        return list(step_toward(tx, ty))

    # No resources: go to a corner deterministically; avoid obstacles if possible.
    t = int(observation.get("turn_index", 0))
    if ((ox + oy + t) & 1) == 0:
        tx, ty = 0, 0
    else:
        tx, ty = w - 1, h - 1
    dx, dy = step_toward(tx, ty)
    return [dx, dy]