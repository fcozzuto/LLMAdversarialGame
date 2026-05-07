def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set(map(tuple, observation.get("obstacles") or []))

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def blocked(x, y): return (x, y) in obstacles or not inb(x, y)
    def md(x1, y1, x2, y2): 
        return abs(x1 - x2) + abs(y1 - y2)

    dirs = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    if not resources:
        tx, ty = w // 2, h // 2
        best = [0, 0]; bestv = -10**18
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if blocked(nx, ny): 
                continue
            v = -(md(nx, ny, tx, ty))
            if v > bestv:
                bestv, best = v, [dx, dy]
        return best

    best = [0, 0]; bestv = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if blocked(nx, ny): 
            continue

        v = -10**12
        # Evaluate best reachable resource this step; reward winning races.
        for rx, ry in resources:
            sd = md(nx, ny, rx, ry)
            od = md(ox, oy, rx, ry)
            # Bigger is better: prefer cells where we can arrive no later than opponent.
            race = (od - sd)  # positive if we are closer
            # If we can collect now, make it dominant.
            if sd == 0:
                cell_score = 10**9
            else:
                # Encourage getting closer and denying resources closer to opponent.
                cell_score = 1000 * race - 10 * sd + 2 * od
            if cell_score > v:
                v = cell_score

        # Deterministic tie-break by dirs iteration order already.
        if v > bestv:
            bestv, best = v, [dx, dy]

    return best