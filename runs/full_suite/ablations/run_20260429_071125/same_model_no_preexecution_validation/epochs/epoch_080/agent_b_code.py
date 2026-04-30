def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = map(int, observation.get("self_position", [0, 0]))
    ox, oy = map(int, observation.get("opponent_position", [0, 0]))
    resources = observation.get("resources") or []
    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles") or []))
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    INF = 10**9

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def valid(x, y): return inb(x, y) and (x, y) not in obstacles

    def bfs(x0, y0):
        dist = [[INF] * h for _ in range(w)]
        if not valid(x0, y0): return dist
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

    dS = bfs(sx, sy)
    dO = bfs(ox, oy)

    best = None
    best_key = None
    for r in resources:
        rx, ry = int(r[0]), int(r[1])
        if not valid(rx, ry): continue
        ds, do = dS[rx][ry], dO[rx][ry]
        if ds >= INF or do >= INF: continue
        # primary: we want earlier than opponent; secondary: also far from opponent and close to us
        key = (-(ds < do), (do - ds), -(ds), -abs(rx - (w - 1) / 2) - abs(ry - (h - 1) / 2))
        if best_key is None or key > best_key:
            best_key, best = key, (rx, ry)

    if best is None:
        tx, ty = (w - 1) // 2, (h - 1) // 2
    else:
        tx, ty = best

    cur_ds = dS[sx][sy]
    cur_do = dO[sx][sy]
    best_move = (0, 0)
    best_score = -INF

    # choose move to get closer to target while also improving our race vs opponent on same target
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny): continue
        nds, ndo = dS[nx][ny], dO[nx][ny]
        # local approximation: prefer smaller ds_next to target and larger (do - ds) at target
        if best is not None:
            tds, tdo = dS[tx][ty], dO[tx][ty]
            # approximate change by comparing distances from next cell to target
            # (use triangle-like proxy via delta in our distance maps to target)
            # Since we only have dist from start positions, we approximate by using our dist-to-target by BFS from next cell would be costly.
            # Instead: maximize our improvement over current at same target using current ds/target ds and our overall position (works reasonably).
            # Use: (tdo - tds) favors contest; slight nudge to reduce our own distance-to-target via nds.
            score = (tdo - tds) * 100 - nds * 3 - ndo * 1
        else:
            score = -((nx - tx) * (nx - tx) + (ny - ty) * (ny - ty)) - nds + cur_ds - ndo
        if dx == 0 and dy == 0 and best is not None and (cur_do - cur_ds) < 0:
            score -= 5  # avoid staying when likely behind
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]