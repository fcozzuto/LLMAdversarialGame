def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or [0, 0]
    ox, oy = observation.get("opponent_position") or [0, 0]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    self_role = str(observation.get("self_role") or "").lower()
    we_evader = ("evader" in self_role) and ("pursuer" not in self_role)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    capture_radius = int(observation.get("capture_radius") or 0)

    def cheb(x1, y1, x2, y2):
        ax = x1 - x2
        if ax < 0:
            ax = -ax
        ay = y1 - y2
        if ay < 0:
            ay = -ay
        return ax if ax > ay else ay

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def ok(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    # If we can be captured immediately, still choose the best escape deterministically.
    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            # Invalid moves are kept in place by engine; model that deterministically.
            nx, ny = sx, sy
        d = cheb(nx, ny, ox, oy)
        # Border-avoidance tie-breaker: keep distance from edges (deterministic, cheap).
        edge_dist = min(nx, ny, (w - 1) - nx, (h - 1) - ny)
        if we_evader:
            # maximize survival proxy: distance from pursuer; break ties by edge_dist and then by move order.
            val = (d, edge_dist)
            key = (-(val[0]), -(val[1]))  # using min selection later
        else:
            # minimize distance to evader; break ties by edge_dist (prefer not getting stuck near edges)
            val = (d, edge_dist)
            key = (val[0], -(val[1]))
        if best is None or key < best[0]:
            best = (key, [dx, dy])
    return best[1]