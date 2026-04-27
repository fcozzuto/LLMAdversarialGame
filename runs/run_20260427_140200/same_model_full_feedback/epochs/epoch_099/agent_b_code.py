def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]

    def dist(a, b):
        dx = a[0] - b[0]
        if dx < 0: dx = -dx
        dy = a[1] - b[1]
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not resources:
        # chase opponent to contest space deterministically
        dx = 0 if ox == sx else (1 if ox > sx else -1)
        dy = 0 if oy == sy else (1 if oy > sy else -1)
        for mx, my in [(dx, dy), (dx, 0), (0, dy), (0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)]:
            nx, ny = sx + mx, sy + my
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                return [mx, my]
        return [0, 0]

    # Race heuristic: prefer moves that make us reach some resource sooner than opponent.
    best = None
    best_score = -10**18
    for mx, my in moves:
        nx, ny = sx + mx, sy + my
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue

        # For each resource, compute lead = (opp_dist - self_dist); larger is better.
        # Choose the resource giving maximum lead, then break ties by smaller self_dist.
        best_lead = -10**18
        best_self_d = 10**18
        for rx, ry in resources:
            rd = (rx, ry)
            sd = dist((nx, ny), rd)
            od = dist((ox, oy), rd)
            lead = od - sd
            if lead > best_lead or (lead == best_lead and sd < best_self_d):
                best_lead = lead
                best_self_d = sd

        # Additional pressure: slight penalty if we increase distance to opponent (less blocking).
        # Encourage diagonal unless blocked; deterministic via fixed move order already.
        self_opp_d = dist((nx, ny), (ox, oy))
        score = (best_lead * 1000) - (best_self_d * 3) + (self_opp_d * -1)

        if score > best_score:
            best_score = score
            best = [mx, my]

    if best is None:
        return [0, 0]
    return best