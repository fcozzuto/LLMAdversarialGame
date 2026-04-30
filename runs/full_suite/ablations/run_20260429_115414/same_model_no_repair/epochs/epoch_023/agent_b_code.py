def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    INF = 10**6

    def bfs(start):
        x0, y0 = start
        dist = [[INF] * w for _ in range(h)]
        if not (0 <= x0 < w and 0 <= y0 < h) or (x0, y0) in obstacles:
            return dist
        dist[y0][x0] = 0
        q = [(x0, y0)]
        qi = 0
        while qi < len(q):
            x, y = q[qi]
            qi += 1
            nd = dist[y][x] + 1
            for dx, dy in moves:
                nx, ny = x + dx, y + dy
                if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles and nd < dist[ny][nx]:
                    dist[ny][nx] = nd
                    q.append((nx, ny))
        return dist

    if not resources:
        return [0, 0]

    myd = bfs((sx, sy))
    opd = bfs((ox, oy))

    best_val = -10**18
    best_target = None
    for rx, ry in resources:
        d1 = myd[ry][rx]
        d2 = opd[ry][rx]
        if d1 >= INF:
            continue
        # Prefer resources we can reach; especially where we are closer than opponent.
        val = (d2 - d1) * 100 - d1
        # Deterministic tie-break: prefer lower x, then lower y.
        val -= rx * 0.001 + ry * 0.000001
        if val > best_val:
            best_val = val
            best_target = (rx, ry)

    if best_target is None:
        return [0, 0]
    tx, ty = best_target

    cur_best = myd[sy][sx]
    chosen = (0, 0)
    chosen_dist = cur_best
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue
        d = myd[ny][nx]
        # Move toward target: minimize distance from next position (lower d better).
        # If tied, prefer smaller move lexicographically for determinism.
        if d < chosen_dist or (d == chosen_dist and (dx, dy) < chosen):
            chosen_dist = d
            chosen = (dx, dy)

    # If still stuck, stay still.
    if chosen == (0, 0) and chosen_dist >= INF:
        return [0, 0]
    return [chosen[0], chosen[1]]