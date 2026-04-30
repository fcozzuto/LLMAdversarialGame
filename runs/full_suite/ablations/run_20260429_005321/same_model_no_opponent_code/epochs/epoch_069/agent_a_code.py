def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for q in observation.get("obstacles") or []:
        if q is None or len(q) < 2:
            continue
        x, y = int(q[0]), int(q[1])
        if 0 <= x < w and 0 <= y < h:
            obstacles.add((x, y))

    resources = []
    for q in observation.get("resources") or []:
        if q is None or len(q) < 2:
            continue
        x, y = int(q[0]), int(q[1])
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

    def nearest_d(x, y):
        if not resources:
            return cheb(x, y, (w - 1) // 2, (h - 1) // 2)
        best = 10**9
        for rx, ry in resources:
            d = cheb(x, y, rx, ry)
            if d < best:
                best = d
        return best

    def is_free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    best_h = -10**18

    base_self = nearest_d(sx, sy)
    base_opp = nearest_d(ox, oy)

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not is_free(nx, ny):
            continue
        ds = nearest_d(nx, ny)
        do = nearest_d(ox, oy)  # opponent position unchanged this turn
        # Prefer reducing our distance to resources; slight preference for moves that also widen our lead.
        h = -ds + 0.08 * (do - ds) - 0.01 * cheb(nx, ny, ox, oy)
        # Deterministic tie-break: prefer moves that reduce distance compared to staying, then lexicographic.
        if h > best_h:
            best_h = h
            best = (dx, dy)
        elif h == best_h:
            if ds < base_self:
                if best is None:
                    best = (dx, dy)
                else:
                    if (dx, dy) < best:
                        best = (dx, dy)
            else:
                if best is None or (dx, dy) < best:
                    best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]