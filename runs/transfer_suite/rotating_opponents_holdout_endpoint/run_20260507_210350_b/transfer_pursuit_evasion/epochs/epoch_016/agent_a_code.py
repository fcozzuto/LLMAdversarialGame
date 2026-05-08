def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    role = str(observation.get("self_role", "")).lower()
    pursuer = ("pursuer" in role) or ("hunter" in role) or ("chaser" in role) or ("pursuit" in role)
    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def min_obs_dist(x, y):
        md = 10**9
        for ax, ay in obstacles:
            d = cheb(x, y, ax, ay)
            if d < md: md = d
        return md if obstacles else 99

    # corners away/towards depending on role
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    if pursuer:
        # chase; slightly prefer moves that improve distance and reduce obstacle proximity
        best = None
        best_key = None
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            dist = cheb(nx, ny, ox, oy)
            md = min_obs_dist(nx, ny)
            # primary: minimize dist, secondary: maximize md, tertiary: deterministic order
            key = (dist, -md, dx, dy)
            if best_key is None or key < best_key:
                best_key = key
                best = [dx, dy]
        return best if best is not None else [0, 0]
    else:
        # evade; maximize distance from pursuer, avoid obstacles, prefer corners that are farthest from opponent
        target = max(corners, key=lambda c: cheb(c[0], c[1], ox, oy))
        best = None
        best_key = None
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            dist_to_opp = cheb(nx, ny, ox, oy)
            md = min_obs_dist(nx, ny)
            # also move towards the selected farthest corner only if it doesn't reduce safety too much
            dist_to_target = cheb(nx, ny, target[0], target[1])
            cur_to_target = cheb(sx, sy, target[0], target[1])
            progress = cur_to_target - dist_to_target  # positive is good
            key = (-dist_to_opp, -md, dist_to_target, -progress, dx, dy)
            if best_key is None or key < best_key:
                best_key = key
                best = [dx, dy]
        return best if best is not None else [0, 0]