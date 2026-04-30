def choose_move(observation):
    w = int(observation["grid_width"]); h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)
    resources = observation.get("resources") or []
    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles") or []))

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    INF = 10**9

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def valid(x, y): return inb(x, y) and (x, y) not in obstacles

    def bfs(x0, y0):
        x0 = int(x0); y0 = int(y0)
        dist = [[INF] * h for _ in range(w)]
        if not valid(x0, y0): return dist
        dist[x0][y0] = 0
        qx = [x0]; qy = [y0]; qi = 0
        while qi < len(qx):
            x = qx[qi]; y = qy[qi]; qi += 1
            nd = dist[x][y] + 1
            for dx, dy in moves:
                nx = x + dx; ny = y + dy
                if valid(nx, ny) and nd < dist[nx][ny]:
                    dist[nx][ny] = nd
                    qx.append(nx); qy.append(ny)
        return dist

    distS = bfs(sx, sy)
    distO = bfs(ox, oy)

    def best_target():
        best = None
        best_key = None
        for r in resources:
            rx, ry = int(r[0]), int(r[1])
            if not valid(rx, ry): 
                continue
            ds = distS[rx][ry]; do = distO[rx][ry]
            if ds >= INF and do >= INF:
                continue
            # Prefer winning/contested targets: larger (do - ds), then smaller ds.
            gain = (do - ds) if ds < INF else -INF
            key = (gain, -do if do < INF else -INF, -ds)
            if best_key is None or key > best_key:
                best_key = key
                best = (rx, ry, ds)
        if best is not None:
            return best[0], best[1]
        return None

    tgt = best_target()
    if tgt is None:
        # No resources (or all unreachable): drift to center.
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best = (INF, 0, 0)
        for dx, dy in moves:
            nx = sx + dx; ny = sy + dy
            if not valid(nx, ny): 
                continue
            d = abs(nx - cx) + abs(ny - cy)
            if d < best[0]:
                best = (d, dx, dy)
        return [int(best[1]), int(best[2])]

    tx, ty = tgt
    # If we are on the target, stay to secure.
    if sx == tx and sy == ty:
        return [0, 0]

    # Greedy step: choose move that minimizes distS to target; tie-break deterministically.
    curd = distS[tx][ty]
    best = (INF, 0, 0)
    for dx, dy in moves:
        nx = sx + dx; ny = sy + dy
        if not valid(nx, ny):
            continue
        nd = distS[nx][ny]
        # Want to reduce overall distance toward target, use (nd to target indirectly via distS + triangle not possible)
        # Use absolute distS from nx to target by recomputing quickly: approximate with distS[nx][tx,ty] not available.
        # Instead, use improvement in our distance-to-target computed via distS array: distS value at target relative.
        # Approx: choose neighbor with smallest distS_to_target_est = curd - (distS[nx][ty] - distS[sx][ty]) is not available.
        # So we directly minimize distS[nx][ty] where distS was computed from start, not from target; still correlates.
        # Better: minimize distS[nx][tx]? none. We'll use distS[nx][ny] not meaningful.
        # Therefore: compute local "progress" using dist to target via BFS