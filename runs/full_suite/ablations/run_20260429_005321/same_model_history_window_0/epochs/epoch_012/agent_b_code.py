def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    # Candidate target: resource where we are relatively closest vs opponent.
    best = None
    bestv = -10**9
    for rx, ry in resources:
        dS = abs(rx - sx) + abs(ry - sy)
        dO = abs(rx - ox) + abs(oy - ry)
        v = (dO - dS) * 10 - dS  # prioritize being ahead, then shorter path
        if best is None or v > bestv or (v == bestv and dS < bestdS):
            best = (rx, ry)
            bestv = v
            bestdS = dS

    # If no resources known, move to maximize distance from opponent (deterministic).
    if best is None:
        cand = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
        bestm = (0, 0)
        bestscore = -10**9
        for dx, dy in cand:
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                score = (abs(nx - ox) + abs(ny - oy))
                if score > bestscore:
                    bestscore = score
                    bestm = (dx, dy)
        return [bestm[0], bestm[1]]

    tx, ty = best
    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    # Choose move minimizing distance to target while avoiding obstacles and not giving ground to opponent.
    bestm = (0, 0)
    bestscore = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        dT = max(abs(tx - nx), abs(ty - ny))  # Chebyshev handles diagonals
        dO = abs(nx - ox) + abs(ny - oy)
        # Higher is better: closer to target, farther from opponent
        score = -dT * 1000 + dO - (dx == 0 and dy == 0) * 2
        if bestscore is None or score > bestscore:
            bestscore = score
            bestm = (dx, dy)

    # Fallback if all moves blocked by obstacles: allow staying or ignore obstacle filtering.
    if bestscore is None:
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h:
                dT = max(abs(tx - nx), abs(ty - ny))
                dO = abs(nx - ox) + abs(ny - oy)
                score = -dT * 1000 + dO
                if bestscore is None or score > bestscore:
                    bestscore = score
                    bestm = (dx, dy)

    return [int(bestm[0]), int(bestm[1])]