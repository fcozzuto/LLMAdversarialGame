def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(map(tuple, observation["obstacles"]))
    resources = list(map(tuple, observation["resources"]))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    def room(x, y):
        c = 0
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                c += 1
        return c

    def best_target():
        best = None
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            myd = man(sx, sy, rx, ry)
            opd = man(ox, oy, rx, ry)
            # Prefer resources we can reach no later than opponent; then closer.
            # If contested, prefer the ones where we have the biggest lead; avoid low room.
            lead = opd - myd
            r = room(rx, ry)
            cand = (-(lead >= 0), -lead, myd, -r)
            if best is None or cand < best:
                best = cand
        if best is None:
            return None
        # Recompute chosen target deterministically from best tuple
        best_lead = best[1]
        best_myd = best[2]
        best_r = -best[3]
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            myd = man(sx, sy, rx, ry)
            opd = man(ox, oy, rx, ry)
            lead = opd - myd
            if (-(lead >= 0), -lead, myd, -room(rx, ry)) == best:
                return (rx, ry)
        return None

    target = best_target()
    if target is None:
        return [0, 0]
    tx, ty = target

    # Choose move that best improves distance to target while staying safe and not easily trapped.
    best_move = (10**9, 10**9, -10**9, 0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        d = man(nx, ny, tx, ty)
        # Slightly bias away from opponent if close (resource-denier pressure).
        opp_close = man(nx, ny, ox, oy)
        cand = (d, -(opp_close >= 3), -room(nx, ny), dx, dy)
        if cand < best_move:
            best_move = cand

    return [int(best_move[3]), int(best_move[4])]