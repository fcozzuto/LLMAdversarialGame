def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def valid(x, y): return inb(x, y) and (x, y) not in obstacles

    cand = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def bfs(stx, sty):
        INF = 10**9
        dist = [[INF] * h for _ in range(w)]
        if not valid(stx, sty): return dist
        qx, qy, qi = [stx], [sty], 0
        dist[stx][sty] = 0
        while qi < len(qx):
            x, y = qx[qi], qy[qi]
            qi += 1
            nd = dist[x][y] + 1
            for dx, dy in cand:
                nx, ny = x + dx, y + dy
                if valid(nx, ny) and nd < dist[nx][ny]:
                    dist[nx][ny] = nd
                    qx.append(nx); qy.append(ny)
        return dist

    if not resources:
        tx, ty = w - 1, h - 1
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        nx, ny = sx + dx, sy + dy
        return [dx, dy] if valid(nx, ny) else [0, 0]

    opp_dist = bfs(ox, oy)
    if any((rx, ry) == (sx, sy) for rx, ry in resources):
        return [0, 0]

    best_val = -10**18
    best_move = (0, 0)
    for dx, dy in cand:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny): continue
        self_dist = bfs(nx, ny)
        # If we can reach a resource before opponent, maximize that lead; otherwise minimize our distance to the best resource.
        val_adv = None
        val_fallback = (10**9, 10**9)
        for rx, ry in resources:
            ds = self_dist[rx][ry]
            do = opp_dist[rx][ry]
            if ds >= 10**8 or do >= 10**8: 
                continue
            if ds < do:
                lead = do - ds
                cand_val = (lead, -ds)  # prioritize lead, then sooner
                if val_adv is None or cand_val > val_adv:
                    val_adv = cand_val
            else:
                cand_f = (ds, do)
                if cand_f < val_fallback:
                    val_fallback = cand_f
        if val_adv is not None:
            score = val_adv[0] * 1000 + val_adv[1]  # strong preference for taking lead
        else:
            score = -val_fallback[0] * 2 - (0 if val_fallback[1] >= 10**8 else val_fallback[1] // 2)
        if score > best_val or (score == best_val and (dx, dy) < best_move):
            best_val = score
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]