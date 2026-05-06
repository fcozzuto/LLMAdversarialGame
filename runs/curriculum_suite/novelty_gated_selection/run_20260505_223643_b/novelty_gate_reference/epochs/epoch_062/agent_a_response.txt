def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if (sx, sy) in resources:
        return [0, 0]
    if not resources:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # Target choice: prefer resources where we're closer than opponent, but not too far.
    best_res = resources[0]
    best_score = -10**9
    for r in resources:
        md = man((sx, sy), r)
        od = man((ox, oy), r)
        advantage = od - md  # positive if we are closer
        score = advantage * 10 - md  # deterministic tie-break via iteration order
        if score > best_score:
            best_score, best_res = score, r

    rx, ry = best_res
    my_dist0 = man((sx, sy), best_res)
    opp_dist0 = man((ox, oy), best_res)
    we_advantaged = (my_dist0 < opp_dist0)

    best_move = (0, 0)
    best_val = -10**9

    if we_advantaged:
        # Move to further reduce our distance while keeping the opponent farther from target.
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inside(nx, ny):
                continue
            md = man((nx, ny), best_res)
            od = man((ox, oy), best_res)
            val = (od - md) * 20 - md
            if val > best_val:
                best_val, best_move = val, (dx, dy)
    else:
        # If not advantaged, break symmetry: move to maximize distance from opponent while still progressing.
        # Prefer: maximize (minDistToResources? no), here use opponent distance and own progress to chosen target.
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inside(nx, ny):
                continue
            md_prog = man((nx, ny), best_res)
            oppd = man((nx, ny), (ox, oy))
            val = oppd * 2 - md_prog
            if val > best_val:
                best_val, best_move = val, (dx, dy)

    dx, dy = best_move
    return [int(dx), int(dy)]