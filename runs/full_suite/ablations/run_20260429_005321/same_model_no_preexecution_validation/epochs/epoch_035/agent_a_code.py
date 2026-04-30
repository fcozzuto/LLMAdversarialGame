def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))
    dirs = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h

    INF = 10**9
    def bfs(start):
        x0, y0 = start
        if not inb(x0, y0) or (x0, y0) in obstacles:
            return None
        dist = [[INF]*w for _ in range(h)]
        dist[y0][x0] = 0
        q = [(x0, y0)]
        qi = 0
        while qi < len(q):
            x, y = q[qi]; qi += 1
            d = dist[y][x]
            nd = d + 1
            if nd >= 80: 
                continue
            for dx, dy in dirs:
                nx, ny = x + dx, y + dy
                if inb(nx, ny) and (nx, ny) not in obstacles and nd < dist[ny][nx]:
                    dist[ny][nx] = nd
                    q.append((nx, ny))
        return dist

    if not resources:
        return [0, 0]

    myd = bfs((sx, sy)); opd = bfs((ox, oy))
    if myd is None or opd is None:
        return [0, 0]

    # Deterministic tie-break: sort resources and evaluate moves with lexicographic preference
    resources_sorted = sorted(resources, key=lambda p: (p[0], p[1]))
    best_move = (0, 0); best_val = -INF; best_tie = (INF, INF)

    # Precompute opponent distances once for speed
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            nx, ny = sx, sy
        my_next = myd[ny][nx]
        op_next = opd[ny][nx]

        # Evaluate by looking for best resource advantage from the neighbor cell
        val = -INF
        min_my = INF
        min_adv = -INF
        for rx, ry in resources_sorted:
            dmy = myd[ry][rx]
            dop = opd[ry][rx]
            # advantage at current plan
            if dmy >= INF or dop >= INF:
                continue
            adv = dop - dmy
            # Ensure resource is not only close for us but also reachable from neighbor
            if my_next > dmy + 2:
                continue
            # prefer taking resources where we are earlier than opponent, then closer ones
            score = 1000* (1 if adv > 0 else 0) + 20*adv - dmy
            # small penalty if moving into a place the opponent can reach too quickly
            score -= 2 * op_next
            if score > val or (score == val and (dmy, dop, rx, ry) < (min_my, min_adv, best_tie[0], best_tie[1])):
                val = score
                min_my = dmy
                min_adv = adv

        # Fallback: move toward nearest resource if no advantageous target found
        if val == -INF:
            near = None; bestd = INF
            for rx, ry in resources_sorted:
                dmy = myd[ry][rx]
                if dmy < bestd:
                    bestd = dmy; near = (rx, ry)
            val = -bestd
            min_my = bestd
            min_adv = opd[near[1]][near[0]] - bestd if near else -INF

        # Tie-breakers: prefer greater advantage, then lower my distance, then lexicographically smaller dx,dy
        adv_pref = min_adv
        tie = (-adv_pref, min_my, dx, dy)
        if val > best_val or (val == best_val and tie < best_tie):
            best_val = val
            best_tie = tie
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]