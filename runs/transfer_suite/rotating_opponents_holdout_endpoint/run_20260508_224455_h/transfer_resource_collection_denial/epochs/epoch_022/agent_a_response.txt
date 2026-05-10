def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    if not resources:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]

    def man(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    def best_step(tx, ty, prefer_block=False):
        # pick step that decreases distance to target; if prefer_block, also slightly
        # increases opponent distance from target
        best = None
        bestv = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if nx < 0 or nx >= w or ny < 0 or ny >= h:
                continue
            if (nx, ny) in obstacles:
                continue
            d = man(nx, ny, tx, ty)
            ov = man(ox, oy, tx, ty)
            v = d * 10
            if prefer_block:
                v -= (ov - d)
                v += man(nx, ny, ox, oy)
            else:
                v += d
            # deterministic tie-break: smaller (dx,dy) in lexicographic order
            key = (v, dx, dy, nx, ny)
            if best is None or key < best:
                best = key
                bestv = (dx, dy)
        if bestv is None:
            return [0, 0]
        return [bestv[0], bestv[1]]

    # Choose a resource: aim for one we can reach earlier; otherwise deny opponent by
    # going to the resource closest to opponent (if within our reach window).
    scored = []
    for rx, ry in resources:
        sd = man(sx, sy, rx, ry)
        od = man(ox, oy, rx, ry)
        # If we reach strictly sooner, big reward; else smaller/denial reward
        score = 0
        if sd < od:
            score += (od - sd) * 100
        else:
            score -= (sd - od) * 60
        score += (16 - od) * 2  # prefer contested resources
        scored.append((score, sd, od, rx, ry))
    scored.sort(key=lambda t: (t[0], t[1], -t[2], t[3], t[4]), reverse=True)
    top = scored[0]
    _, sd, od, rx, ry = top

    # If we're behind by a lot, try to block rather than chase
    if sd - od >= 2:
        return best_step(rx, ry, prefer_block=True)
    return best_step(rx, ry, prefer_block=False)