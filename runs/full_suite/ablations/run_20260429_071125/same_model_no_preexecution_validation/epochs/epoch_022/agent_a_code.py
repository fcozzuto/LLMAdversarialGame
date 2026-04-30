def choose_move(observation):
    w = int(observation["grid_width"]); h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    resources = observation.get("resources") or []
    INF = 10**8

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def valid(x, y): return inb(x, y) and (x, y) not in obstacles

    def bfs(start):
        x0, y0 = start
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

    distS = bfs((sx, sy))
    distO = bfs((ox, oy))

    def score_target(rx, ry):
        ds = distS[rx][ry]; do = distO[rx][ry]
        if ds >= INF:
            return None
        if do >= INF:
            do = INF
        # Prefer being closer than opponent, then shorter distance to secure.
        delta = do - ds
        return (delta * 1000) - ds - (abs(rx - ox) + abs(ry - oy)) * 0.01

    best_move = (0, 0)
    best_val = -INF

    # If resources exist, go for the best contested objective.
    if resources:
        best_targets = []
        for rx, ry in resources:
            v = score_target(rx, ry)
            if v is not None:
                best_targets.append((v, rx, ry))
        if best_targets:
            best_targets.sort(key=lambda t: (-t[0], t[1], t[2]))
            _, tx, ty = best_targets[0]
            # Choose step that improves our distance to target and worsens opponent's.
            for dx, dy in moves:
                nx, ny = sx + dx, sy + dy
                if not valid(nx, ny):
                    continue
                if distS[nx][ny] >= INF:
                    continue
                my = distS[nx][ny]
                op = distO[tx][ty]  # opponent distance to target (constant for step)
                # Use opponent distance from their position to nx,ny to discourage giving them a shortcut.
                opp_reach = distO[nx][ny]
                val = -my - (opp_reach * 0.05 if opp_reach < INF else 0) + (abs(nx - tx) + abs(ny - ty)) * -0.01
                # Small tie-break toward moving generally toward target.
                val += -((nx - tx) ** 2 + (ny - ty) ** 2) * 0.0001
                if val > best_val:
                    best_val = val
                    best_move = (dx, dy)

    # Fallback / reinforcement: move toward nearest resource if any, else toward center while avoiding opponent.
    if best_val == -INF:
        cx, cy = (w - 1) / 2, (h - 1) / 2
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            dcen = (nx - cx) ** 2 + (ny - cy) ** 2
            oppd = (nx - ox) ** 2 + (ny - oy) ** 2
            val = -dcen + oppd * 0.02
            if resources:
                # Prefer a move that reduces distance to the closest reachable resource.
                mres = INF
                for rx, ry in resources:
                    if distS[rx][ry] < INF:
                        mres = min(mres, distS[rx][ry])
                val += -mres * 0.01
            if val > best_val:
                best_val = val
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]