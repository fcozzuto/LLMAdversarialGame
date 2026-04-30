def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = int(observation["self_position"][0]), int(observation["self_position"][1])
    ox, oy = int(observation["opponent_position"][0]), int(observation["opponent_position"][1])

    obstacles = {(int(p[0]), int(p[1])) for p in (observation.get("obstacles") or [])}
    resources = [(int(p[0]), int(p[1])) for p in (observation.get("resources") or [])]

    dirs = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def free(x, y): return inb(x, y) and (x, y) not in obstacles

    INF = 10**9

    def bfs(start):
        x0, y0 = start
        dist = [[INF] * h for _ in range(w)]
        if not free(x0, y0):
            return dist
        dist[x0][y0] = 0
        q = [(x0, y0)]
        qi = 0
        while qi < len(q):
            x, y = q[qi]; qi += 1
            nd = dist[x][y] + 1
            for dx, dy in dirs:
                nx, ny = x + dx, y + dy
                if free(nx, ny) and nd < dist[nx][ny]:
                    dist[nx][ny] = nd
                    q.append((nx, ny))
        return dist

    myd = bfs((sx, sy))
    opd = bfs((ox, oy))

    best = None
    best_val = -10**18
    for rx, ry in resources:
        d1, d2 = myd[rx][ry], opd[rx][ry]
        if d1 >= INF:
            continue
        # Prefer resources where we beat opponent, but also reduce risk of getting stuck behind.
        val = (d2 - d1) * 1000
        val += -d1  # closer is better once compared
        if val > best_val:
            best_val = val
            best = (rx, ry)
        elif val == best_val and best is not None:
            # deterministic tie-break: lexicographic
            if (rx, ry) < best:
                best = (rx, ry)

    if best is None:
        # No reachable resources: head deterministically toward center.
        tx, ty = (w - 1) // 2, (h - 1) // 2
    else:
        tx, ty = best

    # Move: choose among valid deltas that minimize my distance to target; if tie, maximize opponent slack.
    curd = myd
    best_move = (0, 0)
    best_md = INF
    best_adv = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        md = curd[nx][ny]
        adv = opd[nx][ny] - curd[nx][ny]
        # primary: smaller distance to target (proxy via BFS from current: compare myd at target is constant;
        # instead use greedy heuristic to decrease Euclidean to target, then BFS distance)
        # We'll use heuristic distance to target as primary to avoid extra searches.
        hdist = (nx - tx) * (nx - tx) + (ny - ty) * (ny - ty)
        score = (0, 0, 0)  # placeholder tuple
        # We'll implement explicit comparisons for determinism.
        if hdist < ( (sx+best_move[0]-tx)**2 + (sy+best_move[1]-ty)**2 ):
            pass
        # Use combined: (hdist, md, -adv)
        cand = (hdist, md, -adv)
        if cand < ( ( (sx+best_move[0]-tx)**2 + (sy+best_move[1]-ty)**2 ), best_md, -best_adv ):
            best_move = (dx, dy)
            best_md = md
            best_adv = adv
    return [int(best_move[0]), int(best_move[1])]