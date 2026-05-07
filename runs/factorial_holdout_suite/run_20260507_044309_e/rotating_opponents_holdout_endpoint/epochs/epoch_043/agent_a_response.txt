def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [7, 7])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources_in = observation.get("resources", []) or []
    obstacles_in = observation.get("obstacles", []) or []

    resources = []
    for p in resources_in:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            resources.append((int(p[0]), int(p[1])))
    obstacles = set()
    for p in obstacles_in:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    if not resources:
        return [0, 0]

    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    moves.sort()

    # Pick a target resource to contest:
    # primary: our lead (opp_dist - self_dist) largest, secondary: nearer to us
    best_target = None
    best_lead = None
    for rx, ry in resources:
        sd = man(sx, sy, rx, ry)
        od = man(ox, oy, rx, ry)
        lead = od - sd
        key = (lead, -sd, -rx, -ry)
        if best_target is None or key > (best_lead, -999999999, -999999999, -999999999):
            # store exact comparison via explicit variables
            if best_target is None or (lead, -sd, -rx, -ry) > (best_lead, None, None, None):
                pass
        # do deterministic proper selection
    best_key = None
    for rx, ry in resources:
        sd = man(sx, sy, rx, ry)
        od = man(ox, oy, rx, ry)
        key = (od - sd, -sd, -rx, -ry)
        if best_key is None or key > best_key:
            best_key = key
            best_target = (rx, ry)

    tx, ty = best_target

    # If any move lands directly on a resource, take the best such resource immediately.
    landed_resources = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) in resources:
            sd = man(nx, ny, nx, ny)
            od = man(ox, oy, nx, ny)
            landed_resources.append(((od - sd), sd, -nx, -ny, (dx, dy)))
    if landed_resources:
        landed_resources.sort(reverse=True)
        return list(landed_resources[0][4])

    # Otherwise, greedily move to reduce distance to target, while also considering opponent pressure.
    best = None
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        my_d = man(nx, ny, tx, ty)
        opp_d = man(ox, oy, tx, ty)
        # Encourage staying closer to the contested resource relative to opponent.
        score = (-(my_d), (opp_d - my_d), -abs(nx - tx) - abs(ny - ty), -nx, -ny)
        if best_score is None or score > best_score:
            best_score = score
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]