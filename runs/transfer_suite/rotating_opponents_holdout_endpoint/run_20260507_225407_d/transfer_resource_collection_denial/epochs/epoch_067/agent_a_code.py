def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))

    def inb(x, y): 
        return 0 <= x < w and 0 <= y < h

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        try:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                obs.add((x, y))
        except Exception:
            pass

    def ok(x, y):
        return inb(x, y) and (x, y) not in obs

    resources = []
    for p in observation.get("resources") or []:
        try:
            x, y = int(p[0]), int(p[1])
            if ok(x, y):
                resources.append((x, y))
        except Exception:
            pass

    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    def man(a, b, c, d): 
        return abs(a - c) + abs(b - d)

    if not resources or not ok(sx, sy):
        tx, ty = 3, 3
        bestm, bestv = [0, 0], -10**9
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny): 
                continue
            v = -man(nx, ny, tx, ty)
            if v > bestv:
                bestv, bestm = v, [dx, dy]
        return bestm

    # Pick the move that maximizes guaranteed advantage for any reachable resource.
    bestm, bestv = [0, 0], -10**9
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        # Deterministic: evaluate all resources and take the best "advantage" we can convert next.
        best_adv_here = -10**9
        for rx, ry in resources:
            sd = man(nx, ny, rx, ry)
            od = man(ox, oy, rx, ry)
            # Prefer resources where we arrive no later than opponent; break ties by shorter self distance.
            adv = (od - sd) * 1000 - sd
            if adv > best_adv_here:
                best_adv_here = adv
        # If all adv are bad, still prefer reducing distance to the closest resource we are nearest to.
        v = best_adv_here
        if v > bestv:
            bestv, bestm = v, [dx, dy]
    return bestm