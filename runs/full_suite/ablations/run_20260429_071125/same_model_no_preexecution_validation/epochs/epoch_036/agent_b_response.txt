def choose_move(observation):
    w = int(observation["grid_width"]); h = int(observation["grid_height"])
    sx, sy = int(observation["self_position"][0]), int(observation["self_position"][1])
    ox, oy = int(observation["opponent_position"][0]), int(observation["opponent_position"][1])
    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles") or []))
    resources = observation.get("resources") or []
    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    INF = 10**9

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def valid(x, y): return inb(x, y) and (x, y) not in obstacles

    def bfs(x0, y0):
        dist = [[INF] * h for _ in range(w)]
        if not valid(x0, y0): return dist
        dist[x0][y0] = 0
        qx = [x0]; qy = [y0]; qi = 0
        while qi < len(qx):
            x = qx[qi]; y = qy[qi]; qi += 1
            nd = dist[x][y] + 1
            for dx, dy in moves:
                nx, ny = x + dx, y + dy
                if valid(nx, ny) and nd < dist[nx][ny]:
                    dist[nx][ny] = nd
                    qx.append(nx); qy.append(ny)
        return dist

    distS = bfs(sx, sy)
    distO = bfs(ox, oy)

    best = None
    best_score = -INF
    for r in resources:
        rx, ry = int(r[0]), int(r[1])
        if not valid(rx, ry): 
            continue
        ds, do = distS[rx][ry], distO[rx][ry]
        if ds >= INF and do >= INF: 
            continue
        # prefer our earlier arrival; if tie, pick where opponent is later; otherwise target where we can beat them
        score = 0
        if ds < INF: score += 200 - 5 * ds
        if do < INF:
            score += 60 * (1 if ds < do else 0)
            if ds == do: score += 10
            if ds > do: score -= 80 + 3 * (ds - do)
            score += 8 * (do - ds) if ds < do else -4 * (ds - do)
        # deterministic tie-break by coordinates
        score += -0.001 * (rx + 0.01 * ry)
        if score > best_score:
            best_score = score
            best = (rx, ry, ds, do)

    if best is None:
        # fallback: move that increases distance from opponent (deterministic)
        bestm = (0, 0); bestd = -INF
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny): 
                continue
            dd = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
            if dd > bestd:
                bestd = dd; bestm = (dx, dy)
        return [bestm[0], bestm[1]]

    rx, ry, ds, do = best
    if ds == 0:
        # already on target
        return [0, 0]

    # choose next step toward target, while discouraging opponent
    bestm = (0, 0); best_cost = INF; best_adv = -INF
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny): 
            continue
        if distS[nx][ny] >= INF:
            continue
        cost = distS[nx][ny]
        adv = distO[nx][ny] - distO[rx][ry]  # deterministic ordering proxy
        # primary: smaller distance to target; secondary: larger opponent distance at the step
        if cost < best_cost or (cost == best_cost and distO[nx][ny] > distO[sx][sy]) or (cost == best_cost and distO[nx][ny] == distO[sx][sy] and adv > best_adv):
            best_cost = cost
            best_adv = adv
            bestm = (dx, dy)

    return [bestm[0], bestm[1]]