def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in (observation.get("resources") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    if resources:
        best_r = resources[0]
        best_key = (-10**9, 10**9, best_r[0], best_r[1])
        for (rx, ry) in resources:
            d_me = cheb(sx, sy, rx, ry)
            d_op = cheb(ox, oy, rx, ry)
            # prefer resources where I'm closer; otherwise where I'm least behind
            key = (-(d_me - d_op), d_me, rx, ry)
            if key > best_key:
                best_key = key
                best_r = (rx, ry)
        tx, ty = best_r
    else:
        # no resources visible: drift toward opponent side to potentially contest later
        tx, ty = (ox, oy)

    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obstacles:
            continue
        d_to = cheb(nx, ny, tx, ty)
        d_op = cheb(nx, ny, ox, oy)
        # greedy to target, but avoid letting opponent get too close; slight preference for staying safe from edges via inside is implicit
        score = (-d_to) + (0.35 * d_op)
        # If stepping onto a resource, strongly prefer
        if resources and (nx, ny) in obstacles:
            score -= 1000
        if resources and (nx, ny) == (tx, ty):
            score += 1000
        # Tie-break deterministically: prefer smallest dx, then dy
        if score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]