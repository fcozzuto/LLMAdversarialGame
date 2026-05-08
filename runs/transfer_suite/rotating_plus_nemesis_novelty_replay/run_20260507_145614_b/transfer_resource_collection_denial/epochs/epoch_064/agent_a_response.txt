def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def mdist(x1, y1, x2, y2):
        dx = x1 - x2; dx = dx if dx >= 0 else -dx
        dy = y1 - y2; dy = dy if dy >= 0 else -dy
        return dx if dx > dy else dy  # Chebyshev for diagonal-speed

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if not resources:
        tx, ty = w - 1, h - 1
        if (sx, sy) == (tx, ty): tx, ty = 0, 0
        dx = 0 if sx == tx else (1 if tx > sx else -1)
        dy = 0 if sy == ty else (1 if ty > sy else -1)
        return [dx, dy]

    if any((sx == r[0] and sy == r[1]) for r in resources):
        return [0, 0]

    best_move = [0, 0]
    best_val = -10**18

    for dxi, dyi in moves:
        nx, ny = sx + dxi, sy + dyi
        if not inb(nx, ny):
            nx, ny, dxi, dyi = sx, sy, 0, 0

        # Contest score: how much sooner (or later) we reach the best remaining resource.
        # Tie-break: prefer smaller own distance after maximizing lead.
        best_lead = -10**18
        best_own = 10**9
        for rx, ry in resources:
            myd = mdist(nx, ny, rx, ry)
            od = mdist(ox, oy, rx, ry)
            lead = od - myd  # positive is "we are closer"
            if lead > best_lead or (lead == best_lead and myd < best_own):
                best_lead, best_own = lead, myd

        # If we can't beat opponent on lead, still move toward the closest high-priority contested area.
        # Add a small bias to reduce distance to the currently "best" resource in lead space.
        opp_now = mdist(ox, oy, nx, ny)
        val = best_lead * 1000 - best_own - opp_now * 2

        # Secondary: don't step away from all resources (reward progress to nearest resource).
        nearest = 10**9
        for rx, ry in resources:
            d = mdist(nx, ny, rx, ry)
            if d < nearest: nearest = d
        val += -nearest

        if val > best_val:
            best_val = val
            best_move = [dxi, dyi]

    return best_move