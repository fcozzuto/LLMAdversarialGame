def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))
    dirs = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    def inb(x, y): return 0 <= x < w and 0 <= y < h

    if not resources: return [0, 0]

    def bfs(start):
        x0, y0 = start
        if not inb(x0, y0) or (x0, y0) in obstacles: return None
        INF = 10**9
        dist = [[INF] * w for _ in range(h)]
        dist[y0][x0] = 0
        q = [(x0, y0)]
        qi = 0
        while qi < len(q):
            x, y = q[qi]; qi += 1
            nd = dist[y][x] + 1
            for dx, dy in dirs:
                nx, ny = x + dx, y + dy
                if inb(nx, ny) and (nx, ny) not in obstacles and nd < dist[ny][nx]:
                    dist[ny][nx] = nd
                    q.append((nx, ny))
        return dist

    myd = bfs((sx, sy))
    opd = bfs((ox, oy))
    if myd is None or opd is None: return [0, 0]

    # Immediate pickup if any resource is reachable in 0/1 step.
    adj = set()
    for rx, ry in resources:
        if inb(rx, ry) and (rx, ry) not in obstacles:
            adj.add((rx, ry))
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if (nx, ny) in adj:
            return [dx, dy]

    # Pick resource with best advantage (we prefer states where we arrive earlier).
    INF = 10**9
    best = None
    best_val = -10**18
    for rx, ry in resources:
        if not inb(rx, ry) or (rx, ry) in obstacles: 
            continue
        md = myd[ry][rx]; od = opd[ry][rx]
        if md >= INF or od >= INF: 
            continue
        # Value: win-the-race first, then prefer closer, then slight preference to reduce opponent access.
        val = (od - md) * 10 - md
        if val > best_val:
            best_val = val
            best = (rx, ry)

    if best is None: return [0, 0]
    tx, ty = best

    # Move one step toward target, tie-breaker by maximizing opponent delay.
    best_move = [0, 0]
    best_key = (-10**18, -10**18)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        my_to = myd[ny][nx]  # not useful; keep simple greedy via myd from current:
        # Use BFS distance from (nx,ny) by approximating with myd at target? Greedy uses shortest-step:
        # Choose move minimizing myd[ty][tx]?? Instead compute from existing myd: dist from (nx,ny) to (tx,ty) not available.
        # We'll approximate by minimizing Chebyshev distance to target (still deterministic and effective).
        cheb = max(abs(tx - nx), abs(ty - ny))
        # Prefer moves that also worsen opponent's proximity to target.
        cheb_op = max(abs(tx - (ox + dx)), abs(ty - (oy + dy)))
        key = (-cheb, -(cheb_op))
        if key > best_key:
            best_key = key
            best_move = [dx, dy]
    return best_move