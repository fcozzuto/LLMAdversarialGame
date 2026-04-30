def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) == 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    valid = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            valid.append((dx, dy, nx, ny))

    if not valid:
        return [0, 0]
    if not resources:
        return [0, 0]

    # Choose target resource based on "positional advantage".
    # Prefer resources where we are closer; if none, pick the one where we are least worse.
    best = None
    best_key = None
    for rx, ry in resources:
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        adv = od - sd  # higher is better
        # Tie-break: prefer nearer resource, and avoid being too close to opponent.
        key = (adv, -sd, cheb(ox, oy, rx, ry))
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)

    rx, ry = best

    # If opponent is closer, "intercept" by aiming for a point on the way (deterministic midpoint bias).
    sd0 = cheb(sx, sy, rx, ry)
    od0 = cheb(ox, oy, rx, ry)
    if od0 < sd0:
        tx = (rx + ox) // 2
        ty = (ry + oy) // 2
        if not (0 <= tx < w and 0 <= ty < h and (tx, ty) not in obstacles):
            tx, ty = rx, ry
    else:
        tx, ty = rx, ry

    # Pick move that reduces distance to target; tie-break by maximizing distance from opponent.
    best_move = None
    best_move_key = None
    for dx, dy, nx, ny in valid:
        d_to = cheb(nx, ny, tx, ty)
        d_opp = cheb(nx, ny, ox, oy)
        # Slight preference for moving (not strictly required) to avoid getting stuck.
        move_pref = 0 if (dx == 0 and dy == 0) else 1
        key = (-d_to, d_opp, move_pref)
        if best_move_key is None or key > best_move_key:
            best_move_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]