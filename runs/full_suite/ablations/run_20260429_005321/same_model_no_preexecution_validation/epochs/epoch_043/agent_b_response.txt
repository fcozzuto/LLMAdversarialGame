def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))
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

    myd0 = bfs((sx, sy))
    opd = bfs((ox, oy))
    if myd0 is None or opd is None or not resources:
        return [0, 0]

    # Pre-filter reachable resources for both.
    reachable = []
    for rx, ry in resources:
        md = myd0[ry][rx] if inb(rx, ry) and (rx, ry) not in obstacles else INF
        od = opd[ry][rx] if inb(rx, ry) and (rx, ry) not in obstacles else INF
        if md < INF:
            reachable.append((rx, ry, md, od))

    if not reachable:
        return [0, 0]

    # Decide by one-step lookahead: pick move maximizing "winning chance"
    # (md - od) plus tie-breaking toward resource closest to us.
    best_move = (0, 0)
    best_val = -10**18
    # Sort deterministic fallback preference
    pref = [(0, 0), (1, 0), (0, 1), (-1, 0), (0, -1), (1, 1), (-1, 1), (1, -1), (-1, -1)]
    for dx, dy in pref:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            nx, ny = sx, sy
        # Compute distances from hypothetical position; grid small so BFS is fine.
        myd = bfs((nx, ny))
        if myd is None:
            continue

        # Evaluate against opponent: try to find a resource we can beat.
        win_exists = False
        best_local = -10**18
        for rx, ry, md0, od in reachable:
            md = myd[ry][rx]
            if md >= INF:
                continue
            # Prefer resources we can arrive earlier (strictly).
            diff = md - od
            # Hard reward for guaranteed earlier arrival; softer otherwise.
            if md < od:
                win_exists = True
                val = 10000 - diff * 10 - md  # smaller diff, smaller md is better
            else:
                # If cannot win any, minimize how close opponent is compared to us.
                # Also bias toward decreasing our md (progress).
                val = - (diff * 5) - md
            if val > best_local:
                best_local = val

        # If no winning target: focus on reducing (od - md) for the closest resource to us.
        # This changes behavior materially vs greedy-at-start targeting.
        if not win_exists:
            best_local -= 2000  #