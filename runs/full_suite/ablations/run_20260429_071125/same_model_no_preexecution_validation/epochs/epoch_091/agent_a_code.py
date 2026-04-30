def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = map(int, observation.get("self_position", [0, 0]))
    ox, oy = map(int, observation.get("opponent_position", [0, 0]))
    resources = observation.get("resources") or []
    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles") or []))
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    INF = 10**9

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def valid(x, y):
        return inb(x, y) and (x, y) not in obstacles

    def bfs(x0, y0):
        dist = [[INF] * h for _ in range(w)]
        if not valid(x0, y0):
            return dist
        dist[x0][y0] = 0
        qx, qy = [x0], [y0]
        qi = 0
        while qi < len(qx):
            x, y = qx[qi], qy[qi]
            qi += 1
            nd = dist[x][y] + 1
            for dx, dy in moves:
                nx, ny = x + dx, y + dy
                if valid(nx, ny) and nd < dist[nx][ny]:
                    dist[nx][ny] = nd
                    qx.append(nx)
                    qy.append(ny)
        return dist

    dS = bfs(sx, sy)
    dO = bfs(ox, oy)

    best_rx = best_ry = None
    best_score = -10**18
    for r in resources:
        rx, ry = int(r[0]), int(r[1])
        if not (0 <= rx < w and 0 <= ry < h):
            continue
        ds = dS[rx][ry]
        do = dO[rx][ry]
        if ds >= INF or do >= INF:
            continue
        # Prefer resources where we are strictly earlier; otherwise still take those we can reach with minimal delay.
        adv = do - ds
        # Score shaped to strongly prioritize advantage, then shorter our distance, then farther opponent distance.
        score = adv * 1000 + (-ds) * 10 + (do - INF if do < INF else 0) * 0.0
        if score > best_score or (score == best_score and (best_rx is None or (ds, do, rx, ry) < (dS[best_rx][best_ry], dO[best_rx][best_ry], best_rx, best_ry))):
            best_score = score
            best_rx, best_ry = rx, ry

    # If no reachable resource, drift toward center while avoiding obstacles.
    if best_rx is None:
        tx, ty = w // 2, h // 2
        best = (0, 0)
        bestd = -INF
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            # minimize distance to center -> maximize negative dist
            dd = (nx - tx) * (nx - tx) + (ny - ty) * (ny - ty)
            if -dd > bestd:
                bestd = -dd
                best = (dx, dy)
        return [best[0], best[1]]

    target_ds = dS[best_rx][best_ry]
    # Greedily step to reduce our distance to target; if tie, reduce opponent distance to same target (contest).
    cand = None
    cand_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        ns = dS[nx][ny]
        if ns >= INF:
            continue
        # remaining distance after move (lower better)
        rem = ns - (0 if ns is None else 0)
        # Also compute our distance to target and opponent's distance to target from the new position is not needed;
        # instead use opponent's current distance as a tie-break proxy, then lexicographic for determinism.
        od = dO[best_rx][best_ry]
        key = (ns, od, nx, ny)
        # choose move with smallest ns; if ns equal, prefer move that keeps us closer