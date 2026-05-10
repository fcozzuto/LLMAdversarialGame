def choose_move(observation):
    w = int(observation.get("grid_width", 0) or 0)
    h = int(observation.get("grid_height", 0) or 0)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def free(x, y): return inb(x, y) and (x, y) not in obstacles

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    # 1-step BFS (shortest path) towards opponent, depth limited for speed
    max_depth = 8
    start = (sx, sy)
    target = (ox, oy)
    if start == target:
        return [0, 0]

    q = [start]
    qi = 0
    dist = {start: 0}
    prev = {start: None}

    while qi < len(q):
        x, y = q[qi]; qi += 1
        d0 = dist[(x, y)]
        if d0 >= max_depth:
            continue
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if not free(nx, ny):
                continue
            ns = (nx, ny)
            if ns in dist:
                continue
            dist[ns] = d0 + 1
            prev[ns] = (x, y)
            q.append(ns)
    # Choose first step on a shortest reachable path to target (if reachable)
    if target in dist:
        cur = target
        while prev[cur] is not None and prev[cur] != start:
            cur = prev[cur]
        step = [cur[0] - sx, cur[1] - sy]
        if step[0] in (-1, 0, 1) and step[1] in (-1, 0, 1):
            return step
        return [0, 0]

    # Fallback: greedy move that minimizes distance to opponent with obstacle-aware tie-breaks
    # Tie-break priority: (distance, -center_bias, dx, dy) deterministic
    def greedy_key(mv):
        dx, dy = mv
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            return (10**9, 0, 0, 0)
        distv = abs(nx - ox) + abs(ny - oy)
        # center bias slightly to avoid corner trapping
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        center = abs(nx - cx) + abs(ny - cy)
        return (distv, center, dx, dy)

    best_mv = min(moves, key=greedy_key)
    return [best_mv[0], best_mv[1]]