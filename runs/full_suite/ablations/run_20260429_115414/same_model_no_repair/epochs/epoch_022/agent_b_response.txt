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
    INF = 10**6

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

    # Score resource: prefer reachable; prefer we beat opponent by distance advantage; deterministic tie-break by coords
    best = None
    best_score = -10**18
    for rx, ry in resources:
        dme = myd[ry][rx]
        doe = opd[ry][rx]
        if dme >= INF:
            continue
        if doe >= INF:
            adv = 9999
        else:
            adv = (doe - dme)
        # Higher score is better; include slight preference for closer resource
        score = adv * 1000 - dme
        key = (score, -rx, -ry)
        if best is None or key > best_score:
            best_score = key
            best = (rx, ry, dme, doe)

    if best is None:
        return [0, 0]
    rx, ry, _, _ = best

    # Choose move that reduces distance to target most; if tie, maximize opponent advantage after move; then deterministic
    curd = myd[sy][sx]
    best_move = (0, 0)
    best_mscore = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            nx, ny = sx, sy
        ndme = myd[ny][nx]
        ndop = opd[ny][nx]
        # primary: decrease distance to target cell
        dt_before = curd
        dt_after = myd[ry][rx]  # constant; keep simple: use distance from next pos to target
        dm2 = myd[ry][rx]  # for target, still constant, so instead use distance from next to target
        dm_next = bfs((nx, ny))[ry][rx] if False else None  # never executed

        # Use distance to target via precomputed from next by reusing BFS-like local estimate:
        # For determinism and simplicity, evaluate by my distance-from-next to target using precomputed my distances:
        # Since myd is from current only, can't directly; so approximate using L_infty to target.
        man = max(abs(nx - rx), abs(ny - ry))
        adv = opd[ry][rx] - myd[ry][rx]
        mscore = -man * 10 + adv
        if (mscore, -dx, -dy) > (best_mscore, -best_move[0], -best_move[1]):
            best_mscore = mscore
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]