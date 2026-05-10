def choose_move(observation):
    w = int(observation.get("grid_width", 0))
    h = int(observation.get("grid_height", 0))
    sx, sy = observation.get("self_position", (0, 0))
    obstacles = set(map(tuple, observation.get("obstacles") or []))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells") or []))
    self_terr = set(map(tuple, observation.get("self_territory") or []))
    opp_terr = set(map(tuple, observation.get("opponent_territory") or []))
    resources = observation.get("resources") or []

    dirs = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h
    def legal(x, y):
        return inb(x, y) and (x, y) not in obstacles

    def nearest_resource_dist(x, y):
        bestd = None
        for rx, ry in resources:
            d = abs(rx - x) + abs(ry - y)
            if bestd is None or d < bestd:
                bestd = d
        return bestd if bestd is not None else 10**9

    bx, by = sx, sy
    best_score = -10**18
    best_t = 10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        if (nx, ny) in opp_terr:
            score = 50
        elif (nx, ny) in unclaimed:
            score = 30
        elif (nx, ny) in self_terr:
            score = 10
        else:
            score = 0
        t = nearest_resource_dist(nx, ny)
        # Deterministic tie-break: prefer lower distance to resource, then lexicographic direction
        key_t = t
        if (score > best_score) or (score == best_score and key_t < best_t) or (score == best_score and key_t == best_t and (dx, dy) < (bx - sx, by - sy)):
            best_score = score
            best_t = key_t
            bx, by = nx, ny

    return [int(bx - sx), int(by - sy)]