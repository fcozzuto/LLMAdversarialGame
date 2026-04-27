def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    me = observation.get("self_position", [0, 0])
    opp = observation.get("opponent_position", [0, 0])
    sx, sy = int(me[0]), int(me[1])
    ox, oy = int(opp[0]), int(opp[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def legal(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    seed = int(observation.get("turn_index", 0))
    best_target = None
    best_gap = -10**9

    if resources:
        for rx, ry in resources:
            r = (rx, ry)
            d_me = dist((sx, sy), r)
            d_opp = dist((ox, oy), r)
            gap = d_opp - d_me  # positive => we are closer than opponent
            # Slightly prefer nearer resources when gaps tie
            score = gap * 100 - (d_me + d_opp)
            if score > best_gap:
                best_gap = score
                best_target = r

    if best_target is None:
        # No resources: maximize distance from opponent while staying legal
        best_move = (0, 0)
        best_val = -10**18
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            val = dist((nx, ny), (ox, oy))
            # deterministic tie-breaker
            val = val * 2 + ((nx * 17 + ny * 31 + seed) % 7) * 0.001
            if val > best_val:
                best_val = val
                best_move = (dx, dy)
        return [best_move[0], best_move[1]]

    tx, ty = best_target
    # Move one step toward the chosen target, but outbid opponent for that target:
    # choose move maximizing (d_opp(next)-d_me(next)) and avoiding dead-ends.
    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        d_me = dist((nx, ny), (tx, ty))
        d_opp = dist((ox, oy), (tx, ty))
        # We approximate opponent's next step impact by comparing our progress; keep it deterministic.
        prog = (dist((ox, oy), (tx, ty)) - d_me)  # positive if we reduce distance
        # Prefer moves that also increase distance from opponent slightly (space)
        space = dist((nx, ny), (ox, oy))
        # Avoid being trapped: count legal neighbors
        neigh = 0
        for ddx, ddy in dirs:
            ax, ay = nx + ddx, ny + ddy
            if legal(ax, ay):
                neigh += 1
        val = prog * 200 + space * 3 + neigh * 0.5 - d_me * 1.5
        val = val + ((nx * 23 + ny * 19 + seed) % 11) * 0.0001
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]