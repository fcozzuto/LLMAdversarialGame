def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def best_target():
        if not resources:
            return None
        best = None
        best_key = None
        for cx, cy in resources:
            sd = cheb(sx, sy, cx, cy)
            od = cheb(ox, oy, cx, cy)
            # Shift to a "secure grab": prioritize resources we reach earlier than the opponent
            key = (sd - od, -sd, cx, cy)
            if best_key is None or key > best_key:
                best_key = key
                best = (cx, cy)
        return best

    target = best_target()
    if target is None:
        return [0, 0]
    tx, ty = target

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            if (nx, ny) in obs:
                continue
            moves.append((dx, dy, nx, ny))

    if not moves:
        return [0, 0]

    best_m = None
    best_key = None
    for dx, dy, nx, ny in moves:
        sd = cheb(nx, ny, tx, ty)
        # Prefer moving closer to target while keeping opponent further from it
        od_next = cheb(ox, oy, tx, ty)
        opp_push = cheb(nx, ny, ox, oy)
        key = (-sd, opp_push, -od_next, tx, ty, dx, dy)
        if best_key is None or key > best_key:
            best_key = key
            best_m = (dx, dy)

    return [int(best_m[0]), int(best_m[1])]