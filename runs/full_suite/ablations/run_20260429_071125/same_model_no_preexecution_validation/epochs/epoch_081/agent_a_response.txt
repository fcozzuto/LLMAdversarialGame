def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = map(int, observation.get("self_position", [0, 0]))
    ox, oy = map(int, observation.get("opponent_position", [0, 0]))
    resources = observation.get("resources") or []
    obs_list = observation.get("obstacles") or []
    obstacles = set((int(p[0]), int(p[1])) for p in obs_list)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    INF = 10**9

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def valid(x, y):
        return inb(x, y) and (x, y) not in obstacles

    def bfs(x0, y0):
        dist = [[INF] * h for _ in range(w)]
        if not valid(x0, y0):
            return dist
        dist[x0][y0] = 0
        qx = [x0]
        qy = [y0]
        qi = 0
        while qi < len(qx):
            x, y = qx[qi], qy[qi]
            qi += 1
            nd = dist[x][y] + 1
            for dx, dy in moves:
                nx, ny = x + dx, y + dy
                if valid(nx, ny) and nd < dist[nx][ny]:
                    dist[nx][ny] = nd
                    qx.append(nx)
                    qy.append(ny)
        return dist

    dS = bfs(sx, sy)
    dO = bfs(ox, oy)

    best_r = None
    best_sc = -INF
    for r in resources:
        rx, ry = int(r[0]), int(r[1])
        if not valid(rx, ry):
            continue
        ds, do = dS[rx][ry], dO[rx][ry]
        if ds >= INF or do >= INF:
            continue
        # Prefer resources we can reach earlier, then further advantage, then nearer for tie-break.
        sc = (do - ds) * 10 - ds - (abs(rx - ox) + abs(ry - oy)) * 0.001
        if sc > best_sc:
            best_sc = sc
            best_r = (rx, ry, ds, do)

    if best_r is None:
        # No reachable resources: drift to a corner-near-center-ish deterministic direction.
        dx, dy = (1 if sx < w // 2 else -1 if sx > w // 2 else 0), (1 if sy < h // 2 else -1 if sy > h // 2 else 0)
        nx, ny = sx + dx, sy + dy
        return [dx, dy] if valid(nx, ny) else [0, 0]

    rx, ry, ds_target, _ = best_r

    # Move to reduce self distance to target; if tie, increase opponent distance.
    best_move = (0, 0)
    best_val = INF
    best_opp = -INF
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        ns = dS[nx][ny]
        if ns >= INF:
            continue
        no = dO[nx][ny]
        val = ns
        if val < best_val or (val == best_val and no > best_opp) or (val == best_val and no == best_opp and (dx, dy) < best_move):
            best_val = val
            best_opp = no
            best_move = (dx, dy)

    if best_val == INF:
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]