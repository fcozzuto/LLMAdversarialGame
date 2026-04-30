def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if valid(nx, ny):
                moves.append((dx, dy))
    if not moves:
        return [0, 0]

    if not resources:
        # Drift away from opponent but keep deterministic obstacle-robustness via scoring neighbors.
        best = None; bestv = -10**18
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            v = cheb(nx, ny, ox, oy)
            if v > bestv:
                bestv = v; best = (dx, dy)
        return [best[0], best[1]] if best is not None else [0, 0]

    # For each move, maximize "resource advantage" after the move.
    # Advantage favors resources we are closer to than opponent; tie-break toward nearer ds.
    best = None; bestv = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        top_adv = -10**18
        top_ds = 10**18
        # Optional small bias: prefer moving toward the opponent when we are far behind (to contest).
        for rx, ry in resources:
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            adv = do - ds
            if adv > top_adv or (adv == top_adv and ds < top_ds):
                top_adv = adv; top_ds = ds
        # If we can't get positive advantage, still move toward the closest contested resource.
        # Bias discourages long detours by adding a small penalty on ds.
        v = top_adv * 1000 - top_ds
        if v > bestv:
            bestv = v; best = (dx, dy)
        elif v == bestv and best is not None:
            # Deterministic tie-break: prefer staying if possible, then lexicographic.
            if (dx, dy) == (0, 0) and best != (0, 0):
                best = (dx, dy)
            elif (dx, dy) < best:
                best = (dx, dy)

    return [best[0], best[1]] if best is not None else [0, 0]