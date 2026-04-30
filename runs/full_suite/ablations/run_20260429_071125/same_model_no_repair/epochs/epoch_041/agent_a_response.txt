def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw, gh = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    if not resources:
        return [0, 0]

    def in_bounds(x, y):
        return 0 <= x < gw and 0 <= y < gh

    def dist(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def best_resource_for(px, py):
        best = None
        bestv = None
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            d = dist(px, py, rx, ry)
            # slight tie-break: prefer greater x then y deterministically
            v = d * 1000 + (rx * 8 + ry)
            if bestv is None or v < bestv:
                bestv = v
                best = (rx, ry)
        return best if best is not None else resources[0]

    opp_target = best_resource_for(ox, oy)

    # Choose our target as a resource that gives max advantage over opponent.
    best_t = None
    best_adv = None
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        du = dist(sx, sy, rx, ry)
        do = dist(ox, oy, rx, ry)
        # prefer closer to us and relatively farther from opponent
        adv = (do - du) * 10 - du
        if best_adv is None or adv > best_adv:
            best_adv = adv
            best_t = (rx, ry)
    if best_t is None:
        best_t = resources[0]
    tx, ty = best_t

    moves = [(-1,-1), (0,-1), (1,-1), (-1,0), (0,0), (1,0), (-1,1), (0,1), (1,1)]
    best_move = (0, 0)
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue

        du_before = dist(sx, sy, tx, ty)
        du_after = dist(nx, ny, tx, ty)

        # Encourage pushing opponent away from their current target.
        do_before = dist(sx, sy, opp_target[0], opp_target[1])
        do_after = dist(nx, ny, opp_target[0], opp_target[1])

        # If we can reach our target in one move, prioritize it strongly.
        win1 = 1 if du_after == 0 else 0

        # Small deterministic preference to reduce detours: keep dx closer to target direction.
        dir_x = 0 if tx == sx else (1 if tx > sx else -1)
        dir_y = 0 if ty == sy else (1 if ty > sy else -1)
        align = - (abs(dir_x - dx) + abs(dir_y - dy))

        # Penalize moving adjacent to obstacles (risk of getting boxed).
        obst_near = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                if (nx + ax, ny + ay) in obstacles:
                    obst_near += 1

        score = (du_before - du_after) * 20 + (do_after - do_before) * 12 + win1 * 100 + align * 1 - obst_near * 2
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]