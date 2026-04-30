def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = {(p[0], p[1]) for p in (observation.get("obstacles") or [])}
    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    INF = 10**9

    def inb(x, y): return 0 <= x < w and 0 <= y < h

    def bfs(start):
        x0, y0 = start
        if not inb(x0, y0) or (x0, y0) in obstacles:
            return None
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

    myd = bfs((sx, sy))
    opd = bfs((ox, oy))
    if not resources or myd is None or opd is None:
        return [0, 0]

    best_r = None
    best_key = (-INF, -INF, INF)  # (adv, our_closer, our_dist)
    for rx, ry in resources:
        dm, do = myd[ry][rx], opd[ry][rx]
        if dm >= INF and do >= INF:
            continue
        adv = do - dm
        key = (adv, -dm if dm < INF else -INF, dm if dm < INF else INF)
        if key > best_key:
            best_key = key
            best_r = (rx, ry)

    if best_r is None:
        return [0, 0]
    tx, ty = best_r

    cur_my = myd[sy][sx]
    best_move = (0, 0)
    best_move_key = (-INF, -INF, -INF)  # (opponent_dist, our_dist_to_target, -step_dist)

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        my_to = myd[ny][nx]
        # If BFS can't reach, strongly discourage.
        if my_to >= INF:
            continue
        dist_to_target = myd[ty][nx]
        opp_dist = opd[ty][nx] if opd is not None else INF
        # Prefer moves that reduce distance to target, and worsen opponent's access (higher opp_dist).
        step_pen = abs(dx) + abs(dy)
        move_key = (opp_dist, -dist_to_target if dist_to_target < INF else -INF, -step_pen)
        if move_key > best_move_key:
            best_move_key = move_key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]