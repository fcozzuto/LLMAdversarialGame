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

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    rem = observation.get("remaining_resource_count", 0)
    try:
        rem = int(rem or 0)
    except:
        rem = 0
    late = rem <= 4

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if resources:
        best = None
        best_key = None
        for tx, ty in resources:
            d_self = cheb(sx, sy, tx, ty)
            d_opp = cheb(ox, oy, tx, ty)
            # Prefer closest; in late game, also prefer targets we can reach earlier.
            key = (d_self, -d_opp, -tx, -ty) if late else (d_self, d_opp, -tx, -ty)
            if best_key is None or key < best_key:
                best_key = key
                best = (tx, ty)
        tx, ty = best
    else:
        # No visible resources: move toward opponent's side to contest if resources reappear.
        tx, ty = (0, 0) if (ox + oy) < (sx + sy) else (w - 1, h - 1)

    # Choose step that minimizes distance to target; tie-break by progress toward opponent when late.
    best_step = (0, 0)
    best_score = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        dist = cheb(nx, ny, tx, ty)
        if late:
            # Prefer reducing distance to opponent more when close to endgame.
            score = (dist, cheb(nx, ny, ox, oy))
        else:
            score = (dist, cheb(nx, ny, ox, oy))
        if best_score is None or score < best_score:
            best_score = score
            best_step = (dx, dy)

    dx, dy = best_step
    return [int(dx), int(dy)]