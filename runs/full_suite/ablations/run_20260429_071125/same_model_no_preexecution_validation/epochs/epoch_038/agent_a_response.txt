def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = int(observation["self_position"][0]), int(observation["self_position"][1])
    ox, oy = int(observation["opponent_position"][0]), int(observation["opponent_position"][1])
    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles") or []))
    resources = [(int(p[0]), int(p[1])) for p in (observation.get("resources") or [])]
    INF = 10**9

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def valid(x, y): return inb(x, y) and (x, y) not in obstacles

    def bfs(x0, y0):
        dist = [[INF] * h for _ in range(w)]
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

    distS = bfs(sx, sy)
    distO = bfs(ox, oy)

    best_move = (0, 0)
    best_val = -10**18

    # If resources exist, pick move that improves best "claimability" (earlier for us, later for opponent).
    if resources:
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            s_here = distS[nx][ny]
            val = -s_here * 2  # closer first
            for rx, ry in resources:
                ds = distS[rx][ry]
                if ds >= INF:
                    continue
                # We prioritize resources where we can beat the opponent by margin.
                do = distO[rx][ry]
                if do >= INF:
                    do = 10**6
                # "Deny" term: larger (do - ds) is better; also prefer reachable soon from this position.
                # Include a small bonus if moving reduces remaining distance to that resource.
                rem = distS[rx][ry] - s_here
                if rem < 0:
                    rem = 0
                val += (do - ds) * 3 + (-rem) * 0.5
            # Deterministic tie-break: prefer earlier in moves list by slightly biasing.
            val -= (moves.index((dx, dy)) if (dx, dy) in moves else 0) * 1e-6
            if val > best_val:
                best_val = val
                best_move = (dx, dy)
        return [int(best_move[0]), int(best_move[1])]

    # No resources: drift toward opponent to deny by proximity while avoiding obstacles.
    # Secondary objective: keep distance from opponent from getting too low? We'll instead try to reduce it.
    best_d = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        dd = -(abs(nx - ox) + abs(ny - oy))  # maximize closeness to opponent
        if dd > best_d:
            best_d = dd
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]