def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    # Pick a target that we are likely to beat the opponent to (chebyshev due to diagonal moves).
    best_t = None
    best_key = None
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        key = (do - ds, -ds, rx, ry)
        if best_key is None or key > best_key:
            best_key, best_t = key, (rx, ry)
    tx, ty = best_t

    # Choose among valid one-step moves the one that improves advantage to the chosen target,
    # with a small tie-break for moving closer to any resource.
    dirs = (-1, 0, 1)
    current_best = None
    current_move = [0, 0]
    for dx in dirs:
        for dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            self_d = cheb(nx, ny, tx, ty)
            opp_d = cheb(ox, oy, tx, ty)
            # Approximate: opponent might also move, so encourage keeping our advantage.
            adv = opp_d - self_d
            # Secondary: move closer to the nearest remaining resource.
            mind = None
            for rx, ry in resources:
                d = cheb(nx, ny, rx, ry)
                if mind is None or d < mind:
                    mind = d
            key = (adv, -mind, -abs(nx - sx) - abs(ny - sy), nx, ny)
            if current_best is None or key > current_best:
                current_best, current_move = key, [dx, dy]
    return current_move