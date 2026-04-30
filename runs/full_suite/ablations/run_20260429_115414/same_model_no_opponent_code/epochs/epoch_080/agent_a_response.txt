def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if not resources:
        best = (10**9, 10**9, None)
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < w and 0 <= ny < h): 
                continue
            if (nx, ny) in obstacles:
                continue
            d2o = cheb(nx, ny, ox, oy)
            if d2o > best[0]:
                best = (d2o, -d2o, (dx, dy))
        if best[2] is None:
            return [0, 0]
        return [best[2][0], best[2][1]]

    best_target = None
    best_cost = 10**18
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # Prefer resources we can reach sooner; avoid ones opponent is closer to.
        cost = ds + (3 if do < ds else 0) + (1 if do == ds else 0)
        # Slightly prefer middle-ish to reduce corner trap.
        cost += 0.1 * cheb(rx, ry, w // 2, h // 2)
        if cost < best_cost:
            best_cost = cost
            best_target = (rx, ry)

    tx, ty = best_target

    best_move = (10**18, None)
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        d_self = cheb(nx, ny, tx, ty)
        d_opp = cheb(nx, ny, ox, oy)

        # If we step onto a resource, prioritize heavily.
        on_resource = 1 if (nx, ny) in resources else 0

        # Anti-interference: if opponent also can get to target quickly, choose safer progress.
        opp_to_target = cheb(ox, oy, tx, ty)
        self_to_target = cheb(nx, ny, tx, ty)

        score = 0
        score += d_self
        score -= 2.5 * d_opp  # keep away from opponent while moving
        score += 4.0 * (1 if (opp_to_target < self_to_target) else 0)
        score -= 50.0 * on_resource

        # Prefer routes that at least reduce distance to target; otherwise mildly avoid.
        score += 0.6 * (1 if d_self > cheb(sx, sy, tx, ty) else 0)

        if score < best_move[0]:
            best_move = (score, (dx, dy))

    return [best_move[1][0], best_move[1][1]]