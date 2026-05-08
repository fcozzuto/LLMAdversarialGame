def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        try:
            obs.add((p[0], p[1]))
        except:
            pass

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def free(x, y):
        return inb(x, y) and (x, y) not in obs

    def dist(a, b):
        dx = a[0] - b[0]
        if dx < 0: dx = -dx
        dy = a[1] - b[1]
        if dy < 0: dy = -dy
        return dx if dx > dy else dy  # Chebyshev

    dirs = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    # If no resources visible, drift toward best corner away from opponent to reduce interference.
    if not resources:
        corners = [(0,0),(0,h-1),(w-1,0),(w-1,h-1)]
        tx, ty = min(corners, key=lambda c: dist(c, (ox, oy)))
        best = (-10**9, (0,0))
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not free(nx, ny):
                nx, ny = sx, sy
            # prefer increasing distance from opponent while moving toward chosen corner
            v = dist((nx, ny), (ox, oy)) - dist((nx, ny), (tx, ty))
            if v > best[0]:
                best = (v, (dx, dy))
        return [best[1][0], best[1][1]]

    best_move = (0, 0)
    best_val = -10**18

    # Deterministic: score candidate cell by best resource "race" advantage.
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            nx, ny = sx, sy

        my_pos = (nx, ny)
        # Also discourage getting closer to opponent if tied on resource race.
        opp_threat = dist(my_pos, (ox, oy))

        # For each resource, compute advantage = opp_dist - my_dist; larger means we arrive first/safer.
        # Penalize far resources to keep movement purposeful.
        best_resource = -10**18
        for r in resources:
            rpos = (r[0], r[1])
            md = dist(my_pos, rpos)
            od = dist((ox, oy), rpos)
            # Weighted to prefer first arrival, then closeness.
            val = (od - md) * 100 - md
            if val > best_resource:
                best_resource = val

        # Combine: primary best_resource, secondary prefer smaller threat (larger distance).
        v = best_resource + opp_threat * 0.1
        if v > best_val:
            best_val = v
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]