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

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

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

    dist_now = cheb(sx, sy, ox, oy)
    wants_capture = (not we_evader) and dist_now > capture_radius

    best = (0, 0)
    best_val = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            nx, ny = sx, sy
        dist = cheb(nx, ny, ox, oy)

        # Primary objective: distance to opponent
        val = dist if we_evader else -dist

        # Secondary: corner/edge bias for deterministic evasion/pursuit
        # For evader, prefer larger distance; also prefer moving toward farthest corner from opponent.
        # For pursuer, prefer smallest distance; also prefer moving toward opponent's quadrant.
        if we_evader:
            corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
            far_corner_dist = 0
            for cx, cy in corners:
                d = cheb(nx, ny, cx, cy)
                if d > far_corner_dist:
                    far_corner_dist = d
            val = val * 100 + far_corner_dist
        else:
            # prefer reducing max coordinate difference (tie-break via sum of deltas)
            sdiff = abs(nx - ox) + abs(ny - oy)
            val = val * 100 - sdiff

        # If pursuer and can capture immediately, take it deterministically
        if not we_evader:
            if dist <= capture_radius and wants_capture:
                val = 10**12

        # If evader and would be captured, heavily penalize
        if we_evader and dist <= capture_radius:
            val = -10**12

        if best_val is None or val > best_val:
            best_val = val
            best = (dx, dy)

    return [int(best[0]), int(best[1])]