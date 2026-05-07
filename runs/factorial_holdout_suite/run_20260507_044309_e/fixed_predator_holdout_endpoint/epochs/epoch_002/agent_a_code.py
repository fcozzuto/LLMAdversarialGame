def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation["resources"]
    obstacles = set(tuple(o) for o in observation["obstacles"])

    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    INF = 10**9

    def bfs(start):
        dist = [[INF]*h for _ in range(w)]
        dist[start[0]][start[1]] = 0
        qx = [start[0]]; qy = [start[1]]; qi = 0
        while qi < len(qx):
            x = qx[qi]; y = qy[qi]; qi += 1
            nd = dist[x][y] + 1
            for dx, dy in moves:
                nx, ny = x + dx, y + dy
                if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles and dist[nx][ny] > nd:
                    dist[nx][ny] = nd
                    qx.append(nx); qy.append(ny)
        return dist

    dist_s = bfs((sx, sy))
    dist_o = bfs((ox, oy))

    best = None
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        ds = dist_s[rx][ry]
        if ds >= INF:
            continue
        do = dist_o[rx][ry]
        adv = do - ds  # positive means we are closer
        # Prefer being ahead strongly; otherwise chase soonest but slightly prefer cells that are not too bad vs opponent.
        key = (-adv if adv > 0 else (ds), abs(adv) if adv > 0 else 2*do - ds, ds, rx, ry)
        if best is None or key < best[0]:
            best = (key, (rx, ry), ds, do)
    if best is None:
        # Fallback: move to reduce distance to opponent's position (avoid being static-guarded)
        tx, ty = ox, oy
    else:
        _, (tx, ty), _, _ = best

    cur_ds = dist_s[tx][ty]
    best_move = [0, 0]
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue
        nds = dist_s[nx][ny]
        # We want to get closer to target (small dist to target), and if possible widen advantage vs opponent.
        # Use dist to target from the neighbor via dist_s[tx][ty] is constant, so compare neighbor-to-target estimated by dist_s.
        # Since dist_s is from self, we can't get exact neighbor->target; approximate by greedy toward target using dx/dy alignment plus ds to target.
        align = (1 if (tx - nx)*(tx - sx) >= 0 else 0) + (1 if (ty - ny)*(ty - sy) >= 0 else 0)
        # Also penalize moving away from opponent in a denier setting? We'll instead avoid being intercepted: prefer higher (dist_o to target - dist_s to target) indirectly using current dist_s cell.
        # Approximate by preferring moves that reduce dist_s from self to target if possible: use heuristic distance from nx,ny to target by Chebyshev (diagonal allowed).
        greedy_to_target = max(abs(tx - nx), abs(ty - ny))
        opp_greedy = max(abs(tx - ox), abs(ty - oy))
        key = (greedy_to_target, greedy_to_target - (opp_greedy - cur_ds), -align, nds, nx, ny)
        if best_key is None or key < best_key:
            best_key = key
            best_move = [dx, dy]
    return best_move