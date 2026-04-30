def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = map(int, observation.get("self_position", [0, 0]))
    ox, oy = map(int, observation.get("opponent_position", [0, 0]))
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles") or []))
    resources = [(int(p[0]), int(p[1])) for p in (observation.get("resources") or [])]
    INF = 10**9

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def valid(x, y): return inb(x, y) and (x, y) not in obstacles

    def bfs(x0, y0):
        dist = [[INF] * h for _ in range(w)]
        if not valid(x0, y0):
            return dist
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

    dS = bfs(sx, sy)
    dO = bfs(ox, oy)

    if not resources:
        best = (0, 0)
        bestv = -10**18
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            v = -max(abs(nx - ox), abs(ny - oy))  # keep away from opponent
            if v > bestv:
                bestv = v; best = (dx, dy)
        return [best[0], best[1]]

    # Choose a target resource we can reach before (or at least not much later than) opponent.
    best_t = None
    best_key = None
    for rx, ry in resources:
        ds = dS[rx][ry]
        do = dO[rx][ry]
        if ds >= INF:
            continue
        # Favor winning captures; if none, allow near-ties or being closer by small margin.
        margin = do - ds
        key = (margin, -ds)
        if best_key is None or key > best_key:
            best_key = key
            best_t = (rx, ry)

    tx, ty = best_t if best_t is not None else resources[0]

    # Score candidate moves by progress to target, ability to contest, and avoidance of opponent.
    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        ds = dS[nx][ny]
        do = dO[nx][ny]
        # Move-to-target: reduce distance from (nx,ny) to target via our BFS estimate.
        dt = dS[tx][ty]
        nt = dS[nx][tx]  # heuristic proxy; BFS distance between current and target
        # contest bonus if we are ahead/close relative to opponent on this move
        contest = do - ds
        # immediate opponent proximity penalty
        opp_close = max(abs(nx - ox), abs(ny - oy))
        # also avoid stepping into squares where opponent is much closer to the chosen target
        opp_to_t = dO[tx][ty]  # global, but stable; slight weight
        score = 0
        score += 3 * (-(nt))  # lower BFS distance to target is better
        score += 2 * contest
        score += -0.6 * opp_close
        score += -0.05 * abs(opp_to_t - dt)
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]