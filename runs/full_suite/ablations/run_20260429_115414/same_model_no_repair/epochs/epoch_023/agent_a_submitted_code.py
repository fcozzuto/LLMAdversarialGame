def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    if not resources:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    INF = 10**9

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

    myd = bfs((sx, sy))
    opd = bfs((ox, oy))

    def resource_score(dme, doe, rx, ry):
        if dme >= INF and doe >= INF:
            return -10**18
        if dme >= INF:
            return -10**12 + (INF - doe) * -0.001
        if doe >= INF:
            return 10**12 - dme * 0.01
        adv = doe - dme  # positive is good (we arrive earlier)
        base = adv * 100.0
        # prefer closer resources as tie-breaker
        return base - (dme * 1.0) - (rx + ry) * 0.001

    def best_target_from(posx, posy):
        best_s = -10**18
        best_t = None
        for rx, ry in resources:
            dme = myd[ry][rx] if posx == sx and posy == sy else bfs((posx, posy))[ry][rx]
            # Keep deterministic even if unreachable: still score, but strongly penalize.
            s = resource_score(dme, opd[ry][rx], rx, ry)
            if s > best_s or (s == best_s and (rx, ry) < best_t):
                best_s = s
                best_t = (rx, ry)
        return best_t, best_s

    # Evaluate candidate moves by how well they set up the best target (recompute BFS only per move).
    best_move = (0, 0)
    best_val = -10**19
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        myd2 = bfs((nx, ny))
        best_s = -10**18
        best_t = None
        for rx, ry in resources:
            dme = myd2[ry][rx]
            s = resource_score(dme, opd[ry][rx], rx, ry)
            if s > best_s or (s == best_s and (rx, ry) < (best_t if best_t else (10**9, 10**9))):
                best_s = s
                best_t = (rx, ry)

        # Secondary heuristic: if best targets are similarly scored, pick move that improves our distance to opponent's best target.
        if best_t is not None:
            tx, ty = best_t
            tie = -myd2[ty][tx