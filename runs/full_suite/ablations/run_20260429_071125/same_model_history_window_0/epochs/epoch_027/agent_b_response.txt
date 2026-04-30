def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation["resources"]; obstacles = set((p[0], p[1]) for p in observation["obstacles"])
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def dist(a, b): 
        dx = a[0]-b[0]; dy = a[1]-b[1]
        return dx*dx + dy*dy
    # Select best resource by "being closer than opponent" (tie-break by nearer)
    if resources:
        best = None; bestv = -10**18
        for rx, ry in resources:
            sv = dist((sx, sy), (rx, ry))
            ov = dist((ox, oy), (rx, ry))
            v = (ov - sv) * 1000000 - sv  # strong preference for lead
            if v > bestv:
                bestv = v; best = (rx, ry)
        tx, ty = best
    else:
        tx, ty = w // 2, h // 2

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    # If in same cell as obstacle (shouldn't happen), just stay
    if (sx, sy) in obstacles:
        return [0, 0]

    # Evaluate candidate moves with obstacle avoidance and opponent repulsion
    bestm = (0, 0); bestscore = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny): 
            continue
        if (nx, ny) in obstacles:
            continue
        d_self = dist((nx, ny), (tx, ty))
        d_opp_to = dist((ox, oy), (tx, ty))
        # Prefer reducing self distance while maintaining lead and keeping away from opponent
        score = -d_self
        score += (d_opp_to - d_self) * 2000
        # Opponent repulsion if moving toward them (encourage separation to avoid competition)
        d_opp = dist((nx, ny), (ox, oy))
        if d_opp == 0: score -= 10**9
        else: score -= 1000 // (d_opp + 1)
        # Slightly prefer positions closer to target even if tied
        if score > bestscore or (score == bestscore and (dx*dx + dy*dy) < (bestm[0]*bestm[0] + bestm[1]*bestm[1])):
            bestscore = score; bestm = (dx, dy)
    return [int(bestm[0]), int(bestm[1])]