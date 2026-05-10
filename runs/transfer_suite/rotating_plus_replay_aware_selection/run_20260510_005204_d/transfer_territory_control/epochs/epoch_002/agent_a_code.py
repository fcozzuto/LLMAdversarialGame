def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    self_territory = set(tuple(p) for p in observation.get("self_territory", []))
    opp_territory = set(tuple(p) for p in observation.get("opponent_territory", []))
    unclaimed = observation.get("unclaimed_cells", [])
    unclaimed_set = set(tuple(p) for p in unclaimed)
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    adj_dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = [0, 0]
    best_score = -10**18

    # Precompute nearest unclaimed distance heuristic values (small grid, OK).
    unclaimed_list = [tuple(p) for p in unclaimed] if unclaimed else []
    if unclaimed_list:
        # Deterministically pick a target to bias towards (min y then x for tie).
        target = min(unclaimed_list, key=lambda c: (abs(c[0]-sx)+abs(c[1]-sy), c[1], c[0]))
        tx, ty = target
    else:
        tx, ty = sx, sy

    opp_list = list(opp_territory)
    if opp_list:
        ocx = sum(p[0] for p in opp_list) / len(opp_list)
        ocy = sum(p[1] for p in opp_list) / len(opp_list)
    else:
        ocx, ocy = sx, sy

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue

        if (nx, ny) in opp_territory:
            score = 100000
        elif (nx, ny) in unclaimed_set:
            score = 900
        elif (nx, ny) in self_territory:
            score = 30
        else:
            score = 10

        # Frontier shaping: prefer expanding into unclaimed and creating contact with opponent.
        adj_un = 0
        adj_opp = 0
        adj_self = 0
        adj_obs = 0
        for ax, ay in adj_dirs:
            x2, y2 = nx + ax, ny + ay
            if 0 <= x2 < w and 0 <= y2 < h:
                if (x2, y2) in obstacles:
                    adj_obs += 1
                elif (x2, y2) in opp_territory:
                    adj_opp += 1
                elif (x2, y2) in unclaimed_set:
                    adj_un += 1
                elif (x2, y2) in self_territory:
                    adj_self += 1
        score += 35 * adj_un + 18 * adj_opp + 6 * adj_self - 8 * adj_obs

        # Deterministic targeting: move towards a chosen unclaimed cell and, secondarily, closer to opponent center.
        if unclaimed_list:
            score += -2 * (abs(nx - tx) + abs(ny - ty))
        score += -0.8 * (abs(nx - ocx) + abs(ny - ocy))

        # Tiny deterministic tie-break favoring forward-ish moves then lower y then x.
        score += -0.01 * (dx * dx + dy * dy) - 0.001 * (ny * 0.1 + nx * 0.01)

        if score > best_score:
            best_score = score
            best = [dx, dy]

    return [int(best[0]), int(best[1])]