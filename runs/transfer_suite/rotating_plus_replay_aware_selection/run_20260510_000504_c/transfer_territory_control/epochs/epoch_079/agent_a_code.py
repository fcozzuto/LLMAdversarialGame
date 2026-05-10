def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
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

    # If a resource exists, greedily move toward it deterministically.
    if resources:
        tx, ty = resources[0]
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        nx, ny = sx + dx, sy + dy
        if legal(nx, ny):
            return [dx, dy]
        # fallback: any legal step that reduces manhattan to resource
        best = (10**9, [0, 0])
        for a, b in dirs:
            nx, ny = sx + a, sy + b
            if not legal(nx, ny):
                continue
            d = abs(tx - nx) + abs(ty - ny)
            if d < best[0]:
                best = (d, [a, b])
        return best[1]

    # One-step lookahead to claim unclaimed / flip opponent territory while advancing toward frontiers.
    unclaimed_list = list(unclaimed)
    sample = unclaimed_list[:min(10, len(unclaimed_list))]  # deterministic prefix
    def frontier_dist(x, y):
        if not sample:
            return 0
        md = 10**9
        for ux, uy in sample:
            v = abs(ux - x) + abs(uy - y)
            if v < md:
                md = v
        return md

    best_score = -10**18
    best_move = [0, 0]
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        # immediate control gain heuristic
        if (nx, ny) in unclaimed:
            score = 6
        elif (nx, ny) in opp_terr:
            score = 5
        elif (nx, ny) in self_terr:
            score = 2
        else:
            score = 0
        # advance toward nearest unclaimed
        score -= 0.35 * frontier_dist(nx, ny)
        # slight preference to push outward (toward edges) to avoid getting boxed
        score += 0.05 * min(nx, w - 1 - nx, ny, h - 1 - ny) * -1
        # deterministic tie-break: lexicographic on move
        if score > best_score or (score == best_score and [dx, dy] < best_move):
            best_score = score
            best_move = [dx, dy]
    return best_move