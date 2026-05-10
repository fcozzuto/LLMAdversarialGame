def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)

    def to_xy_list(items):
        out = []
        if not items:
            return out
        for it in items:
            if isinstance(it, (list, tuple)) and len(it) >= 2:
                out.append((int(it[0]), int(it[1])))
            elif isinstance(it, dict):
                q = it.get("position", None)
                if isinstance(q, (list, tuple)) and len(q) >= 2:
                    out.append((int(q[0]), int(q[1])))
                elif "x" in it and "y" in it:
                    out.append((int(it["x"]), int(it["y"])))
        return out

    resources = to_xy_list(observation.get("resources"))
    obstacles = set(to_xy_list(observation.get("obstacles")))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    if not resources:
        return [0, 0]

    # Choose resource: prefer ones we are closer to than opponent; otherwise nearest.
    best = None
    best_key = None
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # tie-break deterministically: self advantage, then closer, then lexical
        key = (0 if ds <= do else 1, ds, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry)
    tx, ty = best

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    # Score each move by distance-to-target, and penalize stepping into obstacles and wasting moves when already aligned.
    bestm = (0, 0)
    bestscore = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        score = 0
        if (nx, ny) in obstacles:
            score += 10**6
        score += cheb(nx, ny, tx, ty) * 10
        # Light bias to progress: discourage staying when not on target.
        if (dx, dy) == (0, 0) and not (sx == tx and sy == ty):
            score += 7
        # Prefer moves that reduce both coordinate distances when possible.
        before = cheb(sx, sy, tx, ty)
        after = cheb(nx, ny, tx, ty)
        if after < before:
            score -= 3
        # Deterministic tie-break by move ordering
        key = (score, dx, dy)
        if bestscore is None or key < bestscore:
            bestscore = key
            bestm = (dx, dy)

    return [int(bestm[0]), int(bestm[1])]