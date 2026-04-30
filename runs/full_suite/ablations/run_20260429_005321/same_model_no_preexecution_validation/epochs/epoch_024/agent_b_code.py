def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = {(p[0], p[1]) for p in (observation.get("obstacles") or [])}
    dirs = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    INF = 10**9

    def inb(x, y): return 0 <= x < w and 0 <= y < h

    def bfs(start):
        x0, y0 = start
        dist = [[INF] * w for _ in range(h)]
        if not inb(x0, y0) or (x0, y0) in obstacles:
            return dist
        dist[y0][x0] = 0
        qx = [x0]; qy = [y0]; qi = 0
        while qi < len(qx):
            x, y = qx[qi], qy[qi]; qi += 1
            nd = dist[y][x] + 1
            for dx, dy in dirs:
                nx, ny = x + dx, y + dy
                if inb(nx, ny) and (nx, ny) not in obstacles and nd < dist[ny][nx]:
                    dist[ny][nx] = nd
                    qx.append(nx); qy.append(ny)
        return dist

    myd = bfs((sx, sy))
    opd = bfs((ox, oy))

    if not resources:
        tx, ty = w // 2, h // 2
    else:
        best = None
        for rx, ry in resources:
            dm, do = myd[ry][rx], opd[ry][rx]
            if dm >= INF and do >= INF:
                continue
            # Prefer reachable resources where we are closer than opponent.
            # Tie-break deterministically by coordinates.
            key = (-(do - dm), -(dm), -(rx + ry), rx, ry)
            if best is None or key > best[0]:
                best = (key, (rx, ry))
        tx, ty = best[1] if best is not None else (w // 2, h // 2)

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2; dy = y1 - y2
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    # Candidate move: must be valid (bounds and not into obstacle).
    candidates = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            dm_next = myd[ny][nx]
            # Estimated race value for reaching target from next cell
            # (use precomputed distances, fallback to geometric if unreachable).
            dm_t = myd[ty][tx]
            do_t = opd[ty][tx]
            if resources:
                # Relative advantage at target
                race = (do_t - dm_t)
            else:
                race = 0
            reach = dm_next if dm_next < INF else cheb(nx, ny, tx, ty)
            # Score: maximize advantage, minimize distance to target; keep deterministic order.
            score = (race, -reach, -(cheb(nx, ny, tx, ty)), -nx, -ny, dx, dy)
            candidates.append((score, dx, dy))
    if not candidates:
        return [0, 0]

    candidates.sort(reverse=True)
    _, dx, dy = candidates[0]
    return [dx, dy]