def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    resources = []
    for p in observation.get("resources", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            resources.append((int(p[0]), int(p[1])))
    if not resources:
        return [0, 0]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def obs_pen(nx, ny):
        if (nx, ny) in obstacles:
            return 10**6
        # mild penalty if adjacent to obstacle to reduce pathing into dead ends
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if (nx + dx, ny + dy) in obstacles:
                    return 6
        return 0

    deltas = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    best_move = (0, 0)
    best_score = -10**18

    # Score moves by immediate advantage in "nearest resource race", with obstacle-aware damping
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        p_self = obs_pen(nx, ny)

        # compute our and opponent's nearest-resource distances
        best_adv = None
        best_dist = None
        for rx, ry in resources:
            sd = man(nx, ny, rx, ry)
            od = man(ox, oy, rx, ry)
            adv = (od - sd)  # positive means we are closer
            if best_adv is None or (adv > best_adv) or (adv == best_adv and sd < best_dist):
                best_adv = adv
                best_dist = sd

        # also discourage giving opponent a huge lead elsewhere: penalize their best-minus-ours
        worst_gift = 0
        for rx, ry in resources:
            sd0 = man(nx, ny, rx, ry)
            od0 = man(ox, oy, rx, ry)
            gift = sd0 - od0  # negative => we are behind
            if gift < worst_gift:
                worst_gift = gift

        score = 100 * best_adv - 2 * best_dist + 1.5 * worst_gift - p_self
        # tiny deterministic tie-break toward not moving too far from current direction (prefers closer Manhattan to any resource)
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]