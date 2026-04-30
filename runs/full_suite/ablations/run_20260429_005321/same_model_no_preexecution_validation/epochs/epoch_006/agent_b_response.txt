def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obs_list = observation.get("obstacles") or []
    obstacles = set((p[0], p[1]) for p in obs_list)
    dirs = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h

    INF = 10**9
    def bfs(start):
        x0, y0 = start
        dist = [[INF] * w for _ in range(h)]
        if not inb(x0, y0) or (x0, y0) in obstacles:
            return dist
        dist[y0][x0] = 0
        q = [(x0, y0)]
        qi = 0
        while qi < len(q):
            x, y = q[qi]; qi += 1
            nd = dist[y][x] + 1
            for dx, dy in dirs:
                nx, ny = x + dx, y + dy
                if inb(nx, ny) and (nx, ny) not in obstacles and nd < dist[ny][nx]:
                    dist[ny][nx] = nd
                    q.append((nx, ny))
        return dist

    our_dist = bfs((sx, sy))
    opp_dist = bfs((ox, oy))

    legal = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            legal.append((dx, dy))
    if not legal:
        return [0, 0]

    if not resources:
        # drift to reduce opponent advantage: maximize (opp_dist - our_dist) locally
        best = None; bestv = -10**18
        for dx, dy in legal:
            nx, ny = sx + dx, sy + dy
            v = (opp_dist[ny][nx] - our_dist[ny][nx])
            if v > bestv or (v == bestv and (dx, dy) < best):
                bestv = v; best = (dx, dy)
        return [best[0], best[1]]

    # Choose best target deterministically among reachable resources
    best_target = None; best_metric = INF
    for rx, ry in resources:
        d = our_dist[ry][rx]
        if d < INF:
            # favor closer and also resources that opponent is not much closer to
            m = d * 1000 + opp_dist[ry][rx]
            if m < best_metric:
                best_metric = m
                best_target = (rx, ry)

    # If all unreachable, fallback to avoid obstacles and move to improve distance to opponent
    if best_target is None:
        best = None; bestv = 10**18
        for dx, dy in legal:
            nx, ny = sx + dx, sy + dy
            v = our_dist[ny][nx]
            if v < bestv or (v == bestv and (dx, dy) < best):
                bestv = v; best = (dx, dy)
        return [best[0], best[1]]

    tx, ty = best_target
    best_move = None; best_val = -10**18
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        # minimize our distance to target, maximize opponent distance to target
        my_to = our_dist[ny][nx]
        # compute distance from neighbor to target by using BFS distances already computed:
        # we only have distances from our start, so approximate with (our_dist[sx,sy] - our_dist[nx,ny]) not valid.
        # Instead, use greedy step evaluation by directly comparing neighbor's dist-to-target via BFS from each neighbor is too costly.
        # But we can still evaluate using our_dist-to-target by BFS once from start isn't enough.
        # Use Manhattan/chebyshev tie-break toward target as heuristic; still deterministic and collision-free.
        # Also include exact path usefulness using current our_dist at neighbor.
        cheb = max(abs(nx - tx), abs(ny - ty))
        # opponent heuristic
        opp_cheb = max(abs(ox - tx), abs(oy - ty))
        # prefer reducing cheb and staying on cells with smaller our_dist from start (more "reachable" areas)
        val = (-cheb * 1000) + (-my_to) + (opp_dist[ty][tx] * 0) + (0) - opp_cheb * 0
        # deterministic tie-break: lexicographic (dx,dy)
        if