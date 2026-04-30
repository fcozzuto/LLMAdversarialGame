def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = int(observation["self_position"][0]), int(observation["self_position"][1])
    ox, oy = int(observation["opponent_position"][0]), int(observation["opponent_position"][1])
    obstacles = {(int(p[0]), int(p[1])) for p in (observation.get("obstacles") or [])}
    resources = [(int(p[0]), int(p[1])) for p in (observation.get("resources") or [])]
    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def free(x, y):
        return inb(x, y) and (x, y) not in obstacles

    INF = 10**9

    def bfs(start):
        x0, y0 = int(start[0]), int(start[1])
        dist = [[INF] * h for _ in range(w)]
        if not free(x0, y0):
            return dist
        dist[x0][y0] = 0
        qx, qy = [x0], [y0]
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

    myd = bfs((sx, sy))
    opd = bfs((ox, oy))

    best = None
    best_key = None
    for rx, ry in resources:
        if not free(rx, ry):
            continue
        d1 = myd[rx][ry]
        d2 = opd[rx][ry]
        if d1 >= INF:
            continue
        # Prefer resources where we can arrive earlier; otherwise closest.
        # Key: (ahead?, my_time, opp_time, tie by x,y)
        ahead = 1 if d1 < d2 else 0
        key = (ahead, d1, d2, rx, ry)
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)

    if best is None:
        # If no reachable resources, move to maximize freedom: reduce distance to opponent (deterministic fallback).
        tx, ty = ox, oy
    else:
        tx, ty = best[0], best[1]

    # Choose move that minimizes distance to target (then tie-break deterministically).
    best_move = (0, 0)
    best_dist = myd[tx][ty] if (0 <= tx < w and 0 <= ty < h) else INF
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        d = myd[nx][ny]
        # Prefer smaller distance to the target; approximate by myd from current -> target using precomputed myd is not available.
        # Use direct neighbor evaluation by recomputing to target via heuristic: Manhattan with diagonal allowance.
        # But to stay deterministic and effective, use Euclidean-squared to target with BFS tie through myd to avoid walls.
        if myd[tx][ty] < INF:
            # Use BFS distance-to-target as heuristic by shifting via local distances:
            # If target reachable, compare by BFS distance from neighbor to target computed indirectly:
            # We don't have reverse distances; use Euclidean to guide.
            pass
        hdist = (nx - tx) * (nx - tx) + (ny - ty) * (ny - ty)
        # Primary: closer to target by Euclidean; Secondary: lexicographic move; Tertiary: prefer not to stay still unless forced.
        if hdist < best_dist or (best_dist != hdist and hdist == best_dist and (dx, dy) < best_move):
            best_dist = hdist
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]