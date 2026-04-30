def choose_move(observation):
    w = int(observation["grid_width"]); h = int(observation["grid_height"])
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def valid(x, y): return inb(x, y) and (x, y) not in obstacles
    def cheb(x1, y1, x2, y2):
        dx = x1 - x2; dy = y1 - y2
        return abs(dx) if abs(dx) > abs(dy) else abs(dy)

    if not valid(sx, sy):
        return [0, 0]

    if not resources:
        best = (None, -10**9)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny): 
                continue
            dO = cheb(nx, ny, ox, oy)
            # drift away from opponent if no resources exist
            sc = (dO * 2) - cheb(nx, ny, 0, h-1) * 0.0
            if sc > best[1]:
                best = ((dx, dy), sc)
        return [best[0][0], best[0][1]] if best[0] else [0, 0]

    best_target = None
    best_gap = -10**18
    for rx, ry in resources:
        if not valid(rx, ry):
            continue
        dS = cheb(sx, sy, rx, ry)
        dO = cheb(ox, oy, rx, ry)
        # Prefer resources where we are faster than opponent (positive gap)
        gap = (dO - dS) * 10
        # Slightly prefer closer resources once gap is similar
        tie = -dS
        # Encourage attacking the opponent's "race": if very close tie, prefer nearer to win
        epsilon = 0
        score = gap + tie + epsilon
        if score > best_gap:
            best_gap = score
            best_target = (rx, ry)

    if best_target is None:
        return [0, 0]
    tx, ty = best_target

    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        dT = cheb(nx, ny, tx, ty)
        dTO = cheb(ox + 0, oy + 0, tx, ty)  # static opponent->target distance
        dO_next = cheb(nx, ny, ox, oy)

        # Core: decrease distance to target
        sc = -dT * 8
        # If this move is also improving our lead vs opponent on the target, reward
        # (Opponent's potential movement is approximated by using current distance only)
        sc += (dTO - dT) * 2
        # Avoid allowing direct collision/adjacency if possible
        sc -= (3 if dO_next == 0 else 0)
        sc -= (1 if dO_next == 1 else 0)

        # Mild obstacle-avoidance: penalize moving next to obstacles to reduce detours
        adj_obs = 0
        for ox2, oy2 in obstacles:
            if cheb(nx, ny, ox2, oy2) == 1:
                adj_obs += 1
        sc -= adj_obs * 0.5

        if sc > best_score:
            best_score = sc
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]