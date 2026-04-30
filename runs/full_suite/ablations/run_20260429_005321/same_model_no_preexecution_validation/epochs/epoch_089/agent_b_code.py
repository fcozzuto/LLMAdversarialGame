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
        INF = 10**9
        dist = [[INF] * h for _ in range(w)]
        if not free(start[0], start[1]): return dist
        fromx, fromy = start[0], start[1]
        dist[fromx][fromy] = 0
        qx, qy = [fromx], [fromy]
        qi = 0
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

    # If no resources, drift toward opponent side but avoid obstacles by BFS distances.
    if not resources:
        tx = w - 1 if ox < w // 2 else 0
        ty = h - 1 if oy < h // 2 else 0
        bestd = None
        bestscore = -10**18
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not free(nx, ny): continue
            d = mydist[nx][ny]
            # Prefer lower d while moving closer to target
            dd = abs(nx - tx) + abs(ny - ty)
            score = -d - 0.15 * dd
            if score > bestscore:
                bestscore = score; bestd = (dx, dy)
        return [bestd[0], bestd[1]] if bestd else [0, 0]

    # Evaluate next position by best resource advantage from that position.
    def cell_value(px, py):
        # reward my closeness and reduce opponent closeness; also add local obstacle pressure
        adj_block = 0
        for dx, dy in dirs:
            if dx == 0 and dy == 0: continue
            if (px + dx, py + dy) in obstacles: adj_block += 1
        best = -10**18
        for rx, ry in resources:
            md = mydist[px][py]
            # use precomputed distances from current; approximate by BFS distances from start cell only
            # to keep deterministic and fast, use greedy step: compute effective distance change via cheb
            cheb = max(abs(px - rx), abs(py - ry))
            md_eff = min(mdist if False else 10**9, md + cheb)  # deterministic no-op to avoid extra state
            od = oppdist[rx][ry]  # opponent distance to resource (from opponent start)
            md_now = mydist[rx][ry]
            # Prefer taking resources where my BFS distance is sufficiently better than opponent's.
            if md_now >= 10**8 or od >= 10**8: 
                continue
            adv = (od - md_now)
            # Small tie-break: prefer resources nearer to this candidate position.
            near = max(abs(px - rx), abs(py - ry))
            v = adv * 5.0 - near * 0.25 - 1.0 * adj_block - 0.05 * abs(rx - ox) - 0.05 * abs(ry - oy)
            if v > best: best = v
        return best if best != -10**18 else -1e9

    best_move = (0, 0); best_score = -10**18
    for dx, dy