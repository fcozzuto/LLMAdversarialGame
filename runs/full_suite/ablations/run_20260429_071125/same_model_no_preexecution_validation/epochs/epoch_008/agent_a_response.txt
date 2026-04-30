def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    rem = observation.get("remaining_resource_count", len(resources))
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def valid(x, y): return inb(x, y) and (x, y) not in obstacles
    INF = 10**9
    def bfs(st):
        dist = [[INF]*h for _ in range(w)]
        x0, y0 = st
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
    ds = bfs((sx, sy))
    do = bfs((ox, oy))

    # If no resources/endgame: move to maximize safety (distance from opponent), prefer keeping within bounds
    if not resources or rem <= 0:
        bestv = -INF; best = (0, 0)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny): continue
            v = do[nx][ny]
            # break ties by closeness to center to avoid corners trapping
            v += -abs(nx - (w-1)/2) - abs(ny - (h-1)/2) * 0.01
            if v > bestv:
                bestv = v; best = (dx, dy)
        return [best[0], best[1]]

    # Pick a resource to contest: minimize my distance, but if I can be outpaced, prefer resources I can reach first
    best_t = None; best_key = None
    for r in resources:
        rx, ry = r
        if not valid(rx, ry): continue
        myd = ds[rx][ry]; opd = do[rx][ry]
        if myd >= INF: continue
        # Key: myd first; then prefer where I arrive much earlier than opponent; then far from opponent
        key = (myd, max(-opd, 0) * -1, -opd)
        if best_key is None or key < best_key:
            best_key = key; best_t = (rx, ry)

    if best_t is None:
        return [0, 0]
    tx, ty = best_t

    # Choose move that improves my path to target, while not stepping into a cell where opponent is too close
    bestv = -INF; best = (0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny): continue
        myd = ds[nx][ny]
        # progress toward target: myd + distance-from-target as proxy via BFS of target isn't available; use myd toward target by comparing ds at target
        # Better: estimate opponent pressure by comparing distances to target
        my_to_t = ds[tx][ty]
        opp_to_t = do[tx][ty]
        # immediate pressure: opponent distance to our new cell
        pressure = do[nx][ny]
        # value combines: reduce ds to target (via ds at current? still okay), and avoid being near opponent
        v = -myd
        v += 0.25 * pressure  # prefer cells farther from opponent
        # if opponent is already closer to the target, weight staying away more
        if opp_to_t < my_to_t:
            v += 0.6 * pressure
        else:
            v += 0.2 * pressure
        # small deterministic tie-break: toward target using Chebyshev
        v += -max(abs(nx - tx), abs(ny - ty)) * 0.01
        if v > bestv:
            bestv = v;