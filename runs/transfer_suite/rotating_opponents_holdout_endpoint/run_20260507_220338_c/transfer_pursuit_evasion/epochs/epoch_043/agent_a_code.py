def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            blocked.add((int(p[0]), int(p[1])))

    role_s = str(observation.get("self_role", "") or "").lower()
    is_pursuer = ("purs" in role_s) or ("chase" in role_s) or ("hunter" in role_s)
    is_evader = ("evad" in role_s) or ("run" in role_s) or ("away" in role_s) or ("escape" in role_s) or ("runner" in role_s)
    if not (is_pursuer or is_evader):
        is_pursuer = True
    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    def bfs_next_dist(start, goal, maxd=7):
        if start == goal:
            return 0
        q = [(start[0], start[1], 0)]
        seen = {(start[0], start[1])}
        head = 0
        while head < len(q):
            x, y, d = q[head]
            head += 1
            if d >= maxd:
                continue
            nd = d + 1
            for dx, dy in deltas:
                nx, ny = x + dx, y + dy
                if not inb(nx, ny) or (nx, ny) in seen:
                    continue
                if (nx, ny) == goal:
                    return nd
                seen.add((nx, ny))
                q.append((nx, ny, nd))
        return 10**6

    moves = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny):
            moves.append((dx, dy, nx, ny))
    if not moves:
        return [0, 0]

    if is_pursuer:
        best = None
        bestd = 10**9
        for dx, dy, nx, ny in moves:
            if (nx, ny) == (ox, oy):
                return [dx, dy]
            d = bfs_next_dist((nx, ny), (ox, oy), 7)
            key = (d, abs(ox - nx) + abs(oy - ny), -nx, -ny)
            if d < bestd or best is None:
                bestd = d
                best = (dx, dy, key)
            elif best is not None and key < best[2]:
                best = (dx, dy, key)
        return [int(best[0]), int(best[1])]
    else:
        best = None
        bestScore = -10**18
        for dx, dy, nx, ny in moves:
            if (nx, ny) == (ox, oy):
                continue
            d = bfs_next_dist((nx, ny), (ox, oy), 7)
            edge_bias = (nx == 0 or nx == w - 1 or ny == 0 or ny == h - 1)
            score = d * 1000 + (1 if edge_bias else 0) - (abs(nx - sx) + abs(ny - sy))
            if best is None or score > bestScore:
                bestScore = score
                best = (dx, dy)
            elif best is not None and score == bestScore:
                # tie-break deterministically
                if (dx, dy) > tuple(best):
                    best = (dx, dy)
        return [int(best[0]), int(best[1])]