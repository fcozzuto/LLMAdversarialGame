def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def king_dist(x1, y1, x2, y2):
        dx = abs(x1 - x2)
        dy = abs(y1 - y2)
        return dx if dx >= dy else dy

    def cell_ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    # deterministic tie-break order: fixed deltas list as above

    best = None
    best_score = -10**18
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not cell_ok(nx, ny):
            continue

        # evaluate after making this move: prioritize resources where we gain tempo vs opponent
        local = 0
        min_self = 10**9
        min_opp = 10**9
        for rx, ry in resources:
            sd = king_dist(nx, ny, rx, ry)
            od = king_dist(ox, oy, rx, ry)
            min_self = sd if sd < min_self else min_self
            min_opp = od if od < min_opp else min_opp
            # stronger push for resources where opponent is relatively farther; smaller is better
            local += (od - sd) * 10 - sd

        # obstacle avoidance: prefer moves that keep more surrounding space
        neigh = 0
        for adx in (-1, 0, 1):
            for ady in (-1, 0, 1):
                if adx == 0 and ady == 0:
                    continue
                x2, y2 = nx + adx, ny + ady
                if cell_ok(x2, y2):
                    neigh += 1

        # mix objectives: if close to any resource, prioritize that path; also keep opponent pressure
        score = local + neigh * 3 + (min_opp - min_self) * 15
        if score > best_score:
            best_score = score
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]