def choose_move(observation):
    w = int(observation["grid_width"]); h = int(observation["grid_height"])
    sx, sy = int(observation["self_position"][0]), int(observation["self_position"][1])
    ox, oy = int(observation["opponent_position"][0]), int(observation["opponent_position"][1])

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        obstacles.add((int(p[0]), int(p[1])))

    resources = observation.get("resources") or []
    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    INF = 10**9

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def valid(x, y): return inb(x, y) and (x, y) not in obstacles

    def bfs(x0, y0):
        dist = [[INF] * h for _ in range(w)]
        if not valid(x0, y0): return dist
        dist[x0][y0] = 0
        qx = [x0]; qy = [y0]; qi = 0
        while qi < len(qx):
            x = qx[qi]; y = qy[qi]; qi += 1
            nd = dist[x][y] + 1
            for dx, dy in moves:
                nx, ny = x + dx, y + dy
                if valid(nx, ny) and nd < dist[nx][ny]:
                    dist[nx][ny] = nd
                    qx.append(nx); qy.append(ny)
        return dist

    distS = bfs(sx, sy)
    distO = bfs(ox, oy)

    # Pick best target: prefer resources we can reach earlier and/or that are "denied" (do close to ds).
    best = None
    best_val = -INF
    for r in resources:
        rx, ry = int(r[0]), int(r[1])
        if not valid(rx, ry): 
            continue
        ds = distS[rx][ry]
        do = distO[rx][ry]
        if ds >= INF: 
            continue
        # Advantage: positive if we are earlier; also prefer closer targets.
        adv = (do - ds)
        val = 10.0 * adv / (ds + 1.0)
        # If both can reach, slight preference for where opponent is farther.
        if do >= INF:
            val += 5.0 / (ds + 1.0)
        best_val, best = (val, (rx, ry)) if val > best_val else (best_val, best)

    # If no reachable resources, retreat from opponent a bit (deterministic).
    if best is None:
        best_move = [0, 0]
        best_d = -INF
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny): 
                continue
            dd = -((nx - ox) * (nx - ox) + (ny - oy) * (ny - oy))
            # maximize distance => minimize negative dd
            if dd > best_d:
                best_d = dd
                best_move = [dx, dy]
        return best_move

    tx, ty = best
    # Choose move that reduces our distance to target, but if opponent is closer, bias to slow ourselves least.
    best_move = [0, 0]
    best_score = -INF
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        ds_next = distS[tx][ty]  # fallback
        # compute quick estimate: 1-step to target uses BFS-like gradient from distS
        # We'll use distS at next pos to same target via reusing distS: distS[target] doesn't help.
        # Instead, estimate using Chebyshev distance and opponent proximity.
        step_to_target = max(abs(nx - tx), abs(ny - ty))
        step_to_target = step_to_target + (0 if (nx, ny) == (tx, ty) else 0)
        opp_step = max(abs(nx - ox), abs(ny - oy))
        ds_cur = distS[tx][ty]
        do_cur = distO[tx][ty]
        # If opponent can reach sooner