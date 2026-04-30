def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = {(p[0], p[1]) for p in obstacles}

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def blocked(x, y): return (not inb(x, y)) or ((x, y) in obs)

    if not resources or blocked(sx, sy):
        return [0, 0]

    dirs = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    INF = 10**9

    def bfs(start):
        if blocked(start[0], start[1]): return None
        dist = [[INF]*w for _ in range(h)]
        dist[start[1]][start[0]] = 0
        qx = [start[0]]; qy = [start[1]]; qi = 0
        while qi < len(qx):
            x, y = qx[qi], qy[qi]; qi += 1
            nd = dist[y][x] + 1
            for dx, dy in dirs:
                nx, ny = x + dx, y + dy
                if not blocked(nx, ny) and nd < dist[ny][nx]:
                    dist[ny][nx] = nd
                    qx.append(nx); qy.append(ny)
        return dist

    myd = bfs((sx, sy))
    opd = bfs((ox, oy)) if not blocked(ox, oy) else None
    if myd is None:
        return [0, 0]
    if opd is None:
        opd = [[INF]*w for _ in range(h)]

    # Choose resource that we can reach and keep opponent behind.
    best = None
    best_score = -10**18
    for rx, ry in resources:
        d_me = myd[ry][rx]
        d_op = opd[ry][rx]
        if d_me >= INF: 
            continue
        # Advantage: prefer being earlier; if both unreachable for opp, still take nearest.
        score = (d_op - d_me) * 1000 - d_me
        # Small tie-break to prefer staying away from edges (more stable paths).
        center_bonus = -(abs(rx - (w-1)/2) + abs(ry - (h-1)/2))
        score += center_bonus
        if score > best_score:
            best_score = score
            best = (rx, ry)

    if best is None:
        return [0, 0]
    tx, ty = best

    # Take one step that minimizes distance-to-target while staying valid.
    curd = myd[sy][sx]
    best_move = [0, 0]
    best_nd = curd
    # Deterministic tie-breaking: fixed dir order.
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if blocked(nx, ny):
            continue
        nd = myd[ny][nx]
        if nd < best_nd:
            best_nd = nd
            best_move = [dx, dy]
        elif nd == best_nd:
            if [dx, dy] < best_move:
                best_move = [dx, dy]

    # If somehow all moves don't improve (rare), go to neighbor with smallest distance to target.
    if best_move == [0, 0]:
        min_d = curd
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if blocked(nx, ny): 
                continue
            # distance to target equals myd_from_neighbor? can't; use BFS dist by recomputing target heuristic with chebyshev
            # But must be deterministic and cheap: minimize Chebyshev to target.
            cand = max(abs(nx - tx), abs(ny - ty))
            if cand < max(abs(sx - tx), abs(sy - ty)):
                best_move = [dx, dy]
                break

    return best_move