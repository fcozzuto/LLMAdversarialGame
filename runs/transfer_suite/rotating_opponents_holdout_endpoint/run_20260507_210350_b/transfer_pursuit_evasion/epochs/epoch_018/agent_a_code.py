def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    role = str(observation.get("self_role", "")).lower()
    pursuer = any(k in role for k in ("pursuer", "hunter", "chaser", "pursuit"))

    deltas = [(-1, -1), (-1, 0), (-1, 1),
              (0, -1), (0, 0), (0, 1),
              (1, -1), (1, 0), (1, 1)]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def min_obs_dist(x, y):
        md = 10**9
        for ax, ay in obstacles:
            d = cheb(x, y, ax, ay)
            if d < md: md = d
        return md if md != 10**9 else 99

    def corners_far(cx, cy):
        corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        best = corners[0]
        bestv = -10**9
        for c in corners:
            v = cheb(cx, cy, c[0], c[1])
            if v > bestv:
                bestv = v
                best = c
        return best

    target_corner = corners_far(ox, oy)  # used mainly when evading
    best_move = (0, 0)
    if pursuer:
        best_score = 10**18
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            d = cheb(nx, ny, ox, oy)
            obs_d = min_obs_dist(nx, ny)
            # minimize distance to opponent; also prefer being away from obstacles
            score = d * 1000 - obs_d
            if score < best_score:
                best_score = score
                best_move = (dx, dy)
    else:
        # evade: maximize distance to opponent; also prefer moving toward open "corner" escape
        best_score = -10**18
        tcx, tcy = target_corner
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            d = cheb(nx, ny, ox, oy)
            obs_d = min_obs_dist(nx, ny)
            to_corner = cheb(nx, ny, tcx, tcy)
            # prioritize distance; add support for reaching the corner while keeping away from obstacles
            score = d * 1000 + obs_d * 10 + to_corner
            if score > best_score:
                best_score = score
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]