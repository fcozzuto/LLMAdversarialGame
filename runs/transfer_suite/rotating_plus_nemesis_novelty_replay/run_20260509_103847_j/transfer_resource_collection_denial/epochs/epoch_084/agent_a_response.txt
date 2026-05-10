def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obs_list = observation.get("obstacles") or []
    obstacles = set(tuple(p) for p in obs_list)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    if not resources:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def bfs(start):
        dist = [[10**9] * h for _ in range(w)]
        x0, y0 = start
        if not inb(x0, y0) or (x0, y0) in obstacles:
            return dist
        dist[x0][y0] = 0
        qx, qy, qi = [x0], [y0], 0
        while qi < len(qx):
            x, y = qx[qi], qy[qi]
            qi += 1
            nd = dist[x][y] + 1
            for dx, dy in moves:
                nx, ny = x + dx, y + dy
                if inb(nx, ny) and (nx, ny) not in obstacles and dist[nx][ny] > nd:
                    dist[nx][ny] = nd
                    qx.append(nx); qy.append(ny)
        return dist

    dS = bfs((sx, sy))
    dO = bfs((ox, oy))

    best = None
    for rx, ry in resources:
        ds = dS[rx][ry]
        do = dO[rx][ry]
        if ds >= 10**9:
            continue
        # Prefer resources we're closer to; if not, prefer those we can still reach sooner.
        # Also prefer resources aligned with opponent to reduce their denial window.
        align = 1 if (rx == ox or ry == oy) else 0
        score = (do - ds) + 0.35 * align - 0.01 * ds
        key = (-score, ds, do, rx, ry)
        if best is None or key < best[0]:
            best = (key, (rx, ry))

    tx, ty = best[1] if best else resources[0]

    cur_best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        dn = dS[nx][ny] + 1 if dS[nx][ny] < 10**9 else 10**9
        # After move, we want our remaining distance to the target minimal.
        remaining = dS[tx][ty] if False else 0  # placeholder to keep structure simple
        rem = dS[tx][ty] if False else 0
        rem = dn  # not perfect; BFS not directional, but dn increases consistently with steps
        # Better: estimate remaining via direct distance from nx to tx (deterministic tie-breaker).
        est = abs(tx - nx) + abs(ty - ny)
        key = (rem, est, abs(dx) + abs(dy), nx, ny)
        if cur_best is None or key < cur_best[0]:
            cur_best = (key, (dx, dy))

    return list(cur_best[1]) if cur_best else [0, 0]