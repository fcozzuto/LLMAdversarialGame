def choose_move(observation):
    turn = int(observation.get("turn_index", 0))
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))

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

    dirs = [(-1, -1), (0, -1), (1, -1),
            (-1,  0), (0,  0), (1,  0),
            (-1,  1), (0,  1), (1,  1)]

    def legal(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist(a, b, c, d):
        return abs(a - c) + abs(b - d)

    # Deterministic strategy:
    # 1) If a resource exists, move toward the closest resource with tie-breaker favoring moving away from opponent
    # 2) If no resource or after picking target, try to increase distance from opponent while staying legal
    best_move = (0, 0)
    best_score = -10**9

    # If there is a target resource, evaluate moves by closeness to resource and distance from opponent
    if resources:
        # choose target resource deterministically as closest to me; if tie, choose one with larger distance from opponent
        target = None
        min_d = 10**9
        max_od = -1
        for rx, ry in resources:
            d_me = dist(sx, sy, rx, ry)
            d_opp = dist(ox, oy, rx, ry)
            if d_me < min_d or (d_me == min_d and d_opp > max_od):
                min_d = d_me
                max_od = d_opp
                target = (rx, ry)
        tx, ty = target

        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            # score: closer to target is better; also push away from opponent
            d_me = dist(nx, ny, tx, ty)
            d_opp = dist(nx, ny, ox, oy)
            score = -d_me - d_opp * 0.5
            if score > best_score:
                best_score = score
                best_move = (dx, dy)
    else:
        # No resources: drift away from opponent as much as possible within bounds
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            d_opp = dist(nx, ny, ox, oy)
            score = d_opp
            if score > best_score:
                best_score = score
                best_move = (dx, dy)

    # Fallback: stay still if no legal move found
    dx, dy = best_move
    if not (0 <= sx + dx < w and 0 <= sy + dy < h) or (sx + dx, sy + dy) in obstacles:
        dx, dy = 0, 0
    return [dx, dy]