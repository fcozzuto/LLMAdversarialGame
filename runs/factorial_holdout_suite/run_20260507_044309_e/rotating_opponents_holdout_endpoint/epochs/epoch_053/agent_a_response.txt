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

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # Pick a target resource where we are closer; otherwise the one with smallest opponent lead.
    best = None
    best_key = None
    for r in resources:
        sd = man((sx, sy), r)
        od = man((ox, oy), r)
        # Prefer resources we can secure (sd < od); break ties by larger od-sd and closer sd.
        secure = 1 if sd < od else 0
        key = (secure, (od - sd), -sd)
        if best_key is None or key > best_key:
            best_key = key
            best = r

    tx, ty = best

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_val = -10**18

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue

        self_d = man((nx, ny), (tx, ty))
        opp_d = man((ox, oy), (tx, ty))
        # Move to reduce our distance; also slightly increase chance to be ahead.
        # Deterministic tie-break: prefer fewer steps to target, then prefer moves that increase distance to nearest obstacle.
        nearest_obs = 0
        md = 10**9
        for oxp, oyp in obstacles:
            dd = abs(nx - oxp) + abs(ny - oyp)
            if dd < md:
                md = dd
        nearest_obs = md if obstacles else 999

        val = (-(self_d)) + (0.25 * (opp_d - self_d)) + (0.01 * nearest_obs)
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]