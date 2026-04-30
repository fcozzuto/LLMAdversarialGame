def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    if not valid(sx, sy):
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if valid(nx, ny):
                return [dx, dy]
        return [0, 0]

    if resources:
        best_r = None
        best_key = None
        for rx, ry in resources:
            myd = cheb(sx, sy, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            # Prefer resources where we have an advantage in reachability.
            key = (opd - myd, -myd, -rx, -ry, rx, ry)
            if best_key is None or key > best_key:
                best_key = key
                best_r = (rx, ry)

        rx, ry = best_r
        best_move = [0, 0]
        best_move_key = None
        curd = cheb(sx, sy, rx, ry)
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            nd = cheb(nx, ny, rx, ry)
            # Primary: reduce distance to target; secondary: avoid giving opponent an even bigger edge.
            n_my_adv = cheb(nx, ny, rx, ry)
            n_opp_adv = cheb(ox, oy, rx, ry)
            key = (-nd, curd - nd, n_opp_adv - n_my_adv, -abs(nx - ox) - abs(ny - oy), dx, dy)
            if best_move_key is None or key > best_move_key:
                best_move_key = key
                best_move = [dx, dy]
        return best_move

    # No visible resources: move deterministically toward opponent's corner-adjacent area to constrain.
    tx, ty = (w - 1 if ox < w // 2 else 0, h - 1 if oy < h // 2 else 0)
    best_move = [0, 0]
    best_key = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d = cheb(nx, ny, tx, ty)
        key = (-d, dx, dy)
        if best_key is None or key > best_key:
            best_key = key
            best_move = [dx, dy]
    return best_move