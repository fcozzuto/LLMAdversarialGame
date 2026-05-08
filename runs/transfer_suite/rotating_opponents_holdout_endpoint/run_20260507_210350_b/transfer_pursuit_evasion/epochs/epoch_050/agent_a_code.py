def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])

    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    rolestr = (observation.get("self_role", "") or "").lower()
    is_evader = any(k in rolestr for k in ("evader", "escape", "flee", "runner"))

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def valid(x, y):
        return inb(x, y) and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x2 - x1
        if dx < 0:
            dx = -dx
        dy = y2 - y1
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def edge_dist(x, y):
        a = x
        b = w - 1 - x
        c = y
        d = h - 1 - y
        m = a if a < b else b
        m = m if m < c else c
        m = m if m < d else d
        return m

    def min_obs_dist(x, y):
        if not obstacles:
            return 10
        best = 10
        for ax, ay in obstacles:
            d = cheb(x, y, ax, ay)
            if d < best:
                best = d
        return best

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    tcx, tcy = max(corners, key=lambda p: cheb(p[0], p[1], ox, oy))

    best_move = (0, 0)
    best_score = -10**18 if not is_evader else -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        dist_opp = cheb(nx, ny, ox, oy)
        od = min_obs_dist(nx, ny)
        ed = edge_dist(nx, ny)

        if is_evader:
            corner_pull = cheb(nx, ny, tcx, tcy)
            score = dist_opp + 0.35 * ed + 0.6 * od - 0.25 * corner_pull
        else:
            # pursuer: move to reduce distance, but keep away from obstacles
            rowcol_toward = 0
            if nx == ox or ny == oy:
                rowcol_toward = 1
            score = -dist_opp + 0.45 * od + 0.06 * rowcol_toward - 0.05 * ed

        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]