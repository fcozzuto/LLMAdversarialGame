def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", []) or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles", []) or []))
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    INF = 10**9

    def bfs(start):
        x0, y0 = start
        dist = [[INF] * w for _ in range(h)]
        if not (0 <= x0 < w and 0 <= y0 < h) or (x0, y0) in obstacles:
            return dist
        dist[y0][x0] = 0
        qx, qy = [x0], [y0]
        qi = 0
        while qi < len(qx):
            x, y = qx[qi], qy[qi]
            qi += 1
            nd = dist[y][x] + 1
            for dx, dy in moves:
                nx, ny = x + dx, y + dy
                if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles and nd < dist[ny][nx]:
                    dist[ny][nx] = nd
                    qx.append(nx)
                    qy.append(ny)
        return dist

    myd = bfs((sx, sy))
    opd = bfs((ox, oy))

    best_target = None
    best_key = None
    for rx, ry in resources:
        if not (0 <= rx < w and 0 <= ry < h) or (rx, ry) in obstacles:
            continue
        d1, d2 = myd[ry][rx], opd[ry][rx]
        if d1 >= INF and d2 >= INF:
            continue
        # Prefer reachable & where I'm not too far behind; tie-break lexicographically
        if d1 < INF and d2 < INF:
            key = (min(d1, d2), (d1 - d2), rx, ry)
        elif d1 < INF:
            key = (0, d1, rx, ry)
        else:
            key = (1, d2 + 1000, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best_target = (rx, ry)

    if best_target is None:
        # No valid targets: move to reduce distance to opponent's location or stay safe
        tx, ty = ox, oy
    else:
        tx, ty = best_target

    # Choose move that minimizes distance to target; if contesting, also slightly increases distance from opponent
    def cheb(x, y, a, b):
        dx = x - a
        if dx < 0: dx = -dx
        dy = y - b
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    best_move = (0, 0)
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            dist_to = myd[ny][nx]
            # Heuristic: progress to target by chebyshev; penalize getting closer to opponent when I'm behind
            score = cheb(nx, ny, tx, ty)
            opp_dist = cheb(nx, ny, ox, oy)
            my_to_t = myd[ty][tx]
            op_to_t = opd[ty][tx]
            behind = 1 if (my_to_t < INF and op_to_t < INF and my_to_t - op_to_t > 0) else 0
            score = (score, -opp_dist if behind else opp_dist, dist_to, nx, ny)
            if best_val is None or score < best_val:
                best_val = score
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]