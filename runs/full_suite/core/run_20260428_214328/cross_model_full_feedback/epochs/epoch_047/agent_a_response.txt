def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    obst = set()
    for p in observation.get("obstacles", []) or []:
        if p is not None and len(p) >= 2:
            x = int(p[0]); y = int(p[1])
            if inside(x, y):
                obst.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if p is not None and len(p) >= 2:
            x = int(p[0]); y = int(p[1])
            if inside(x, y) and (x, y) not in obst:
                resources.append((x, y))

    def cheb(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    cur_res_left = int(observation.get("remaining_resource_count", len(resources)) or len(resources))

    best = (0, 0)
    best_score = -10**18

    # If few resources remain, weight racing the closest; otherwise, just improve toward resources.
    race_weight = 2.0 if cur_res_left <= max(3, len(resources) // 3 + 1) else 1.0
    opp_weight = 0.8

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obst:
            continue

        # Distance to nearest resource (we want to minimize)
        if resources:
            dmy = 10**9
            for rx, ry in resources:
                d = cheb(nx, ny, rx, ry)
                if d < dmy: dmy = d
        else:
            dmy = 0

        # Opportunity: compare our distance vs opponent's to nearest resource
        opp_closest = 10**9
        my_closest = 10**9
        if resources:
            for rx, ry in resources:
                om = cheb(ox, oy, rx, ry)
                mm = cheb(nx, ny, rx, ry)
                if mm < my_closest: my_closest = mm
                if om < opp_closest: opp_closest = om
        else:
            my_closest = 0; opp_closest = 0

        # Penalize being close to opponent (avoid being contested too early)
        d_op = cheb(nx, ny, ox, oy)

        # Reward being on/near resources; slight reward for reducing opponent advantage.
        score = 0.0
        score += -1.2 * dmy
        score += race_weight * (opp_closest - my_closest)  # positive when we are closer than opponent
        score += opp_weight * d_op

        # Deterministic tie-break: prefer moves with smaller (|dx|+|dy|), then favor toward resources direction
        man = abs(dx) + abs(dy)
        if score > best_score or (score == best_score and (man, dx, dy) < (abs(best[0]) + abs(best[1]), best[0], best[1])):
            best_score = score
            best = (dx, dy)

    return [int(best[0]), int(best[1])]