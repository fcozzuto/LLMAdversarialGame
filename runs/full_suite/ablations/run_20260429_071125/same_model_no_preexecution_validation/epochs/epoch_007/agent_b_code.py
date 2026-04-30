def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def valid(x, y): return inb(x, y) and (x, y) not in obstacles

    def bfs_from(st):
        INF = 10**9
        dist = [[INF]*h for _ in range(w)]
        x0, y0 = st
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

    ds = bfs_from((sx, sy))
    do = bfs_from((ox, oy))

    rem = observation.get("remaining_resource_count", len(resources))
    resources = [tuple(r) for r in resources]
    if not resources or rem <= 0:
        best = (-(10**9), 0, 0, 0)
        bestmv = (0, 0)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny): continue
            d = max(abs(nx - ox), abs(ny - oy))
            adv = -max(abs(nx - sx), abs(ny - sy))  # small tie-break
            key = (d, adv, nx, ny)
            if key > best:
                best = key; bestmv = (dx, dy)
        return [bestmv[0], bestmv[1]]

    # Pick a resource we can reach no later than opponent, maximizing margin and closeness.
    best_target = None
    best_key = None
    for rx, ry in resources:
        a = ds[rx][ry]; b = do[rx][ry]
        if a >= 10**9: 
            continue
        # Encourage taking resources likely secured; if none, still choose minimizing our distance.
        margin = b - a  # positive is good (we arrive earlier or equal)
        # Small extra: prefer being closer to it and away from opponent (tends to deny).
        key = (margin, -a, -max(abs(rx - ox), abs(ry - oy)), rx, ry)
        if best_key is None or key > best_key:
            best_key = key; best_target = (rx, ry)

    tx, ty = best_target
    # Move to neighbor that best advances toward chosen target, with slight denial against opponent.
    best_key = None
    bestmv = (0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny): continue
        myd = ds[nx][ny]
        # Use Chebyshev as a tie-break toward target (diagonal-friendly).
        cheb_to_t = max(abs(nx - tx), abs(ny - ty))
        cheb_from_o = max(abs(nx - ox), abs(ny - oy))
        # prefer lower distance-to-target; also prefer states where opponent is farther.
        key = (-cheb_to_t, -cheb_from_o, -myd, nx, ny)
        if best_key is None or key > best_key:
            best_key = key; bestmv = (dx, dy)
    return [bestmv[0], bestmv[1]]