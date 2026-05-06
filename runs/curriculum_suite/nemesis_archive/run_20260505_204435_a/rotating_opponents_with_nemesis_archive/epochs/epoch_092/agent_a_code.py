def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])

    resources = observation.get("resources", []) or []
    obstacles_raw = observation.get("obstacles", []) or []
    blocked = set()
    for p in obstacles_raw:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            blocked.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    rpos = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if inb(x, y) and (x, y) not in blocked:
                rpos.append((x, y))
    if not rpos:
        return [0, 0]

    # Pick target that maximizes our lead (self_dist - opp_dist minimized => lead maximized)
    best_t = rpos[0]
    best_lead = -10**9
    for rx, ry in rpos:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        lead = do - ds
        if lead > best_lead or (lead == best_lead and (rx + ry) < (best_t[0] + best_t[1])):
            best_lead = lead
            best_t = (rx, ry)

    tx, ty = best_t
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    curd = cheb(sx, sy, tx, ty)

    # Choose move that best improves distance while avoiding obstacles; deterministic tie-breaks.
    best_m = (0, 0)
    best_score = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in blocked:
            continue
        nd = cheb(nx, ny, tx, ty)
        step_improve = curd - nd
        # Encourage blocking/contending: move that also reduces opponent distance to target
        od = cheb(ox, oy, tx, ty)
        score = step_improve * 1000 - nd * 3
        score += (od - cheb(ox, oy, tx, ty)) * 0  # keep deterministic structure
        score += -(abs((nx - ox)) + abs((ny - oy))) * 0.01
        if score > best_score or (score == best_score and (dx, dy) < best_m):
            best_score = score
            best_m = (dx, dy)

    return [int(best_m[0]), int(best_m[1])]