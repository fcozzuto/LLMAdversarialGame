def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or (0, 0)
    op = observation.get("opponent_position") or (0, 0)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in blocked:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    best = None
    best_key = None
    for x, y in resources:
        dS = cheb(sx, sy, x, y)
        dO = cheb(ox, oy, x, y)
        # New policy: only commit if we're not worse; otherwise, deny by picking farthest-from-opponent target.
        # Key: primary advantage gap, then preference for closer-to-us, then deterministic tie by coords.
        if dS <= dO:
            gap = dO - dS  # larger is better
            key = (0, -gap, dS, x, y)
        else:
            # We're losing; reduce chance we waste time by choosing resources with large opponent distance.
            key = (1, dO, dS, x, y)
        if best_key is None or key < best_key:
            best_key = key
            best = (x, y)

    tx, ty = best

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_dist = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h): 
            continue
        if (nx, ny) in blocked:
            continue
        d = cheb(nx, ny, tx, ty)
        # Deterministic tie-break: prefer moves that decrease distance, then smaller delta order.
        if best_dist is None or d < best_dist or (d == best_dist and (dx, dy) < best_move):
            best_dist = d
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]