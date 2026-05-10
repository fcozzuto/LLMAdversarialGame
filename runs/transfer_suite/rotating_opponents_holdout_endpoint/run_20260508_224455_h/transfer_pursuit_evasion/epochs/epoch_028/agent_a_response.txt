def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obs = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    role = (observation.get("self_role") or "").lower()
    pursuer = ("pursuer" in role) or ("pursue" in role) or ("chaser" in role) or ("pursuit" in role)
    evader = ("evader" in role) or ("evade" in role) or ("runner" in role) or ("escape" in role)
    if evader:
        pursuer = False
    if not evader and not pursuer:
        # Fallback: if unspecified, behave as pursuer to pressure opponent.
        pursuer = True

    deltas = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    moves = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs:
            moves.append((dx, dy, nx, ny))

    def bfs_dist(start, goal):
        if start == goal:
            return 0
        qx, qy = [start[0]], [start[1]]
        dist = [[-1]*h for _ in range(w)]
        dist[start[0]][start[1]] = 0
        qi = 0
        while qi < len(qx):
            x, y = qx[qi], qy[qi]
            qi += 1
            nd = dist[x][y] + 1
            for ddx, ddy in ((1,0),(-1,0),(0,1),(0,-1),(1,1),(1,-1),(-1,1),(-1,-1)):
                nx, ny = x + ddx, y + ddy
                if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs and dist[nx][ny] == -1:
                    if (nx, ny) == goal:
                        return nd
                    dist[nx][ny] = nd
                    qx.append(nx); qy.append(ny)
        return 10**9

    best_move = [0, 0]
    best_val = None
    for dx, dy, nx, ny in moves:
        d = bfs_dist((nx, ny), (ox, oy))
        # small tie-breakers keep determinism and avoid oscillation into edges
        edge_pen = (min(nx, w-1-nx) + min(ny, h-1-ny))
        cheb = max(abs(nx-ox), abs(ny-oy))
        val = (-d, -(cheb), edge_pen) if pursuer else (d, cheb, -edge_pen)
        if best_val is None or val > best_val:
            best_val = val
            best_move = [dx, dy]

    return best_move if best_move in ([d[0], d[1]] for d in deltas) else [0, 0]