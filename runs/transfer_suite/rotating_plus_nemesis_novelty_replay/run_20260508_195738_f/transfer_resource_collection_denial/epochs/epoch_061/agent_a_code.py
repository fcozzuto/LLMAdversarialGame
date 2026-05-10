def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles", []) or []))
    resources = [(int(r[0]), int(r[1])) for r in (observation.get("resources", []) or [])]

    def cheb(x1, y1, x2, y2):
        dx = abs(x1 - x2)
        dy = abs(y1 - y2)
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        # retreat to keep control near opponent: go to corner farthest from opponent but valid
        corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        tx, ty = max(corners, key=lambda c: cheb(c[0], c[1], ox, oy))
        best, bestm = -10**9, (0, 0)
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            score = -cheb(nx, ny, tx, ty)
            if score > best:
                best, bestm = score, (dx, dy)
        return [bestm[0], bestm[1]]

    resset = set(resources)
    best_score, best_move = -10**18, (0, 0)
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        if (nx, ny) in resset:
            score = 1e9
        else:
            score = 0.0
            for (rx, ry) in resources:
                d_me = cheb(nx, ny, rx, ry)
                d_op = cheb(ox, oy, rx, ry)
                # Prefer landing where we can be <= opponent; stronger preference for closer resources.
                if d_me <= d_op:
                    score += (d_op - d_me + 1) * (10.0 / (1 + d_me))
                else:
                    score -= (d_me - d_op) * (2.0 / (1 + d_me))
            # Mild anti-collision/anti-trap: discourage moving adjacent to obstacles heavily
            adj_pen = 0.0
            for ex in (-1, 0, 1):
                for ey in (-1, 0, 1):
                    ax, ay = nx + ex, ny + ey
                    if (ax, ay) in obstacles:
                        adj_pen += 0.3
            score -= adj_pen
            # Small tie-break toward reducing distance to opponent when we are behind on most resources
            score -= 0.01 * cheb(nx, ny, ox, oy)
        if score > best_score:
            best_score, best_move = score, (dx, dy)
    return [int(best_move[0]), int(best_move[1])]