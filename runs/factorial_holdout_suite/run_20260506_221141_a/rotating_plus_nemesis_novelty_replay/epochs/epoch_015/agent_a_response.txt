def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw = observation.get("grid_width", 8)
    gh = observation.get("grid_height", 8)

    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < gw and 0 <= y < gh:
                obs.add((x, y))

    resources = observation.get("resources", []) or []
    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < gw and 0 <= y < gh and (x, y) not in obs:
                res.append((x, y))
    if not res:
        return [0, 0]

    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1),
             (1, 1), (1, -1), (-1, 1), (-1, -1)]

    def md(a, b, c, d):
        return abs(a - c) + abs(b - d)

    def best_resource_for(pos):
        x, y = pos
        best = None
        bestv = -10**18
        for rx, ry in res:
            our_d = md(x, y, rx, ry)
            opp_d = md(ox, oy, rx, ry)
            # Prefer resources we can reach sooner; strongly deny those opponent is closer to.
            v = (opp_d - our_d) * 5 - our_d - (our_d == 0) * 20
            if best is None or v > bestv:
                bestv = v
                best = (rx, ry, our_d, opp_d)
        return best

    def inb(nx, ny):
        return 0 <= nx < gw and 0 <= ny < gh and (nx, ny) not in obs

    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        target = best_resource_for((nx, ny))
        rx, ry, our_d, opp_d = target
        # If opponent is closer, step toward that resource to deny/intercept.
        # Otherwise, race it.
        intercept_bias = 0
        if opp_d < our_d:
            intercept_bias = (opp_d - our_d) * 2 - md(nx, ny, rx, ry)
        score = (opp_d - our_d) * 10 - our_d + intercept_bias
        if (rx, ry) == (nx, ny):
            score += 50
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]