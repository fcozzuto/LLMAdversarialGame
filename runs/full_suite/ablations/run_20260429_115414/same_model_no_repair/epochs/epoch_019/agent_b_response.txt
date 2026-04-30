def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if not resources:
        return [0, 0]
    if (sx, sy) in obstacles:
        return [0, 0]

    INF = 10**9

    def bfs_dist(start):
        dist = [[INF] * w for _ in range(h)]
        x0, y0 = start
        if not (0 <= x0 < w and 0 <= y0 < h) or (x0, y0) in obstacles:
            return dist
        qx, qy = [x0], [y0]
        qi = 0
        dist[y0][x0] = 0
        while qi < len(qx):
            x, y = qx[qi], qy[qi]
            qi += 1
            nd = dist[y][x] + 1
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    if dx == 0 and dy == 0:
                        continue
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles and nd < dist[ny][nx]:
                        dist[ny][nx] = nd
                        qx.append(nx)
                        qy.append(ny)
        return dist

    myd = bfs_dist((sx, sy))
    opd = bfs_dist((ox, oy))

    # If standing on a resource, try to move to deny opponent the best alternative.
    best_res = None
    best_val = -INF
    for rx, ry in resources:
        d1, d2 = myd[ry][rx], opd[ry][rx]
        if d1 >= INF and d2 >= INF:
            continue
        # Value: prioritize resources we can reach and where we are significantly closer than opponent.
        val = (d2 - d1) * 1000 - d1
        if val > best_val:
            best_val = val
            best_res = (rx, ry)

    if best_res is None:
        return [0, 0]
    tx, ty = best_res

    def move_key(dx, dy):
        nx, ny = sx + dx, sy + dy
        if nx < 0 or ny < 0 or nx >= w or ny >= h or (nx, ny) in obstacles:
            return -INF
        # Re-evaluate advantage using precomputed distances (BFS is from current positions; approximation is fine).
        d_my = myd[ny][nx]
        # Aim: reduce distance to target; also keep opponent from gaining on same target.
        cur_my_to_t = bfs_dist((nx, ny))[ty][tx] if (nx, ny) != (sx, sy) else myd[ty][tx]
        cur_op_to_t = opd[ty][tx]
        if cur_my_to_t >= INF:
            return -INF
        return (cur_op_to_t - cur_my_to_t) * 2000 - cur_my_to_t - (d_my if d_my < INF else 0)

    best_move = (0, 0)
    best_move_val = -INF
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or ny < 0 or nx >= w or ny >= h or (nx, ny) in obstacles:
            continue
        # Primary: how much closer we become to the chosen target vs opponent.
        # Tie-breaker: prefer smaller myd to the target.
        cur_my_to_t = myd[ny][nx]  # not directly to target; used only as deterministic tiebreak noise
        # Better: exact distance from candidate to target via BFS (still cheap on 8x8).
        cand_d = bfs_dist((nx, ny))[ty][tx]
        op_d = opd[ty][tx]
        if cand_d >= INF:
            continue
        val = (op_d - cand_d) * 2000 - cand_d - cur_my_to_t
        if val > best_move_val:
            best_move_val = val
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]