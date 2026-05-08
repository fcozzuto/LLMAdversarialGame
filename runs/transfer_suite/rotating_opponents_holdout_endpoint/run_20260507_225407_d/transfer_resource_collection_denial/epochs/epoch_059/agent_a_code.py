def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obs.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def valid(x, y):
        return inb(x, y) and (x, y) not in obs

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def bfs_dist(start, goal, maxd=6):
        if start == goal:
            return 0
        if not valid(start[0], start[1]) or not valid(goal[0], goal[1]):
            return 10**9
        q = [(start[0], start[1], 0)]
        seen = {(start[0], start[1])}
        while q:
            x, y, d = q.pop(0)
            if d >= maxd:
                continue
            nd = d + 1
            for dx, dy in dirs:
                nx, ny = x + dx, y + dy
                if (nx, ny) in seen or not valid(nx, ny):
                    continue
                if (nx, ny) == goal:
                    return nd
                seen.add((nx, ny))
                q.append((nx, ny, nd))
        return 10**9

    if not resources:
        return [0, 0]

    # Counter-strategy: prioritize fastest self-collection, with mild pressure on opponent.
    # Score lower is better.
    best_res = None
    best_key = None
    for rx, ry in resources:
        self_manh = abs(rx - sx) + abs(ry - sy)
        opp_manh = abs(rx - ox) + abs(ry - oy)
        # Prefer closer resources; if similarly close, prefer one that delays opponent slightly.
        key = (self_manh, (self_manh - 0.25 * opp_manh), rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best_res = (rx, ry)

    tx, ty = best_res

    # Choose move that minimizes BFS distance-to-target (lookahead via obstacles).
    best_move = (0, 0)
    best_move_key = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d_to = bfs_dist((nx, ny), (tx, ty), maxd=6)
        # If tie, prefer reducing opponent's progress (closer in manhattan to the same target).
        opp_d = abs(tx - ox) + abs(ty - oy)
        self_d = abs(tx - nx) + abs(ty - ny)
        # Also break ties by keeping move small/deterministic order
        key = (d_to, self_d - 0.1 * opp_d, abs(dx) + abs(dy), dx, dy)
        if best_move_key is None or key < best_move_key:
            best_move_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]