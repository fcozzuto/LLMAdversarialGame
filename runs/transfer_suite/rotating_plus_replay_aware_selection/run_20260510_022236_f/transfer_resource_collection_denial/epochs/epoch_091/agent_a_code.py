def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = {(int(x), int(y)) for x, y in obstacles}
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def bfs_from(start):
        sx0, sy0 = start
        INF = 10**9
        dist = [[INF] * w for _ in range(h)]
        if not inb(sx0, sy0) or (sx0, sy0) in obs:
            return dist
        dist[sy0][sx0] = 0
        q = [(sx0, sy0)]
        qi = 0
        dirs = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
        while qi < len(q):
            x, y = q[qi]; qi += 1
            d0 = dist[y][x] + 1
            for dx, dy in dirs:
                nx, ny = x + dx, y + dy
                if inb(nx, ny) and (nx, ny) not in obs and d0 < dist[ny][nx]:
                    dist[ny][nx] = d0
                    q.append((nx, ny))
        return dist
    dself = bfs_from((sx, sy))
    dob = bfs_from((ox, oy))
    best = None
    for rx, ry in resources:
        rx, ry = int(rx), int(ry)
        if not inb(rx, ry) or (rx, ry) in obs:
            continue
        ds = dself[ry][rx]
        do = dob[ry][rx]
        if ds >= 10**9:
            continue
        lead = do - ds
        # Prefer winning lead; then closer; then stable tie-break toward center-ish
        y_pref = -abs(ry - (h - 1) / 2.0)
        score = (lead, -ds, y_pref)
        if best is None or score > best[0]:
            best = (score, rx, ry, ds)
    if best is None:
        return [0, 0]
    _, tx, ty, _ = best
    # Choose next move that minimizes our distance to target (with deterministic tie-break)
    dirs = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    beststep = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        nd = dself[ny][nx]
        if nd >= 10**9:
            continue
        # Tie-break: first minimize nd, then maximize lead to target using opponent dist
        lead_now = dob[ty][tx] - nd
        key = (-nd, -lead_now, -abs((nx - tx)) - abs((ny - ty)))
        if beststep is None or key > beststep[0]:
            beststep = (key, dx, dy)
    if beststep is None:
        return [0, 0]
    return [int(beststep[1]), int(beststep[2])]