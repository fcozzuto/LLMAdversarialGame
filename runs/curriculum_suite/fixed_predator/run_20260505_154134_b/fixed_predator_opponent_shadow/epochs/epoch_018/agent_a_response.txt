def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    rem = observation.get("remaining_resource_count", 0)

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def valid(x, y):
        return inb(x, y) and (x, y) not in obs

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    if not resources:
        best = [0, 0]
        bestv = -10**9
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            v = cheb(nx, ny, ox, oy)
            if v < bestv:
                bestv = v
                best = [dx, dy]
            elif v == bestv:
                if (nx, ny) < (sx + best[0], sy + best[1]):
                    best = [dx, dy]
        return best

    best_move = [0, 0]
    best_val = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        # Evaluate immediate advantage to secure a resource next
        best_for_move = -10**18
        for cx, cy in resources:
            sd = cheb(nx, ny, cx, cy)
            od = cheb(ox, oy, cx, cy)
            # Prefer moves that make us closer than opponent; tie-break by closeness to resource
            val = (od - sd) * 1000 - sd
            if sd == 0:
                val += 100000
            # If few resources remain, slightly prioritize distance to finish line
            if rem <= 4:
                val += (4 - sd) * 3
            if val > best_for_move:
                best_for_move = val
        # Tie-break deterministically toward not moving, then toward smaller dx,dy lexicographically
        if best_for_move > best_val:
            best_val = best_for_move
            best_move = [dx, dy]
        elif best_for_move == best_val:
            if [dx, dy] == [0, 0] and best_move != [0, 0]:
                best_move = [dx, dy]
            elif [dx, dy] < best_move:
                best_move = [dx, dy]
    return best_move