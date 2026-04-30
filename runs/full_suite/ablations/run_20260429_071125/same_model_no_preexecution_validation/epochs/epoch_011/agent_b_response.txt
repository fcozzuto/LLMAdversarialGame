def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles_list = observation.get("obstacles", []) or []
    obstacles = set((p[0], p[1]) for p in obstacles_list)

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    INF = 10**9

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def valid(x, y):
        return inb(x, y) and (x, y) not in obstacles

    def bfs(start):
        dist = [[INF] * h for _ in range(w)]
        x0, y0 = start
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

    # If no resources, just stay safe (deterministic)
    if not resources:
        return [0, 0]

    ds = bfs((sx, sy))
    do = bfs((ox, oy))

    # Choose target that maximizes winning margin (opponent slower than self)
    best_r = None
    best_key = -10**18
    for rx, ry in resources:
        d1 = ds[rx][ry]
        d2 = do[rx][ry]
        if d1 >= INF:
            continue
        if d2 >= INF:
            key = 10**6 - d1
        else:
            key = (d2 - d1) * 100 - d1
        # tiny deterministic tie-break: prefer smaller coords
        key = key - (rx * 0.001 + ry * 0.000001)
        if key > best_key:
            best_key = key
            best_r = (rx, ry)

    if best_r is None:
        return [0, 0]
    tx, ty = best_r

    # Move to neighbor that most reduces distance to target; tie-break deterministically
    best_move = (0, 0)
    best_dist = INF
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d = ds[nx][ny]
        # If ds distances not meaningful for target cell, use direct step heuristic to (tx,ty)
        # (ds[x][y] holds distance from start to that cell, not to target)
        # So we compute heuristic: Chebyshev distance to target
        # Deterministically also prefer avoiding proximity to opponent when margins are small.
        hdist = max(abs(tx - nx), abs(ty - ny))
        opp_step = max(abs(ox - nx), abs(oy - ny))
        # Primary: reduce remaining heuristic distance to target
        # Secondary: prefer cells that are "ahead" in race: smaller ds to target isn't available,
        # so approximate using (margin proxy) via step towards target and away from opponent.
        key = (hdist * 10000 + opp_step) + (0 if (dx, dy) == (0, 0) else 0)
        # Convert to minimization; store best by key and also ensure valid
        if key < (best_dist if best_move != (0,0) else INF):
            best_dist = key
            best_move = (dx, dy)

    # Additional deterministic correction if best_move invalid (shouldn't happen)
    dx, dy = best_move
    if not valid(sx + dx, sy + dy):
        return [0, 0]
    return [dx, dy]