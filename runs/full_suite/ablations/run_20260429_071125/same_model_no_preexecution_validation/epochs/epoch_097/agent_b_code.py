def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = map(int, observation.get("self_position", [0, 0]))
    ox, oy = map(int, observation.get("opponent_position", [0, 0]))
    obstacles = set()
    for p in (observation.get("obstacles") or []):
        x, y = int(p[0]), int(p[1])
        obstacles.add((x, y))
    resources = []
    for p in (observation.get("resources") or []):
        resources.append((int(p[0]), int(p[1])))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    INF = 10**9

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def valid(x, y): return inb(x, y) and (x, y) not in obstacles

    def bfs(x0, y0):
        dist = [[INF] * h for _ in range(w)]
        if not valid(x0, y0):
            return dist
        dist[x0][y0] = 0
        qx, qy = [x0], [y0]
        qi = 0
        while qi < len(qx):
            x, y = qx[qi], qy[qi]
            qi += 1
            nd = dist[x][y] + 1
            for dx, dy in moves:
                nx, ny = x + dx, y + dy
                if valid(nx, ny) and nd < dist[nx][ny]:
                    dist[nx][ny] = nd
                    qx.append(nx); qy.append(ny)
        return dist

    dS = bfs(sx, sy)
    dO = bfs(ox, oy)

    def best_target():
        best = None
        best_key = None
        for rx, ry in resources:
            ds = dS[rx][ry]
            if ds >= INF:
                continue
            do = dO[rx][ry]
            if do >= INF:
                do = INF
            # Prefer resources we reach earlier; if close, prefer those opponent also can't beat.
            adv = do - ds
            # Deterministic tie-breakers: smaller ds, then higher adv, then lexicographic.
            key = (-(adv if do < INF else INF), ds, rx, ry)
            if best_key is None or key < best_key:
                best_key = key
                best = (rx, ry, ds, do)
        return best

    target = best_target()
    if target is None:
        # No reachable resource: drift toward center while avoiding opponent.
        tx, ty = w // 2, h // 2
    else:
        tx, ty = target[0], target[1]

    # Pick move that decreases distance to target; if target none, use center.
    def score_move(nx, ny):
        # If move invalid (shouldn't happen), stay worst.
        if not valid(nx, ny):
            return -10**18
        # Distance heuristic (Chebyshev works well with 8-neigh).
        dist_to_t = max(abs(tx - nx), abs(ty - ny))
        # Also consider blocking/contest: move that improves advantage on target is best.
        s_adv = dO[tx][ty] - dS[nx][ny]
        # If advancing, make it strong; otherwise fall back to simple approach.
        return (s_adv * 1000 - dist_to_t) - (abs(ox - nx) + abs(oy - ny)) * 0.01

    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        val = score_move(nx, ny)
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    dx, dy = best_move
    if dx not in (-1, 0, 1) or dy not in (-1, 0, 1):
        return [0, 0]
    return [int(dx), int(dy)]