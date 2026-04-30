def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obst_list = observation.get("obstacles") or []
    obstacles = set((p[0], p[1]) for p in obst_list)
    dirs = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    INF = 10**9

    def inb(x, y): return 0 <= x < w and 0 <= y < h

    def bfs(start):
        x0, y0 = start
        if not inb(x0, y0) or (x0, y0) in obstacles: return None
        dist = [[INF] * w for _ in range(h)]
        dist[y0][x0] = 0
        q = [(x0, y0)]
        qi = 0
        while qi < len(q):
            x, y = q[qi]; qi += 1
            nd = dist[y][x] + 1
            for dx, dy in dirs:
                nx, ny = x + dx, y + dy
                if inb(nx, ny) and (nx, ny) not in obstacles and nd < dist[ny][nx]:
                    dist[ny][nx] = nd
                    q.append((nx, ny))
        return dist

    myd = bfs((sx, sy))
    opd = bfs((ox, oy))
    if myd is None or opd is None:
        return [0, 0]

    best = None
    best_score = -INF
    for rx, ry in resources:
        if not inb(rx, ry) or (rx, ry) in obstacles:
            continue
        md = myd[ry][rx]; od = opd[ry][rx]
        if md >= INF or od >= INF:
            continue
        # Prefer resources we reach earlier; also punish resources opponent can take sooner.
        score = (od - md) * 10 - md
        if best is None or score > best_score or (score == best_score and (rx, ry) < best):
            best = (rx, ry); best_score = score

    if best is None:
        # No reachable resources: drift toward the center while avoiding obstacles.
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        candidates = []
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                candidates.append((dx, dy, (nx - cx) ** 2 + (ny - cy) ** 2))
        if not candidates:
            return [0, 0]
        candidates.sort(key=lambda t: (t[2], t[0], t[1]))
        return [candidates[0][0], candidates[0][1]]

    tx, ty = best
    # Choose best valid one-step move that decreases distance to target; tie-break deterministically.
    best_step = (0, 0)
    best_val = INF
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        val = myd[ny][nx]
        # Encourage moving closer; if equal, prefer smaller move delta lexicographically.
        if val < best_val or (val == best_val and (dx, dy) < best_step):
            best_val = val; best_step = (dx, dy)

    return [int(best_step[0]), int(best_step[1])]