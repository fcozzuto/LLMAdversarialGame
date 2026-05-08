def choose_move(observation):
    w = int(observation.get("grid_width", 0) or 0)
    h = int(observation.get("grid_height", 0) or 0)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))

    obstacles = set(map(tuple, observation.get("obstacles") or []))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells") or []))
    self_t = set(map(tuple, observation.get("self_territory") or []))
    opp_t = set(map(tuple, observation.get("opponent_territory") or []))
    resources = set(map(tuple, observation.get("resources") or []))

    adj = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    targets = resources if resources else (unclaimed if unclaimed else [])
    tx, ty = (ox, oy)
    if targets:
        bestd = 10**18
        for px, py in targets:
            d = (sx - px) * (sx - px) + (sy - py) * (sy - py)
            if d < bestd:
                bestd = d
                tx, ty = px, py

    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in adj:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d = (nx - tx) * (nx - tx) + (ny - ty) * (ny - ty)
        score = -d

        if (nx, ny) in unclaimed:
            score += 5000
        if targets and any((nx + ddx, ny + ddy) in unclaimed for ddx, ddy in ((-1,0),(1,0),(0,-1),(0,1),(0,0),(-1,-1),(1,-1),(-1,1),(1,1))):
            score += 1200

        if (nx, ny) in opp_t:
            score -= 4000
        if (nx, ny) == (ox, oy):
            score -= 800

        if score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]