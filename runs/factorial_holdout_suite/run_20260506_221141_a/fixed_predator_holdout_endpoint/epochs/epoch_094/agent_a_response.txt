def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    resources = observation.get("resources") or []
    if not resources:
        return [0, 0]

    obstacles = set()
    for p in observation.get("obstacles") or []:
        x, y = int(p[0]), int(p[1])
        if 0 <= x < w and 0 <= y < h:
            obstacles.add((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # Prefer resources where we are closer (opp_dist - self_dist high),
    # then prioritize smaller self distance, then prefer cells farther from opponent
    # only as a minor tie-break to reduce contention.
    best = None
    best_t = None
    for r in resources:
        rx, ry = int(r[0]), int(r[1])
        if (rx, ry) in obstacles:
            continue
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        if sd == 0:
            t = (10**9, 0, 0, rx, ry)
        else:
            # Encourage winning races: positive (od-sd) means we are closer.
            t = (od - sd, -sd, od, rx, ry)
        if best_t is None or t > best_t:
            best_t = t
            best = (rx, ry)

    if best is None:
        return [0, 0]
    tx, ty = best

    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)

    # If stepping diagonally would be "worse" in terms of contention (rare),
    # optionally switch to one axis deterministically.
    if dx != 0 and dy != 0:
        cand = [([dx, dy]), ([dx, 0]), ([0, dy])]
        scored = []
        for cdx, cdy in [(dx, dy), (dx, 0), (0, dy)]:
            nx, ny = sx + cdx, sy + cdy
            nx = 0 if nx < 0 else (w - 1 if nx >= w else nx)
            ny = 0 if ny < 0 else (h - 1 if ny >= h else ny)
            nsd = cheb(nx, ny, tx, ty)
            nod = cheb(ox, oy, tx, ty)
            scored.append(((nod - nsd, -nsd, cdx, cdy), [cdx, cdy]))
        scored.sort(key=lambda x: x[0], reverse=True)
        return scored[0][1]

    return [dx, dy]