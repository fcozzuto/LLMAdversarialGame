def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def legal(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    if resources:
        best_target = None
        best_key = None
        for tx, ty in resources:
            dself = cheb(sx, sy, tx, ty)
            dopp = cheb(ox, oy, tx, ty)
            # Prefer closer resources; if tied, prefer those farther from opponent.
            key = (dself, -dopp, tx, ty)
            if best_key is None or key < best_key:
                best_key = key
                best_target = (tx, ty)
        tx, ty = best_target
    else:
        tx, ty = (w - 1) - sx, (h - 1) - sy

    best_move = (0, 0)
    best_score = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        if resources:
            d_to_target = cheb(nx, ny, tx, ty)
            d_to_opp = cheb(nx, ny, ox, oy)
            d_opp_now = cheb(sx, sy, ox, oy)
            d_self_now = cheb(sx, sy, tx, ty)
            # Minimize distance to target; break ties by maximizing distance from opponent,
            # and (if still tied) improving our progress vs current.
            key = (d_to_target, -d_to_opp, d_self_now - d_to_target, tx, ty)
        else:
            d_to_opp = cheb(nx, ny, ox, oy)
            key = (-d_to_opp, nx, ny)
        if best_score is None or key < best_score:
            best_score = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]