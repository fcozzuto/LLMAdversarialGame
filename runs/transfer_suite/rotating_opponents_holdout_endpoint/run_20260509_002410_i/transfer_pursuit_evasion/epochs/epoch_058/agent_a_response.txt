def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    role = str(observation.get("self_role") or "").lower()
    is_evader = "evader" in role

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def blocked(x, y): return (x, y) in obstacles

    # Limited BFS distance (deterministic) to handle wall-running better than straight-line chasing
    def bfs_dist(start, goal, limit=16):
        if start == goal:
            return 0
        sx2, sy2 = start
        gx2, gy2 = goal
        qx = [sx2]; qy = [sy2]; d = [0]; qi = 0
        seen = {(sx2, sy2)}
        while qi < len(qx):
            x, y, dd = qx[qi], qy[qi], d[qi]
            qi += 1
            if dd >= limit:
                continue
            for dx, dy in deltas:
                nx, ny = x + dx, y + dy
                if not inb(nx, ny) or blocked(nx, ny) or (nx, ny) in seen:
                    continue
                if (nx, ny) == (gx2, gy2):
                    return dd + 1
                seen.add((nx, ny))
                qx.append(nx); qy.append(ny); d.append(dd + 1)
        return limit + 1

    # For evader: maximize distance; also prefer moves that increase path length (behind obstacle cover)
    best_val = None
    best_move = [0, 0]
    goal = (ox, oy)

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or blocked(nx, ny):
            continue
        dist = bfs_dist((nx, ny), goal, limit=16)
        mdx, mdy = nx - ox, ny - oy
        man = mdx * mdx + mdy * mdy

        # Tie-breaker: slight bias away/toward direct line to prevent oscillations
        bias = (man // 1)  # deterministic integer

        if is_evader:
            # maximize path distance primarily; small tie-break on direct separation
            val = (dist, bias)
            better = best_val is None or (val[0] > best_val[0] or (val[0] == best_val[0] and val[1] > best_val[1]))
        else:
            # minimize path distance primarily; small tie-break on direct closeness
            val = (dist, -bias)
            better = best_val is None or (val[0] < best_val[0] or (val[0] == best_val[0] and val[1] > best_val[1]))

        if better:
            best_val = val
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]