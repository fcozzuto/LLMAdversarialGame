def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    self_role = (observation.get("self_role") or "").lower()
    opp_role = (observation.get("opponent_role") or "").lower()
    i_am_pursuer = ("pursuer" in self_role) or (("evader" not in self_role) and ("pursuer" not in opp_role))

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def legal(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs

    def dist2(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        return dx * dx + dy * dy

    def corner_score(x, y):
        corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        return max(dist2(x, y, cx, cy) for cx, cy in corners)

    best_dxdy = (0, 0)
    if i_am_pursuer:
        best = -10**18
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            d = dist2(nx, ny, ox, oy)
            # Encourage closing distance, discourage stepping into obstacle-adjacent traps.
            adj_block = 0
            for ddx, ddy in deltas:
                ax, ay = nx + ddx, ny + ddy
                if 0 <= ax < w and 0 <= ay < h and (ax, ay) in obs:
                    adj_block += 1
            val = -d - 2.0 * adj_block
            # Tie-break deterministically toward more "forward" motion.
            val += 1e-6 * (dx * dx + dy * dy)
            if val > best:
                best = val
                best_dxdy = (dx, dy)
    else:
        best = -10**18
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            d = dist2(nx, ny, ox, oy)
            # Evader wants distance; also avoid getting boxed by obstacles.
            adj_block = 0
            free_nei = 0
            for ddx, ddy in deltas:
                ax, ay = nx + ddx, ny + ddy
                if 0 <= ax < w and 0 <= ay < h and (ax, ay) not in obs:
                    free_nei += 1
                if 0 <= ax < w and 0 <= ay < h and (ax, ay) in obs:
                    adj_block += 1
            val = d + 1.5 * corner_score(nx, ny) + 0.3 * free_nei - 2.0 * adj_block
            val += 1e-6 * (dx * dx + dy * dy)
            if val > best:
                best = val
                best_dxdy = (dx, dy)

    dx, dy = best_dxdy
    return [int(dx), int(dy)]