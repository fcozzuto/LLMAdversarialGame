def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def valid(x, y): return inb(x, y) and (x, y) not in obstacles

    def bfs(startx, starty):
        inf = 10**9
        dist = [[inf]*w for _ in range(h)]
        if not valid(startx, starty):
            return dist
        qx, qy, qi = [startx], [starty], 0
        dist[starty][startx] = 0
        while qi < len(qx):
            x, y = qx[qi], qy[qi]
            qi += 1
            d = dist[y][x] + 1
            for dx, dy in dirs:
                nx, ny = x + dx, y + dy
                if valid(nx, ny) and d < dist[ny][nx]:
                    dist[ny][nx] = d
                    qx.append(nx); qy.append(ny)
        return dist

    if not resources:
        tx, ty = w - 1, h - 1
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        nx, ny = sx + dx, sy + dy
        return [dx, dy] if valid(nx, ny) else [0, 0]

    self_dmap = bfs(sx, sy)
    opp_dmap = bfs(ox, oy)

    best = None
    best_key = None
    for rx, ry in resources:
        sd = self_dmap[ry][rx]
        od = opp_dmap[ry][rx]
        if sd >= 10**9: 
            continue
        key = (od - sd, -sd, od)
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)
    if best is None:
        return [0, 0]

    rx, ry = best
    sd0 = self_dmap[ry][rx]
    # If already at target (resource pickup), stay.
    if sx == rx and sy == ry:
        return [0, 0]

    # Move to neighbor that best reduces distance to the chosen target.
    best_step = (0, 0)
    best_sd = sd0
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        sd = self_dmap[ny][nx]
        # We want to approach target using exact shortest-distance monotonicity.
        if abs(sd0 - (sd + 1)) == 0 and sd < best_sd:
            best_sd = sd
            best_step = (dx, dy)

    if best_step == (0, 0):
        # Fallback: greedy by Manhattan if BFS monotonic wasn't usable (still deterministic).
        md_best = 10**9
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            m = abs(nx - rx) + abs(ny - ry)
            if m < md_best:
                md_best = m
                best_step = (dx, dy)
    return [int(best_step[0]), int(best_step[1])]