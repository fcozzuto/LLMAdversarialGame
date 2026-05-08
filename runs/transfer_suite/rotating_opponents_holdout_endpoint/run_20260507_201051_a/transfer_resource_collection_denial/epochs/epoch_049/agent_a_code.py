def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position") or [0, 0]
    ox, oy = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

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
    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx >= dy else dy

    # Pick a resource we are likely to secure, with a strong bias toward (opponent_distance - self_distance).
    best = None
    best_key = None
    for rx, ry in resources:
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        margin = od - sd  # positive => we can arrive earlier (or at least not later)
        key = (margin, -sd, -(rx + ry))  # tie-break deterministically
        if best is None or key > best_key:
            best = (rx, ry)
            best_key = key
    tx, ty = best

    # Evaluate immediate moves with obstacle avoidance and target progress.
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    bestm = (0, 0)
    bestv = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            nx, ny = sx, sy  # deterministic: effectively invalid => stay

        d1 = cheb(nx, ny, tx, ty)
        d0 = cheb(sx, sy, tx, ty)
        progress = d0 - d1  # prefer reducing distance

        # If we step onto a resource, that's optimal; otherwise keep pressure on the target.
        on_resource = 1 if (nx, ny) == (tx, ty) else 0

        # Add a mild defensive term: avoid moving into squares that let opponent get much closer to that same target.
        opp_d = cheb(ox, oy, tx, ty)
        v = (on_resource, progress, -d1, opp_d - (opp_d), 0)  # fixed structure for determinism
        if bestv is None or v > bestv:
            bestv = v
            bestm = (dx, dy)

    return [int(bestm[0]), int(bestm[1])]