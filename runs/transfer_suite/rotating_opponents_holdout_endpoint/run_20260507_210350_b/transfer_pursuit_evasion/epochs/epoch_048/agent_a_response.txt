def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    rolestr = (observation.get("self_role", "") or "").lower()
    is_evader = any(k in rolestr for k in ("evader", "escape", "flee", "runner"))
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def valid(x, y):
        return inb(x, y) and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        return dx if dx > dy else dy

    def edge_dist(x, y):
        return min(x, w - 1 - x, y, h - 1 - y)

    def obstacle_gap(x, y):
        # larger is safer; 0 if standing on/adjacent to obstacle is still allowed by rules,
        # but adjacency is discouraged for evasion.
        best = 10
        for ax, ay in obstacles:
            d = cheb(x, y, ax, ay)
            if d < best:
                best = d
        return best if obstacles else 10

    best = (0, 0)
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            nx, ny, dx, dy = sx, sy, 0, 0
        d = cheb(nx, ny, ox, oy)

        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        center_bias = -abs(nx - cx) - abs(ny - cy)  # deterministic tie-breaker

        if is_evader:
            # maximize distance; prefer staying away from edges when opponent is close;
            # also prefer squares with more clearance from obstacles.
            closeness = -cheb(nx, ny, ox, oy)
            edge_pref = edge_dist(nx, ny)
            gap_pref = obstacle_gap(nx, ny)
            score = (d, edge_pref + (1.0 / (1.0 + max(0.0, closeness))), gap_pref, center_bias)
            if best_score is None or score > best_score:
                best_score = score
                best = (dx, dy)
        else:
            # pursuer: minimize distance; prefer moves that move toward center less (i.e., stay aggressive),
            # and prefer more clearance to avoid obstacle traps.
            gap_pref = obstacle_gap(nx, ny)
            edge_pref = edge_dist(nx, ny)
            score = (-d, gap_pref + 0.01 * edge_pref, center_bias)
            if best_score is None or score > best_score:
                best_score = score
                best = (dx, dy)

    return [int(best[0]), int(best[1])]