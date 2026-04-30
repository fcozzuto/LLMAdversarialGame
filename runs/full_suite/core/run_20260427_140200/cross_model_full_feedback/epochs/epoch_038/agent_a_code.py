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

    def md(a, b, c, d):
        return abs(a - c) + abs(b - d)

    def move_score(nx, ny):
        if resources:
            # Prefer grabbing/contesting a resource we can reach sooner than opponent.
            best = -10**9
            closest = 10**9
            for rx, ry in resources:
                d_me = md(nx, ny, rx, ry)
                d_opp = md(ox, oy, rx, ry)
                if d_me < closest:
                    closest = d_me
                # Large reward if we are closer than opponent to same resource.
                k = (d_opp - d_me)
                # Slight preference for reducing our absolute distance once contest is lost.
                if k > best:
                    best = k
            # Combine: contest strength, then tie-break by closeness; also keep some distance from opponent.
            return 10.0 * best - 1.5 * closest + 0.15 * md(nx, ny, ox, oy)
        # No resources: move to maximize distance from opponent while drifting toward center.
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        return 2.0 * md(nx, ny, ox, oy) - 0.02 * (abs(nx - cx) + abs(ny - cy))

    best_move = [0, 0]
    best_val = -10**18
    # Deterministic tie-break: fixed dir order.
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        val = move_score(nx, ny)
        if val > best_val:
            best_val = val
            best_move = [dx, dy]
    return [int(best_move[0]), int(best_move[1])]