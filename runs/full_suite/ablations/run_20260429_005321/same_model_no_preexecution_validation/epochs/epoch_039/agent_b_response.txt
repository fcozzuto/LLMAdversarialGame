def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))
    dirs = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def bfs(start):
        x0, y0 = start
        if not inb(x0, y0) or (x0, y0) in obstacles: return None
        INF = 10**9
        dist = [[INF]*w for _ in range(h)]
        dist[y0][x0] = 0
        qx = [x0]; qy = [y0]; qi = 0
        while qi < len(qx):
            x = qx[qi]; y = qy[qi]; qi += 1
            d = dist[y][x] + 1
            for dx, dy in dirs:
                nx, ny = x + dx, y + dy
                if inb(nx, ny) and (nx, ny) not in obstacles and d < dist[ny][nx]:
                    dist[ny][nx] = d
                    qx.append(nx); qy.append(ny)
        return dist
    myd = bfs((sx, sy))
    opd = bfs((ox, oy))
    if myd is None or opd is None or not resources:
        return [0, 0]

    best = None; best_score = -10**18
    for r in resources:
        rx, ry = r[0], r[1]
        if not inb(rx, ry) or (rx, ry) in obstacles: 
            continue
        md = myd[ry][rx]; od = opd[ry][rx]
        if md >= 10**9 or od >= 10**9:
            continue
        score = (od - md) * 3 - md - (0 if od >= md else (md - od) * 5)
        if (rx + ry) % 2 == 0:
            score += 0.2  # deterministic tie-break preference
        if score > best_score:
            best_score = score
            best = (rx, ry)

    if best is None:
        return [0, 0]
    tx, ty = best

    best_move = [0, 0]
    best_val = 10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            nx, ny = sx, sy
        md2 = myd[ny][nx] if myd else 10**9
        od2 = opd[ny][tx] if opd else 10**9  # approximate opponent pressure after we move
        # Prefer getting closer; avoid moving into opponent's advantageous zones.
        val = md2 * 10 - (od2 - myd[ty][tx]) * 1.5
        # Strongly discourage if opponent can reach target sooner (unless we also are very close)
        if opd and opd[ty][tx] < myd[ty][tx] and md2 > 2:
            val += 50 + md2
        if val < best_val:
            best_val = val
            best_move = [dx, dy]
    return best_move