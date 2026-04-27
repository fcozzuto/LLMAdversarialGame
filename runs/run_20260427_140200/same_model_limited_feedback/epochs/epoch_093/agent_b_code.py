def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    cands = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    def clamp(nx, ny):
        if nx < 0: nx = 0
        if ny < 0: ny = 0
        if nx >= w: nx = w - 1
        if ny >= h: ny = h - 1
        return nx, ny
    def dist(a,b):
        return (a[0]-b[0])**2 + (a[1]-b[1])**2
    # Pick a resource we can reach sooner than opponent; deterministic tie-break by position.
    if resources:
        best = None
        best_key = None
        for rx, ry in resources:
            dS = dist((sx,sy),(rx,ry))
            dO = dist((ox,oy),(rx,ry))
            key = (dO - dS, -rx, -ry)  # larger is better
            if best_key is None or key > best_key:
                best_key = key
                best = (rx, ry)
        tx, ty = best
    else:
        tx, ty = (ox, oy)
    moves = []
    for dx, dy in cands:
        nx, ny = clamp(sx + dx, sy + dy)
        if (nx, ny) in obstacles:
            continue
        # Avoid stepping onto opponent (if allowed, still contest is risky).
        if (nx, ny) == (ox, oy):
            continue
        self_d = dist((nx,ny),(tx,ty))
        opp_d = dist((ox,oy),(tx,ty))
        # Prefer increasing the advantage; also gently spread from opponent when tied.
        opp_spread = (nx-ox)**2 + (ny-oy)**2
        # Small preference to reduce step cost
        step_cost = dx*dx + dy*dy
        score = (opp_d - self_d) + 0.01*opp_spread - 0.001*step_cost
        moves.append((score, -dx, -dy, dx, dy))
    if not moves:
        # Only safe fallback if all moves blocked.
        return [0, 0]
    moves.sort(reverse=True)
    return [moves[0][3], moves[0][4]]