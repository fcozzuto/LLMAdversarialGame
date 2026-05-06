def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    moves = [(-1,-1), (0,-1), (1,-1), (-1,0), (0,0), (1,0), (-1,1), (0,1), (1,1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def dist(a,b,c,d): 
        dx = a-c; dy = b-d
        return (dx*dx + dy*dy)
    def best_step(tx, ty):
        # choose step that is best for getting to (tx,ty), avoiding obstacles
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny): 
                continue
            if (nx, ny) in obstacles:
                continue
            val = dist(nx, ny, tx, ty)
            # small tie-break: prefer moving in x then y deterministically
            tie = (abs(dx), abs(dy), dx, dy)
            cand = (val, tie)
            if best is None or cand < best[0]:
                best = (cand, (dx, dy))
        if best is None:
            return [0,0]
        return [best[1][0], best[1][1]]

    if not resources:
        # no resources: try to approach center deterministically
        cx, cy = w//2, h//2
        return best_step(cx, cy)

    # Choose target resource where we are relatively closer than the opponent.
    # Score = (opp_dist - self_dist) with slight preference for nearer resources.
    scored = []
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        sd = dist(sx, sy, rx, ry)
        od = dist(ox, oy, rx, ry)
        # higher is better
        score = (od - sd) * 1000 - sd
        scored.append((-(score), sd, od, rx, ry))  # sort ascending by negative score
    scored.sort()
    _, _, _, tx, ty = scored[0]

    # If opponent is closer to almost all resources, try to contest the closest one directly.
    # Simple deterministic contest trigger:
    best_self = scored[0]
    best_opp = None
    for rx, ry in resources:
        sd = dist(sx, sy, rx, ry)
        od = dist(ox, oy, rx, ry)
        if (rx, ry) in obstacles:
            continue
        if best_opp is None or od < best_opp[0]:
            best_opp = (od, sd, rx, ry)
    if best_opp is not None:
        _, selfd_opp, ptx, pty = best_opp
        if best_self[2] <= best_self[1] and (best_opp[0] - best_self[2]) < 1:
            # opponent not far: focus on the opponent's closest target
            tx, ty = ptx, pty

    return best_step(tx, ty)