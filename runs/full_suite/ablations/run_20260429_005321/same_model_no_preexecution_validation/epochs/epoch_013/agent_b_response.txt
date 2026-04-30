def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))
    dirs = [(-1,-1), (-1,0), (-1,1), (0,-1), (0,0), (0,1), (1,-1), (1,0), (1,1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    INF = 10**9

    def bfs(start):
        x0, y0 = start
        dist = [[INF] * w for _ in range(h)]
        if not inb(x0, y0) or (x0, y0) in obstacles:
            return dist
        dist[y0][x0] = 0
        qx = [x0]; qy = [y0]; qi = 0
        while qi < len(qx):
            x = qx[qi]; y = qy[qi]; qi += 1
            nd = dist[y][x] + 1
            for dx, dy in dirs:
                nx, ny = x + dx, y + dy
                if inb(nx, ny) and (nx, ny) not in obstacles and nd < dist[ny][nx]:
                    dist[ny][nx] = nd
                    qx.append(nx); qy.append(ny)
        return dist

    myd = bfs((sx, sy))
    opd = bfs((ox, oy))

    # pick best reachable resource by "lead": opponent farther than me
    best = None
    for rx, ry in resources:
        md = myd[ry][rx]
        if md >= INF:
            continue
        od = opd[ry][rx]
        lead = (od - md)  # higher is better for me
        # tie-break deterministically by resource position then by md
        key = (lead, -od, -md, -rx, -ry)
        if best is None or key > best[0]:
            best = (key, rx, ry)

    # choose a move that heads toward the chosen target if possible
    if best is not None:
        _, tx, ty = best
        cur = myd[sy][sx]
        # greedy: among valid moves, minimize distance to target while staying safe
        bestmv = None
        bestscore = None
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            nd = myd[ny][nx]
            if nd >= INF:
                continue
            # primary: get closer (smaller nd) to reachability; secondary: prefer progressing toward target by nd<=cur and lower nd
            score = (nd, abs(tx - nx) + abs(ty - ny), abs(tx - (sx + dx)) + abs(ty - (sy + dy)))
            if bestscore is None or score < bestscore:
                bestscore = score
                bestmv = (dx, dy)
        if bestmv is not None:
            return [int(bestmv[0]), int(bestmv[1])]

    # fallback: avoid obstacles; move toward opponent's closest resource attractor (or toward center if none)
    # compute a deterministic safe move that reduces my distance to "best reachable cell" under a simple potential
    safe_moves = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles and myd[ny][nx] < INF:
            safe_moves.append((dx, dy, nx, ny))
    if not safe_moves:
        return [0, 0]

    # potential: prefer being closer to nearest resource, but only if it doesn't help opponent too much (deterministic)
    bestm = None
    bestv = None
    for dx, dy, nx, ny in safe_moves:
        # evaluate locally using a small deterministic function: compare distances to resources
        best_lead = -10**9
        for rx, ry in resources:
            md = myd[ry][rx]; od = opd[ry][rx]
            if md >= INF or od >= INF:
                continue
            lead = od - md
            if lead > best_lead:
                best_lead = lead
        # also encourage moving toward higher lead cells by our proximity
        dist_to_center = abs((w-1)/2 - nx) + abs