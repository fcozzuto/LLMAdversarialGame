def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))
    dirs8 = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    INF = 10**9

    def bfs(start):
        x0, y0 = start
        dist = [[INF] * w for _ in range(h)]
        if not inb(x0, y0) or (x0, y0) in obstacles:
            return dist
        dist[y0][x0] = 0
        qx = [x0]; qy = [y0]; qi = 0
        while qi < len(qx):
            x = qx[qi]; y = qy[qi]; qi += 1
            nd = dist[y][x] + 1
            for dx, dy in dirs8:
                nx, ny = x + dx, y + dy
                if inb(nx, ny) and (nx, ny) not in obstacles and nd < dist[ny][nx]:
                    dist[ny][nx] = nd
                    qx.append(nx); qy.append(ny)
        return dist

    myd = bfs((sx, sy))
    opd = bfs((ox, oy))

    best_move = (0, 0)
    best_val = -10**18
    has_any = False

    for dx, dy in dirs8:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            nx, ny = sx, sy
        my_dn = myd[ny][nx]
        if my_dn >= INF:
            continue
        val = -my_dn  # prefer being closer
        # choose target resource that we can potentially contest
        for rx, ry in resources:
            md = myd[ry][rx]
            if md >= INF:
                continue
            od = opd[ry][rx]
            if od >= INF:
                # free resource; strongly prefer
                gain = 120 - my_dn
            else:
                gain = (od - my_dn) * 120 - my_dn - (md * 0)
            val = max(val, gain)
            has_any = True

        # secondary: if opponent is nearby, don't step into becoming much closer to them
        opp_step = max(abs(nx - ox), abs(ny - oy))
        val += -2.0 * opp_step
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    if not has_any:
        # fallback: move to reduce distance to nearest resource if any are reachable
        for dx, dy in dirs8:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            if myd[ny][nx] < myd[sy][sx]:
                return [dx, dy]
        return [0, 0]

    return [best_move[0], best_move[1]]