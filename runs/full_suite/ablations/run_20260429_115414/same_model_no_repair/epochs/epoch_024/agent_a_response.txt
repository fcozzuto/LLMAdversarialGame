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

    best_r = None
    best_margin = -10**18
    for rx, ry in resources:
        d1 = myd[ry][rx]
        if d1 >= INF:
            continue
        d2 = opd[ry][rx]
        if d2 >= INF:
            margin = 10**12 - d1
        else:
            margin = (d2 - d1)  # positive if I'm closer
        # tie-break: prefer closer overall, then deterministic by coordinates
        if margin > best_margin or (margin == best_margin and (d1, rx, ry) < (myd[best_r[1]][best_r[0]], best_r[0], best_r[1])):
            best_margin = margin
            best_r = (rx, ry)

    tx, ty = best_r
    cur_my = myd[sy][sx]
    cur_op = opd[ty][tx]

    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue
        d_my_to_t = myd[ny][tx]
        if d_my_to_t >= INF:
            continue
        d_op_to_t = opd[ty][tx]
        # Prefer getting closer to target, and being closer than opponent.
        val = (d_op_to_t - d_my_to_t)
        # If I'm not winning on margin, still push toward target; small anti-oscillation bias
        val = val * 100 - d_my_to_t
        # Deterministic tie-break
        if val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]