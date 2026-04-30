def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = int(observation["self_position"][0]), int(observation["self_position"][1])
    ox, oy = int(observation["opponent_position"][0]), int(observation["opponent_position"][1])

    obstacles = {(int(p[0]), int(p[1])) for p in (observation.get("obstacles") or [])}
    resources = [(int(p[0]), int(p[1])) for p in (observation.get("resources") or [])]

    dirs = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    INF = 10**9

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def free(x, y):
        return inb(x, y) and (x, y) not in obstacles

    def bfs(x0, y0):
        dist = [[INF] * h for _ in range(w)]
        if not free(x0, y0):
            return dist
        dist[x0][y0] = 0
        qx = [x0]
        qy = [y0]
        qi = 0
        while qi < len(qx):
            x, y = qx[qi], qy[qi]
            qi += 1
            nd = dist[x][y] + 1
            for dx, dy in dirs:
                nx, ny = x + dx, y + dy
                if free(nx, ny) and nd < dist[nx][ny]:
                    dist[nx][ny] = nd
                    qx.append(nx)
                    qy.append(ny)
        return dist

    myd = bfs(sx, sy)
    opd = bfs(ox, oy)

    # Choose best target resource deterministically via contest-aware score.
    best_res = None
    best_val = -10**18
    alpha = 1.15  # prefer resources we can reach sooner than opponent
    beta = 0.05   # small bias to nearer resources
    for rx, ry in resources:
        d1, d2 = myd[rx][ry], opd[rx][ry]
        if d1 >= INF:
            continue
        if d2 >= INF:
            val = 10_000 - beta * d1
        else:
            # Higher is better: we want (d2 - d1) positive and large; also prefer shorter d1.
            val = (d2 - d1) * alpha - beta * d1
        if val > best_val:
            best_val = val
            best_res = (rx, ry)

    # If no reachable resources, just move toward opponent to disrupt.
    tx, ty = best_res if best_res is not None else (ox, oy)

    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        # Score this move by its progress to target and advantage in contest (if reachable).
        d1 = myd[nx][ny]
        # Use precomputed distances from the move position to the chosen target by approximating via BFS from target?
        # Instead compute by direct Chebyshev distance as a proxy; BFS is expensive repeatedly, but we stay concise.
        # Chebyshev is exact for empty grid with diagonal moves.
        proxy_to_target = max(abs(nx - tx), abs(ny - ty))
        # Also estimate opponent proximity to target: use precomputed opd at target only.
        t_opd = opd[tx][ty] if best_res is not None else opd[nx][ny]
        # We want to reduce proxy_to_target; and if contesting, prefer being closer than opponent's BFS distance-to-target.
        if best_res is not None and t_opd < INF:
            score = (t_opd - myd[tx][ty]) * alpha - proxy_to_target - beta * d1
        else:
            score = -proxy_to_target - 0.01 * d1
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]