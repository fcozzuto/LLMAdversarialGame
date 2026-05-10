def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]

    self_terr = observation.get("self_territory", [])
    opp_terr = observation.get("opponent_territory", [])
    unclaimed = observation.get("unclaimed_cells", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    self_set = set(tuple(p) for p in self_terr)
    opp_set = set(tuple(p) for p in opp_terr)
    unclaimed_set = set(tuple(p) for p in unclaimed)

    dirs = [(-1,-1), (0,-1), (1,-1), (-1,0), (0,0), (1,0), (-1,1), (0,1), (1,1)]
    best = None
    best_score = -10**9

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue

        if (nx, ny) in opp_set:
            score = 100
        elif (nx, ny) in unclaimed_set:
            score = 40
        elif (nx, ny) in self_set:
            score = 5
        else:
            score = 0

        # Encourage moves that create/advance frontier; approximate by counting adjacent targets.
        adj_target = 0
        adj_opp = 0
        adj_un = 0
        for adx, ady in [(-1,-1),(0,-1),(1,-1),(-1,0),(1,0),(-1,1),(0,1),(1,1)]:
            ax, ay = nx + adx, ny + ady
            if ax < 0 or ax >= w or ay < 0 or ay >= h:
                continue
            if (ax, ay) in obstacles:
                continue
            if (ax, ay) in opp_set:
                adj_opp += 1
                adj_target += 1
            elif (ax, ay) in unclaimed_set:
                adj_un += 1
                adj_target += 1

        score += adj_target * 7 + adj_un * 2 + adj_opp * 3

        # Avoid drifting into safe territory if opponent is closer to taking unclaimed.
        dist_to_opp = abs(nx - ox) + abs(ny - oy)
        score += max(0, 20 - dist_to_opp) * 0.5

        # Deterministic tiebreak: prefer earlier dirs if same score.
        if score > best_score:
            best_score = score
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]