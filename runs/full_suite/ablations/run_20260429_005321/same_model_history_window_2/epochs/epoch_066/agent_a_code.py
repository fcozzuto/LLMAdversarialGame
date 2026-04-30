def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def legal(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if not resources:
        tx = (w - 1) // 2
        ty = (h - 1) // 2
        best = None
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            # Prefer moving toward center while increasing distance from opponent.
            val = -(cheb(nx, ny, tx, ty)) + cheb(nx, ny, ox, oy)
            if best is None or val > best[0]:
                best = (val, dx, dy)
        if best is None:
            return [0, 0]
        return [best[1], best[2]]

    # Choose next move that maximizes my advantage over opponent for the best resource.
    best = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue

        best_for_me = None  # maximize (opp_dist - my_dist), then minimize my_dist
        for rx, ry in resources:
            my_d = cheb(nx, ny, rx, ry)
            opp_d = cheb(ox, oy, rx, ry)
            adv = opp_d - my_d
            # Encourage taking resources that are reachable sooner even if opponent is also close.
            tie = -my_d
            cand = (adv, tie)
            if best_for_me is None or cand > best_for_me:
                best_for_me = cand

        # Small penalty for proximity to obstacles handled implicitly by legality.
        # Prefer moves that don't increase distance to chosen best resource.
        val = best_for_me[0] * 10 + best_for_me[1]
        if best is None or val > best[0]:
            best = (val, dx, dy)

    if best is None:
        return [0, 0]
    return [best[1], best[2]]