def choose_move(observation):
    w = int(observation["grid_width"]); h = int(observation["grid_height"])
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def valid(x, y): return inb(x, y) and (x, y) not in obstacles
    INF = 10**9

    def bfs(start):
        if not valid(start[0], start[1]):
            return [[INF]*h for _ in range(w)]
        dist = [[INF]*h for _ in range(w)]
        x0, y0 = start
        dist[x0][y0] = 0
        q = [(x0, y0)]
        qi = 0
        while qi < len(q):
            x, y = q[qi]; qi += 1
            nd = dist[x][y] + 1
            for dx, dy in moves:
                nx, ny = x + dx, y + dy
                if valid(nx, ny) and nd < dist[nx][ny]:
                    dist[nx][ny] = nd
                    q.append((nx, ny))
        return dist

    resources = observation.get("resources") or []
    distS = bfs((sx, sy))
    distO = bfs((ox, oy))

    if not resources:
        cx, cy = (w-1)//2, (h-1)//2
        best_move = (0, 0)
        best_val = -10**18
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny): 
                continue
            d_center = max(abs(nx - cx), abs(ny - cy))
            d_opp = max(abs(nx - ox), abs(ny - oy))
            val = d_opp*2 - d_center
            if val > best_val:
                best_val = val
                best_move = (dx, dy)
        return [best_move[0], best_move[1]]

    best = None
    best_score = -10**18
    for rx, ry in resources:
        if not valid(rx, ry):
            continue
        dS = distS[rx][ry]
        dO = distO[rx][ry]
        if dS >= INF:
            continue
        # Prefer grabbing where we are closer than opponent; tie-break by absolute speed.
        score = (dO - dS)*1000 - dS
        # Slight deterministic bias toward resources closer to our current heading corner (away from being stuck)
        score += -0.001 * (abs(rx - (w-1)) + abs(ry - (h-1)))
        if score > best_score:
            best_score = score
            best = (rx, ry)

    if best is None:
        return [0, 0]

    tx, ty = best
    # Choose neighbor that minimizes distance to target; break ties by maximizing distance advantage vs opponent.
    best_move = (0, 0)
    best_pair = (INF, -INF)  # (d_to_target, -advantage)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d_to = distS[nx][ny] + 0  # distS from start; monotonic proxy
        # Better: use distS to target from each neighbor via BFS computed earlier? we only have dist from start.
        # We'll approximate by direct Chebyshev to target to stay local and deterministic.
        d_to = max(abs(nx - tx), abs(ny - ty))
        adv = distO[tx][ty] - distS[tx][ty]  # global advantage signal
        pair = (d_to, -(adv*1000))
        if pair < best_pair:
            best_pair = pair
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]