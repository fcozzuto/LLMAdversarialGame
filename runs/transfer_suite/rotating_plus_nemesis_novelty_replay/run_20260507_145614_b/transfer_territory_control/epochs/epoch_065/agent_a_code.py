def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if p and len(p) >= 2:
            x, y = p[0], p[1]
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    unclaimed = []
    for p in (observation.get("unclaimed_cells") or []):
        if p and len(p) >= 2:
            x, y = p[0], p[1]
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                unclaimed.append((x, y))

    opp_set = set()
    for p in (observation.get("opponent_territory") or []):
        if p and len(p) >= 2:
            x, y = p[0], p[1]
            if 0 <= x < w and 0 <= y < h:
                opp_set.add((x, y))

    def neigh4(x, y):
        for dx, dy in ((1,0),(-1,0),(0,1),(0,-1)):
            nx, ny = x + dx, y + dy
            if 0 <= nx < w and 0 <= ny < h:
                yield nx, ny

    # Target selection: prioritize unclaimed adjacent (4-neigh) to opponent, else best unclaimed overall, else stay.
    best_t = None
    best_adj = -10**9
    for (x, y) in unclaimed:
        adj = 0
        for nx, ny in neigh4(x, y):
            if (nx, ny) in opp_set:
                adj += 1
        # tie-break: closer to us
        cand_adj = adj * 1000 - (abs(x - sx) + abs(y - sy))
        if cand_adj > best_adj:
            best_adj = cand_adj
            best_t = (x, y)

    if best_t is None:
        return [0, 0]
    tx, ty = best_t

    deltas = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    best_move = (0, 0)
    best_val = 10**18
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue  # avoid obstacle, engine would otherwise waste move
        # Heuristic: go to target, slightly prefer moves that are nearer to opponent boundary if adjacent
        dist = abs(nx - tx) + abs(ny - ty)
        opp_adj = 0
        for ax, ay in neigh4(nx, ny):
            if (ax, ay) in opp_set:
                opp_adj += 1
        val = dist - opp_adj * 2
        if val < best_val:
            best_val = val
            best_move = (dx, dy)

    dx, dy = best_move
    return [int(dx), int(dy)]