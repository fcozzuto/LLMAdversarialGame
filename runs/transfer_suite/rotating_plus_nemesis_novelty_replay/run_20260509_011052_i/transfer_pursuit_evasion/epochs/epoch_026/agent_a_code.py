def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]

    self_role = (observation.get("self_role") or "").lower()
    opp_role = (observation.get("opponent_role") or "").lower()
    i_am_evader = "evader" in self_role
    evade = i_am_evader

    def king_dist(x1, y1, x2, y2):
        dx = abs(x1 - x2)
        dy = abs(y1 - y2)
        return dx if dx > dy else dy

    def corner_score(x, y, to_far):
        if to_far:
            return max(abs(x - cx) + abs(y - cy) for cx, cy in corners)
        return -min(abs(x - cx) + abs(y - cy) for cx, cy in corners)

    best = (sx, sy)
    bestv = -10**18 if evade else 10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        d = king_dist(nx, ny, ox, oy)
        if evade:
            # keep away; also drift toward the corner farthest from pursuer
            v = d * 1000 + corner_score(nx, ny, True)
        else:
            # pursue; prefer moves that reduce king distance and "cut off" by favoring corners
            # opposite of where we want to push the evader (i.e., choose corner toward which pursuer can block)
            v = -d * 1000 + corner_score(nx, ny, False)  # closer to our target corner is slightly better
        if v > bestv:
            bestv = v
            best = (nx, ny)

    if best == (sx, sy):
        return [0, 0]
    return [best[0] - sx, best[1] - sy]