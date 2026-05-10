def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    if not resources:
        return [0, 0]
    obst = {(x, y) for x, y in obstacles}
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def legal(x, y):
        return inb(x, y) and (x, y) not in obst

    def man(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx + dy

    # Pick best target by "advantage": prefer being closer than opponent (then nearer to finish).
    best = None  # (adv, -self_d, self_d, rx, ry)
    for rx, ry in resources:
        sd = man(sx, sy, rx, ry)
        od = man(ox, oy, rx, ry)
        adv = od - sd
        cand = (adv, -sd, sd, rx, ry)
        if best is None or cand > best:
            best = cand
    _, _, _, tx, ty = best

    # If opponent is clearly closer to every resource, switch to the "least-worst" denial target:
    # maximize (opp_d - self_d) is already denial; but add a second pass to avoid dithering:
    # if best adv <= 0, head toward the resource with minimum opponent distance to reduce chase window.
    if best[0] <= 0:
        best2 = None  # (opp_d, self_d, rx, ry)
        for rx, ry in resources:
            sd = man(sx, sy, rx, ry)
            od = man(ox, oy, rx, ry)
            cand2 = (od, sd, rx, ry)
            if best2 is None or cand2 < best2:
                best2 = cand2
        _, _, tx, ty = best2

    # Move one step to reduce manhattan distance to target while avoiding obstacles.
    bestm = (10**9, sx, sy)  # (dist, nx, ny)
    for mdx, mdy in moves:
        nx, ny = sx + mdx, sy + mdy
        if not legal(nx, ny):
            continue
        d = man(nx, ny, tx, ty)
        if d < bestm[0]:
            bestm = (d, nx, ny)
        elif d == bestm[0]:
            # deterministic tie-break: prefer staying in place, then lexicographic.
            if (nx, ny) == (sx, sy):
                bestm = (d, nx, ny)
            elif (nx, ny) < (bestm[1], bestm[2]):
                bestm = (d, nx, ny)

    nx, ny = bestm[1], bestm[2]
    return [nx - sx, ny - sy]