def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    role = str(observation.get("self_role", "")).lower()
    pursuer = any(k in role for k in ("pursuer", "hunter", "chaser", "pursuit"))
    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    def nearest_obs_dist(nx, ny):
        if not obstacles:
            return 99
        md = 99
        for ax, ay in obstacles:
            d = cheb(nx, ny, ax, ay)
            if d < md:
                md = d
        return md

    def corner_bias(nx, ny):
        corners = ((0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1))
        best = cheb(nx, ny, corners[0][0], corners[0][1])
        for cx, cy in corners[1:]:
            d = cheb(nx, ny, cx, cy)
            if d < best:
                best = d
        return best

    best_move = (0, 0)
    if pursuer:
        best = -10**9
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            nd = cheb(nx, ny, ox, oy)
            # Primary: get closer to opponent; Secondary: keep away from corners; Tertiary: avoid obstacles.
            score = (-(nd * 1000)) + (corner_bias(nx, ny) * 10) + (nearest_obs_dist(nx, ny))
            if score > best:
                best = score
                best_move = (dx, dy)
    else:
        best = -10**9
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            nd = cheb(nx, ny, ox, oy)
            # Primary: maximize distance; Secondary: stay near corners (evasion); Tertiary: avoid obstacles.
            score = (nd * 1000) + (-(corner_bias(nx, ny)) * 10) + (nearest_obs_dist(nx, ny))
            if score > best:
                best = score
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]