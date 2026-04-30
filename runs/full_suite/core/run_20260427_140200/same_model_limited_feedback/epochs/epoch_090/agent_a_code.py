def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def clamp(x, y):
        if x < 0: x = 0
        elif x >= w: x = w - 1
        if y < 0: y = 0
        elif y >= h: y = h - 1
        return x, y

    def dist(a, b):
        ax, ay = a
        bx, by = b
        dx = ax - bx
        dy = ay - by
        return (dx * dx + dy * dy) ** 0.5

    if not resources:
        # No resources: move away from opponent while staying legal
        best = (0, (0, 0))
        for dx, dy in moves:
            nx, ny = clamp(sx + dx, sy + dy)
            if (nx, ny) in obstacles:
                continue
            d = dist((nx, ny), (ox, oy))
            if d > best[0]:
                best = (d, (dx, dy))
        return [best[1][0], best[1][1]]

    # Preselect best resource by relative accessibility
    def res_value_from(pos):
        # maximize value: closer to me, farther from opponent
        bestv = -1e18
        bestpos = None
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            dv = -dist(pos, (rx, ry)) + 0.25 * dist((ox, oy), (rx, ry))
            if dv > bestv:
                bestv = dv
                bestpos = (rx, ry)
        return bestv, bestpos

    _, target = res_value_from((sx, sy))
    if target is None:
        target = resources[0]

    best_score = -1e18
    best_move = (0, 0)
    for dx, dy in moves:
        nx, ny = clamp(sx + dx, sy + dy)
        if (nx, ny) in obstacles:
            continue
        # Primary: reduce distance to chosen target
        d1 = dist((nx, ny), target)
        # Secondary: avoid giving opponent an easy grab (increase their distance)
        d2 = dist((nx, ny), (ox, oy))
        # Tertiary: small preference to approach any resource that becomes competitive
        v = -d1 + 0.05 * d2
        # Look at opponent relative closeness to target after move
        opp_d = dist((ox, oy), target)
        my_d = d1
        v += 0.2 * (opp_d - my_d)
        if v > best_score:
            best_score = v
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]