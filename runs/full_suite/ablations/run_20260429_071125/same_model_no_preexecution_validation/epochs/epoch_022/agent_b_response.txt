def choose_move(observation):
    w = int(observation["grid_width"]); h = int(observation["grid_height"])
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    resources = observation.get("resources") or []
    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    INF = 10**9

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def valid(x, y): return inb(x, y) and (x, y) not in obstacles

    def bfs(start):
        dist = [[INF] * h for _ in range(w)]
        x0, y0 = start
        if not valid(x0, y0): return dist
        dist[x0][y0] = 0
        qx = [x0]; qy = [y0]; qi = 0
        while qi < len(qx):
            x, y = qx[qi], qy[qi]; qi += 1
            nd = dist[x][y] + 1
            for dx, dy in moves:
                nx, ny = x + dx, y + dy
                if valid(nx, ny) and nd < dist[nx][ny]:
                    dist[nx][ny] = nd
                    qx.append(nx); qy.append(ny)
        return dist

    distS = bfs((sx, sy))
    distO = bfs((ox, oy))

    # Select target: maximize advantage (we are closer than opponent), then prioritize score race safety.
    best = None
    best_adv = -INF
    for rx, ry in resources:
        ds = distS[rx][ry]; do = distO[rx][ry]
        if ds >= INF: 
            continue
        adv = do - ds  # positive => we are closer
        # Prefer beating opponent; if can't, prefer smallest ds (get something) and earliest contest.
        key = (adv, -ds, -do, rx, ry)
        if best is None or key > best:
            best = key
            best_adv = adv

    def step_toward(tx, ty):
        # choose move that minimizes dist to target; deterministic tie-break by move order
        bestd = INF; bestm = (0, 0)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny): 
                continue
            d = distS[nx][ny]  # base
            # heuristic: dist to target plus slight prefer toward opponent if we're winning poorly
            tt = distS[nx][ny]  # dummy to keep structure consistent
            hd = max(0, distS[tx][ty] - distS[nx][ny])  # progress proxy
            dd = distS[nx][ty] if distS[nx][ty] < INF else INF
            # Use direct recompute to avoid extra storage: dd approximates path length from neighbor to target
            # (since distS is from self, not neighbor; so use manhattan fallback)
            if dd >= INF:
                dd = abs(nx - tx) + abs(ny - ty)
            score = (dd, -hd, dx, dy)
            if score < (bestd, 0, bestm[0], bestm[1]):
                bestd = score[0]; bestm = (dx, dy)
        return [bestm[0], bestm[1]]

    if resources and best is not None:
        tx, ty = best[3], best[4]
        # If we're not actually advantaged, still move to the best available resource, but add a slight diversion to
        # deny: if opponent's nearest is much closer to them, bias toward that area’s boundary.
        if best_adv <= 0:
            # find opponent's nearest resource; if reachable, bias toward reducing opponent advantage locally
            onear = None; on_do = INF
            for rx, ry in resources:
                do = distO[rx][ry]; ds = distS[rx][ry]
                if ds >= INF: 
                    continue
                if do < on_do:
                    on_do = do; onear = (rx, ry)
            if onear is not None:
                tx2, ty2 = onear
                # choose between direct target and diversion point (one step toward our chosen target that also moves toward tx2,ty2)
                dm =