def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    role = str(observation.get("self_role") or "").lower()
    is_evader = "evader" in role

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            ax, ay = int(p[0]), int(p[1])
            if 0 <= ax < w and 0 <= ay < h:
                obstacles.add((ax, ay))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = abs(ax - bx)
        dy = abs(ay - by)
        return dx if dx > dy else dy

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    if is_evader:
        target = max(corners, key=lambda c: cheb(ox, oy, c[0], c[1]))  # run to corner far from pursuer
        tx, ty = target
    else:
        # pursuer preempt: aim to reduce distance, but also steer toward opponent's "nearest corner"
        opp_corner = min(corners, key=lambda c: cheb(ox, oy, c[0], c[1]))
        tx, ty = ox, oy  # primary: directly chase

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    best_val = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        dcur = cheb(nx, ny, ox, oy)
        if is_evader:
            # maximize survival: increase distance from pursuer, and drift toward chosen corner
            val = (dcur, -cheb(nx, ny, tx, ty), - (abs(nx - tx) + abs(ny - ty)))
            better = best_val is None or val > best_val
        else:
            # pursue: minimize distance; tie-break by moving toward opponent corner to cut evasion routes
            val = (-dcur, -cheb(nx, ny, tx, ty), -(abs(nx - tx) + abs(ny - ty)))
            better = best_val is None or val > best_val
        if better:
            best_val = val
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return best