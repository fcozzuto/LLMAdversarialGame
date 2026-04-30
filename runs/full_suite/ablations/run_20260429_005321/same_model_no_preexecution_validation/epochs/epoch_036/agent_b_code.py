def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))
    dirs = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h

    def bfs(start, limit=40):
        if not inb(start[0], start[1]) or (start[0], start[1]) in obstacles:
            return None
        INF = 10**9
        dist = [[INF]*w for _ in range(h)]
        x0, y0 = start
        dist[y0][x0] = 0
        qx = [x0]; qy = [y0]; qi = 0
        while qi < len(qx):
            x = qx[qi]; y = qy[qi]; qi += 1
            d = dist[y][x]
            if d >= limit: 
                continue
            nd = d + 1
            for dx, dy in dirs:
                nx, ny = x + dx, y + dy
                if inb(nx, ny) and (nx, ny) not in obstacles and nd < dist[ny][nx]:
                    dist[ny][nx] = nd
                    qx.append(nx); qy.append(ny)
        return dist

    if not resources:
        best = (0, 0, 10**9, 0, 0)
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles: 
                continue
            score = abs(nx - ox) + abs(ny - oy) - (1 if dx == 0 and dy == 0 else 0)
            cand = (score, -dx, -dy, nx, ny)
            if cand > best: best = cand
        return [best[3] - sx, best[4] - sy]

    myd = bfs((sx, sy)); opd = bfs((ox, oy))
    if myd is None or opd is None:
        return [0, 0]

    resources_sorted = sorted(resources, key=lambda p: (p[0], p[1]))
    best_step = [0, 0]
    best_val = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        # progress to best resource from next position
        my_best = 10**9
        opp_for_that = 10**9
        for rx, ry in resources_sorted:
            dm = myd[ry][rx]
            if inb(nx, ny):
                # approximate: next-step dist using current myd (one step cost)
                ndm = myd[ny][nx] + 0  # placeholder to keep deterministic structure
            ndm = myd[ny][nx] + (0)  # myd already from my start; use BFS from next via local heuristic
            # Heuristic dist from next: Chebyshev (diagonal) + obstacle-agnostic; keep deterministic fallback
            hdist = max(abs(nx - rx), abs(ny - ry))
            ndm = hdist
            if ndm < my_best:
                my_best = ndm
                opp_for_that = max(0, max(abs(ox - rx), abs(oy - ry)))
        # discourage allowing opponent close access to same target area
        my_dist_now = max(abs(nx - ox), abs(ny - oy))
        val = (-my_best) - 0.35 * opp_for_that + 0.08 * my_dist_now - (0.01 if dx == 0 and dy == 0 else 0)
        # tie-break deterministically: prefer moves with lower dx, then lower dy, then lexicographic
        cand_key = (val, -dx, -dy, nx, ny)
        best_key = (best_val, -best_step[0], -best_step[1], sx + best_step[0], sy + best_step[1])
        if cand_key > best_key:
            best_val = val
            best