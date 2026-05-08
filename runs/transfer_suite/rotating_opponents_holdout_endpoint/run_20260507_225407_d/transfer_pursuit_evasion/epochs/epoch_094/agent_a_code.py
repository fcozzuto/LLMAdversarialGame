def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    self_role = str(observation.get("self_role") or "").lower()
    opp_role = str(observation.get("opponent_role") or "").lower()
    we_evader = ("evader" in self_role) or ("pursuer" not in self_role and "evader" in opp_role)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    capture_radius = int(observation.get("capture_radius") or 0)

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    dist_now = cheb(sx, sy, ox, oy)
    if (not we_evader) and dist_now <= capture_radius:
        return [0, 0]

    def obstacle_pressure(x, y):
        # Penalize proximity to obstacles to reduce being forced into corners.
        p = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                if (x + ax, y + ay) in obstacles:
                    p += 1
        return p

    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        d = cheb(nx, ny, ox, oy)
        opp_next_bias = 0
        # Deterministic tie-breaker: prefer moves that keep line-of-approach open.
        if not we_evader:
            # pursuer: prefer decreasing distance, slight penalty for obstacle pressure
            val = (-d * 1000) - obstacle_pressure(nx, ny)
        else:
            # evader: prefer increasing distance, slight penalty for obstacle pressure
            val = (d * 1000) - obstacle_pressure(nx, ny)
        cand = (val, -abs(dx), -abs(dy), dx, dy)  # deterministic ordering
        if best is None or cand > best:
            best = cand

    if best is None:
        return [0, 0]
    return [int(best[3]), int(best[4])]