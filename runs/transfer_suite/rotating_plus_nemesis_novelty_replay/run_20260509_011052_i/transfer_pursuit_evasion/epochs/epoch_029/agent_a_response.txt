def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist_score(x, y, tx, ty):
        dx = abs(x - tx)
        dy = abs(y - ty)
        return dx if dx > dy else dy  # Chebyshev

    self_role = (observation.get("self_role") or "").lower()
    opp_role = (observation.get("opponent_role") or "").lower()
    i_am_evader = "evader" in self_role and "pursuer" not in self_role
    i_am_pursuer = "pursuer" in self_role

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    if i_am_evader and not i_am_pursuer:
        target_corner = max(corners, key=lambda c: abs(c[0] - ox) + abs(c[1] - oy))
        best = (sx, sy)
        bestv = -10**9
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            d_to_opp = dist_score(nx, ny, ox, oy)
            # Prefer increasing distance, and heading away via corner drift; slight tie-break by staying closer to far corner
            v = (d_to_opp * 1000) + (abs(target_corner[0] - nx) + abs(target_corner[1] - ny))
            if v > bestv:
                bestv = v
                best = (nx, ny)
        return [best[0] - sx, best[1] - sy]

    # Default: pursue if possible; otherwise also behave like evader if role ambiguity
    if i_am_pursuer or ("pursuer" not in self_role and "evader" not in self_role):
        best = (sx, sy)
        bestv = 10**9
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            d_to_opp = dist_score(nx, ny, ox, oy)
            if d_to_opp < bestv:
                bestv = d_to_opp
                best = (nx, ny)
        return [best[0] - sx, best[1] - sy]

    # Fallback evade behavior
    target_corner = max(corners, key=lambda c: abs(c[0] - ox) + abs(c[1] - oy))
    best = (sx, sy)
    bestv = -10**9
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d_to_opp = dist_score(nx, ny, ox, oy)
        v = (d_to_opp * 1000) + (abs(target_corner[0] - nx) + abs(target_corner[1] - ny))
        if v > bestv:
            bestv = v
            best = (nx, ny)
    return [best[0] - sx, best[1] - sy]