def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = observation.get("obstacles", [])
    obs_set = set((p[0], p[1]) for p in obstacles)

    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def dist(a, b, c, d):
        dx = a - c
        dy = b - d
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx + dy

    if not resources:
        tx, ty = (w // 2, h // 2)
        best = None
        bestv = -10**9
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obs_set: continue
            v = -dist(nx, ny, tx, ty)
            if v > bestv or (v == bestv and (dx, dy) < best):
                bestv = v
                best = (dx, dy)
        return list(best if best is not None else (0, 0))

    opp_dists = {}
    for rx, ry in resources:
        opp_dists[(rx, ry)] = dist(ox, oy, rx, ry)

    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs_set:
            continue
        # Evaluate this move by how much closer we are to the best contested resource
        my_best = -10**18
        for i, (rx, ry) in enumerate(resources):
            myd = dist(nx, ny, rx, ry)
            oppd = opp_dists[(rx, ry)]
            # Prefer resources we're closer to; tie-break by smaller my distance and index
            v = (oppd - myd) * 10 - myd - i * 0.001
            if v > my_best:
                my_best = v
        # Small preference to reduce distance when contest score is similar
        total = my_best
        if total > best_val or (total == best_val and (dx, dy) < best_move):
            best_val = total
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]