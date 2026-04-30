def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def bfs(start):
        x0, y0 = start
        if not inb(x0, y0) or (x0, y0) in obstacles:
            return None
        INF = 10**9
        dist = [[INF] * w for _ in range(h)]
        dist[y0][x0] = 0
        qx = [x0]
        qy = [y0]
        qi = 0
        while qi < len(qx):
            x = qx[qi]
            y = qy[qi]
            qi += 1
            nd = dist[y][x] + 1
            for dx, dy in dirs:
                nx, ny = x + dx, y + dy
                if inb(nx, ny) and (nx, ny) not in obstacles and nd < dist[ny][nx]:
                    dist[ny][nx] = nd
                    qx.append(nx)
                    qy.append(ny)
        return dist

    if not resources:
        return [0, 0]

    myd = bfs((sx, sy))
    opd = bfs((ox, oy))
    if myd is None or opd is None:
        return [0, 0]

    # If we're already on a resource, stay to collect.
    for rx, ry in resources:
        if rx == sx and ry == sy and (sx, sy) not in obstacles:
            return [0, 0]

    INF = 10**9
    best = None
    best_score = -10**18
    for rx, ry in resources:
        if not inb(rx, ry) or (rx, ry) in obstacles:
            continue
        md = myd[ry][rx]
        od = opd[ry][rx]
        if md >= INF or od >= INF:
            continue
        # Prefer resources we can reach sooner than opponent; break ties deterministically.
        score = (od - md) * 10 - md
        if score > best_score or (score == best_score and (rx, ry) < best):
            best_score = score
            best = (rx, ry)

    if best is None:
        return [0, 0]

    tx, ty = best
    # Pick move that minimizes our distance to target; deterministic tie-breaking.
    cur_best = (INF, 0, 0)  # (dist, rx, ry) style deterministic
    chosen = (0, 0)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        d_to_target = myd[ny][nx]  # already computed; but myd is from start so need dist from new pos.
        # Use our precomputed dist-to-each-cell from start: compare via dist difference.
        # Approximation: minimize myd[ty][tx] - myd[ty][nx] would require all-pairs; instead use greedy by
        # directly minimizing Euclidean to target and then myd[ny][nx] monotonicity is unreliable.
        # We'll instead do a local Manhattan/chebyshev greedy with obstacle check; deterministic.
        cheb = max(abs(tx - nx), abs(ty - ny))
        # Ensure staying still is allowed and considered via dx=0,dy=0.
        key = (cheb, d_to_target, dx, dy)
        if key < cur_best:
            cur_best = key
            chosen = (dx, dy)

    return [int(chosen[0]), int(chosen[1])]