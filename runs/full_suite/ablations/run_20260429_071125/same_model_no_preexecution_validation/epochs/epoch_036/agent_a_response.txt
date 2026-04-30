def choose_move(observation):
    w = int(observation["grid_width"]); h = int(observation["grid_height"])
    sx, sy = int(observation["self_position"][0]), int(observation["self_position"][1])
    ox, oy = int(observation["opponent_position"][0]), int(observation["opponent_position"][1])

    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles") or []))
    resources = observation.get("resources") or []
    if not resources:
        return [0, 0]

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    INF = 10**9

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def valid(x, y): return inb(x, y) and (x, y) not in obstacles

    def bfs(x0, y0):
        dist = [[INF] * h for _ in range(w)]
        if not valid(x0, y0):
            return dist
        dist[x0][y0] = 0
        q = [(x0, y0)]
        qi = 0
        while qi < len(q):
            x, y = q[qi]; qi += 1
            nd = dist[x][y] + 1
            for dx, dy in moves:
                nx, ny = x + dx, y + dy
                if valid(nx, ny) and nd < dist[nx][ny]:
                    dist[nx][ny] = nd
                    q.append((nx, ny))
        return dist

    distS = bfs(sx, sy)
    distO = bfs(ox, oy)

    best = None
    best_key = None
    for r in resources:
        rx, ry = int(r[0]), int(r[1])
        ds = distS[rx][ry]; do = distO[rx][ry]
        if ds >= INF: 
            continue
        # Prefer winning/resource advantage; fallback to closeness
        adv = do - ds  # positive means we reach earlier than opponent
        key = (-(adv), ds, rx, ry) if adv != 0 else ((0), ds, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry)

    if best is None:
        return [0, 0]
    tx, ty = best

    # Choose move that decreases distance to target; if multiple, avoid letting opponent gain parity.
    cur_ds = distS[sx][sy]
    best_move = [0, 0]
    best_score = (INF, -INF, 0, 0)  # (next_ds, opp_ds_delta, -tx_align, tie)
    opp_cur = distO[sx][sy]  # opponent not here, but keep deterministic tie-breaking
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        nds = distS[nx][ny]
        if nds >= INF:
            continue
        # Opponent "pressure" if they can reach quickly from their current pos after a similar move
        # Use their current distance to target as proxy, since we can't predict their move deterministically.
        opp_to_target = distO[tx][ty]
        opp_from_n = distO[nx][ny]
        opp_delta = opp_cur - opp_from_n
        tx_align = (abs(tx - nx) - abs(tx - sx)) + (abs(ty - ny) - abs(ty - sy))
        score = (nds, opp_delta, -tx_align, 0)
        if score < best_score or (score == best_score and (dx, dy) < (best_move[0], best_move[1])):
            best_score = score
            best_move = [dx, dy]

    # If somehow all moves invalid, stay
    if best_move is None:
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]