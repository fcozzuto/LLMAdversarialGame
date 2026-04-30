def choose_move(observation):
    W = int(observation.get("grid_width", 8) or 8)
    H = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obs = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H:
                obs.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H and (x, y) not in obs:
                resources.append((x, y))

    moves = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0), (-1, -1), (-1, 1), (1, -1), (1, 1)]

    def man(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx + dy

    def legal(nx, ny):
        return 0 <= nx < W and 0 <= ny < H and (nx, ny) not in obs

    if not resources:
        # Drift away from opponent to reduce interference, but avoid obstacles.
        best = (0, 0)
        bestv = -10**18
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            v = -man(nx, ny, ox, oy)
            # Prefer edges less (deterministic tie-break via coordinate)
            v += -0.01 * (nx * nx + ny * ny)
            if v > bestv:
                bestv, best = v, (dx, dy)
        return [best[0], best[1]]

    my_best_res = None
    # Evaluate each move by how much it improves our chance to be first at some resource.
    best = (0, 0)
    bestv = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        score = -10**18
        for rx, ry in resources:
            md = man(nx, ny, rx, ry)
            od = man(ox, oy, rx, ry)
            # Strong preference for resources we can reach no later than opponent.
            if md <= od:
                v = 1000 - md * 10 - od
            else:
                # If we're late, prioritize minimizing the gap and cutting it fast.
                v = - (md - od) * 30 - md
            # Deterministic tie-break: slight bias toward resources with smaller coords.
            v += -0.001 * (rx + 3 * ry)
            if v > score:
                score = v
                my_best_res = (rx, ry)
        # Extra discouragement for moving into proximity of opponent (keeps us less contested).
        score += -0.02 * man(nx, ny, ox, oy)
        if score > bestv:
            bestv, best = score, (dx, dy)
    return [best[0], best[1]]