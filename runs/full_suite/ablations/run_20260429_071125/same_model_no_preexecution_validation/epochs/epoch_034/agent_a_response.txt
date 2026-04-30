def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
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
        if not valid(x0, y0):
            return dist
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
    best_key = None
    for r in resources:
        rx, ry = int(r[0]), int(r[1])
        if not valid(rx, ry):
            continue
        ds = distS[rx][ry]
        if ds >= INF:
            continue
        do = distO[rx][ry]
        # Prefer resources we can reach sooner; penalize those opponent can reach earlier.
        # Key: (advantage, -self_speed, tie_break)
        do_eff = do if do < INF else INF
        key = (do_eff - ds, -ds, rx, ry)
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)

    if best is None:
        # Fallback: move to reduce distance to the nearest resource ignoring opponent.
        # Deterministically head away from opponent if no resources.
        if resources:
            nearest = None
            nearest_d = INF
            for r in resources:
                rx, ry = int(r[0]), int(r[1])
                d = distS[rx][ry]
                if d < nearest_d:
                    nearest_d = d
                    nearest = (rx, ry)
            best = nearest
        else:
            # No resources visible: drift toward center if possible; else stay.
            targets = [(w//2, h//2), (w//2, h//2-1), (w//2-1, h//2)]
            for t in targets:
                tx, ty = t
                if valid(tx, ty) and distS[tx][ty] < INF:
                    best = (tx, ty)
                    break
            if best is None:
                return [0, 0]

    tx, ty = best
    curd = distS[tx][ty]
    if curd >= INF:
        return [0, 0]

    # Choose neighbor with strictly decreasing distance; tie-break by dx,dy order.
    best_step = None
    best_step_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        if distS[nx][ny] + 1 == curd or distS[nx][ny] < distS[sx][sy]:
            # Prefer closer to target and slightly away from opponent.
            step_adv = (abs(nx - tx) + abs(ny - ty))
            step_opp = abs(nx - ox) + abs(ny - oy)
            key = (-step_adv, step_opp, dx, dy)
            if best_step_key is None or key > best_step_key:
                best_step_key = key
                best_step = (dx, dy)

    if best_step is None:
        # Last resort: stay still
        return [0, 0]
    return [int(best_step[