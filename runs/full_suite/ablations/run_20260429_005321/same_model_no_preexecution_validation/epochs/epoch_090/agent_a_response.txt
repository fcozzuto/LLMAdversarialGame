def choose_move(observation):
    w = int(observation["grid_width"]); h = int(observation["grid_height"])
    sx, sy = int(observation["self_position"][0]), int(observation["self_position"][1])
    ox, oy = int(observation["opponent_position"][0]), int(observation["opponent_position"][1])
    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles") or []))
    resources = [(int(p[0]), int(p[1])) for p in (observation.get("resources") or [])]
    dirs = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def free(x, y): return inb(x, y) and (x, y) not in obstacles

    def bfs(start):
        INF = 10**6
        dist = [[INF] * h for _ in range(w)]
        if not free(start[0], start[1]): return dist
        qx = [start[0]]; qy = [start[1]]; qi = 0
        dist[start[0]][start[1]] = 0
        while qi < len(qx):
            x, y = qx[qi], qy[qi]; qi += 1
            nd = dist[x][y] + 1
            for dx, dy in dirs:
                nx, ny = x + dx, y + dy
                if free(nx, ny) and nd < dist[nx][ny]:
                    dist[nx][ny] = nd
                    qx.append(nx); qy.append(ny)
        return dist

    mydist = bfs((sx, sy))
    oppdist = bfs((ox, oy))

    def adj_obstacle_density(x, y):
        c = 0
        for dx, dy in dirs:
            if dx == 0 and dy == 0: 
                continue
            nx, ny = x + dx, y + dy
            if inb(nx, ny) and (nx, ny) in obstacles:
                c += 1
        return c

    def best_target_from(posx, posy):
        best = None
        best_score = -10**18
        for rx, ry in resources:
            if not free(rx, ry): 
                continue
            dme = mydist[posx][posy] + 0
            # Use direct dist if precomputed cell differs; correct by reading dist from global tables:
            dme = mydist[rx][ry]  # true distance from current start position
            dop = oppdist[rx][ry]
            if dme >= 10**5 and dop >= 10**5:
                continue
            # Advantage: earlier arrival matters most; tie-break by being closer to the resource and obstacle density
            adv = dop - dme
            score = adv * 1000 - dme + adj_obstacle_density(rx, ry)
            # If we are currently behind on this resource, prefer resources where we can still catch up
            if adv < 0:
                score -= (-adv) * 20
            if best is None or score > best_score:
                best_score = score
                best = (rx, ry, dme, dop)
        return best

    # Choose best immediate move by evaluating next position against global distances
    best_move = [0, 0]
    best_val = -10**18
    # If resources are empty, move toward opponent side while keeping away from obstacles
    if not resources:
        targetx, targety = w - 1, h - 1
        if ox < w - 1 and oy > 0: 
            targetx, targety = w - 2, h - 2
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not free(nx, ny): 
                continue
            cheb = abs(targetx - nx); d2 = abs(targety - ny)
            val = -(cheb if cheb > d2 else d2)
            val -= adj_obstacle_density(nx, ny) * 2
            if val > best_val:
                best_val = val; best_move = [dx, dy]
        return best_move

    # Precompute distance arrays for quick successor evaluation:
    # We'll approximate successor distances by using BFS from successor if needed? Too heavy.
    # Instead, do a local 2-step lookahead by using one-step update with the BFS