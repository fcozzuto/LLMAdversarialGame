def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]

    obstacles = observation.get("obstacles") or []
    blocked = set()
    for p in obstacles:
        if p and len(p) >= 2:
            blocked.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def ok(x, y):
        return inb(x, y) and (x, y) not in blocked

    resources = observation.get("resources") or []
    res = []
    for r in resources:
        if r and len(r) >= 2:
            res.append((int(r[0]), int(r[1])))
    if not res and "remaining_resource_count" in observation and observation["remaining_resource_count"]:
        res = []

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_dx, best_dy = 0, 0
    best_score = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        # Chebyshev distance to opponent
        d_opp = abs(nx - ox)
        t = abs(ny - oy)
        if t > d_opp:
            d_opp = t

        # Best (min) distance to any resource, if known
        if res:
            d_res = 10**9
            for rx, ry in res:
                d = abs(nx - rx)
                ty = abs(ny - ry)
                if ty > d:
                    d = ty
                if d < d_res:
                    d_res = d
                    if d_res == 0:
                        break
        else:
            d_res = 0

        # Light obstacle-avoidance
        near_block = 0
        for bx, by in blocked:
            if abs(bx - nx) <= 1 and abs(by - ny) <= 1:
                near_block += 1

        # Score: move toward resources (smaller d_res), away from opponent (larger d_opp)
        # Use scalar scoring to avoid tuple/int comparisons.
        score = (d_opp * 10) - (d_res * 6) - (near_block * 3) + (1 if (d_res == 0 and res) else 0) - (abs(dx) + abs(dy) * 0.1)
        if score > best_score:
            best_score = score
            best_dx, best_dy = dx, dy

    return [int(best_dx), int(best_dy)]