def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in (observation.get("resources") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles
    def dist_m(a, b):
        dx = a[0] - b[0]
        if dx < 0: dx = -dx
        dy = a[1] - b[1]
        if dy < 0: dy = -dy
        return dx + dy
    def adj_obs(x, y):
        c = 0
        for dx, dy in [(-1,0),(1,0),(0,-1),(0,1),(-1,-1),(1,1),(-1,1),(1,-1)]:
            nx, ny = x + dx, y + dy
            if (nx, ny) in obstacles:
                c += 1
        return c

    if not resources:
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if ok(nx, ny):
                return [dx, dy]
        return [0, 0]

    # Contest-focused: prefer resources where we can beat the opponent by a margin after moving.
    best = (0, 0)
    bestv = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        my_pos = (nx, ny)
        # Score is higher when (a) we are close to the best target and (b) opponent is farther for that target.
        local_best = -10**18
        for r in resources:
            dm = dist_m(my_pos, r)
            do = dist_m((ox, oy), r)
            # Encourage immediate pick-up strongly.
            pick = 5000 if (nx, ny) == r else 0
            # Encourage taking contested spots; penalize when opponent is closer.
            contest = (do - dm) * 120
            # Small regularizer: avoid moving into "tight" obstacle-adjacent areas.
            tight = -10 * adj_obs(nx, ny)
            v = pick + contest - dm * 18 + tight
            if v > local_best:
                local_best = v
        # If tie, prefer smaller distance-to-opponent (more disruption) then deterministic dx/dy order.
        tie_key = (local_best, -(dist_m(my_pos, (ox, oy))), -abs(dx), -abs(dy))
        if bestv is None or tie_key > bestv:
            bestv = tie_key
            best = (dx, dy)

    return [int(best[0]), int(best[1])]