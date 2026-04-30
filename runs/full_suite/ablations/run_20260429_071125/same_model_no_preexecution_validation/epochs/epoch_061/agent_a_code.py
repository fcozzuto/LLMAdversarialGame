def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = map(int, observation.get("self_position", [0, 0]))
    ox, oy = map(int, observation.get("opponent_position", [0, 0]))
    resources = [(int(p[0]), int(p[1])) for p in (observation.get("resources") or [])]
    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles") or []))
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    INF = 10**9

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def valid(x, y): return inb(x, y) and (x, y) not in obstacles

    def bfs(x0, y0):
        dist = [[INF] * h for _ in range(w)]
        if not valid(x0, y0): return dist
        dist[x0][y0] = 0
        qx, qy = [x0], [y0]
        qi = 0
        while qi < len(qx):
            x, y = qx[qi], qy[qi]; qi += 1
            nd = dist[x][y] + 1
            for dx, dy in moves:
                nx, ny = x + dx, y + dy
                if valid(nx, ny) and nd < dist[nx][ny]:
                    dist[nx][ny] = nd
                    qx.append(nx); qy.append(ny)
        return dist

    if not resources:
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best, bestd = [0, 0], -INF
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny): continue
            d = -(abs(nx - cx) + abs(ny - cy))
            if d > bestd: bestd = d; best = [dx, dy]
        return best

    distS = bfs(sx, sy)
    distO = bfs(ox, oy)

    opp_catch = 0
    best_move = [0, 0]
    best_val = -INF

    # Evaluate immediate moves by best resource contest outcome + obstacle avoidance (implicitly via BFS validity)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny): 
            continue
        val = 0
        # Prefer collecting reachable resources, deny opponent if we can arrive no later
        for tx, ty in resources:
            ds = distS[tx][ty]
            if ds >= INF: 
                continue
            # If we step to (nx,ny), approximate our remaining distance to (tx,ty) using triangle inequality in grid metric via BFS lookup next by recomputing? too costly.
            # Instead compute from new position using Manhattan as a quick deterministic bias, while contest term uses distS already.
            # Add stronger term for resources that are close to our current move target.
            dm = abs(tx - nx) + abs(ty - ny)
            # Our advantage estimate: ds from start, opponent distance from opponent
            do = distO[tx][ty]
            if do >= INF: 
                do = ds + 5
            # Reward being able to reach at least as early as opponent; penalize if opponent earlier.
            contest = (do - ds)
            val += 3.0 * contest - 0.35 * dm - 0.05 * ds
            # Extra: if opponent is close to this resource, prioritize denying them.
            val += 0.75 * max(0, 3 - do)
        # Safety: avoid moves that keep us immobilized next to obstacles by favoring fewer blocked neighbors
        blocked = 0
        for adx, ady in moves:
            ax, ay = nx + adx, ny + ady
            if not valid(ax, ay): blocked += 1
        val -= 0.08 * blocked
        if val > best_val:
            best_val = val
            best_move = [dx, dy]
    return best_move