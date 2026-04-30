def choose_move(observation):
    sx, sy = observation["self_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if p is not None and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def step_towards(tx, ty):
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        if dx != 0 and dy != 0:
            return dx, dy
        if dx != 0:
            return dx, 0
        return 0, dy

    resources = []
    for p in (observation.get("resources") or []):
        if p is not None and len(p) >= 2:
            rx, ry = int(p[0]), int(p[1])
            if (rx, ry) not in obstacles:
                resources.append((rx, ry))

    ox, oy = observation["opponent_position"]
    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if resources:
        # Choose a deterministic target: minimum of (cheb*4 + manhattan)
        best = None
        bestv = None
        for rx, ry in resources:
            c = cheb(sx, sy, rx, ry)
            md = (sx - rx)
            if md < 0:
                md = -md
            td = (sy - ry)
            if td < 0:
                td = -td
            m = md + td
            v = c * 4 + m
            if bestv is None or v < bestv or (v == bestv and (rx < best[0] or (rx == best[0] and ry < best[1]))):
                bestv = v
                best = (rx, ry)
        tx, ty = best

        # Evaluate legal moves locally: minimize distance to target, maximize distance from opponent, avoid obstacles
        best_move = (0, 0)
        best_score = None
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            dist_to_t = cheb(nx, ny, tx, ty)
            dist_to_o = cheb(nx, ny, ox, oy)
            # Prefer diagonal if tied; deterministic via order already
            score = dist_to_t * 1000 - dist_to_o
            if best_score is None or score < best_score:
                best_score = score
                best_move = (dx, dy)
        return [int(best_move[0]), int(best_move[1])]

    # No resources: move to maximize distance from opponent, deterministically towards a far corner.
    corners = [(0, 0), (w - 1, h - 1), (0, h - 1), (w - 1, 0)]
    far_corner = None
    farv = None
    for cx, cy in corners:
        v = cheb(cx, cy, ox, oy)
        if farv is None or v > farv or (v == farv and (cx < far_corner[0] or (cx == far_corner[0] and cy < far_corner[1]))):
            farv = v
            far_corner = (cx, cy)
    tx, ty = far_corner

    best_move = (0, 0)
    best_score = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        dist_to_o = cheb(nx, ny,