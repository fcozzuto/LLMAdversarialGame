def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    rem = observation.get("remaining_resource_count", len(resources))
    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def valid(x, y): return inb(x, y) and (x, y) not in obstacles

    def bfs(st):
        INF = 10**9
        dist = [[INF]*h for _ in range(w)]
        x0, y0 = st
        if not valid(x0, y0): return dist
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

    # If no resources visible/endgame: maximize safety from opponent with obstacle-aware BFS distance
    if not resources or rem <= 0:
        do = bfs((ox, oy))
        best = [0, 0]; bestv = -1
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny): continue
            v = do[nx][ny]  # farther is better
            if v > bestv:
                bestv = v; best = [dx, dy]
        return best

    ds = bfs((sx, sy))
    do = bfs((ox, oy))

    # Evaluate one-step moves by their ability to reach good contested resources,
    # and if all are bad, by reducing opponent's closest resource distance.
    cur_valid = [(dx, dy) for dx, dy in moves if valid(sx + dx, sy + dy)]
    if not cur_valid:
        return [0, 0]

    best_move = cur_valid[0]
    best_score = -10**18

    # Precompute distances from each candidate cell to resources
    for dx, dy in cur_valid:
        nx, ny = sx + dx, sy + dy
        self_best = -10**9
        opp_best = 10**9
        # score resources: prefer ones we can reach sooner (opp_dist - self_dist),
        # with tie-breaker favoring smaller self distance.
        for rx, ry in resources:
            sd = ds[nx][ny]
            od = do[rx][ry]  # opponent distance to resource
            # if resource unreachable, keep it harmless
            if od >= 10**8:
                continue
            rsd = ds[rx][ry]
            rod = od
            if rsd >= 10**8:
                continue
            win_margin = rod - rsd
            # Strongly prioritize positive margin; also prioritize larger margin / closer win.
            score = win_margin * 100 - rsd
            if score > self_best:
                self_best = score
            # For blocking mode, track opponent's best (closest) resource
            if rod < opp_best:
                opp_best = rod

        # Determine whether we have any competitive resource (using current position distances)
        comp = -10**18
        any_comp = False
        for rx, ry in resources:
            rsd = ds[rx][ry]
            rod = do[rx][