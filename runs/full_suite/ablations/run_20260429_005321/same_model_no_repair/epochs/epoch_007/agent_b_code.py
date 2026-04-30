def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", [])
    obs = set((p[0], p[1]) for p in observation.get("obstacles", []))
    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    def bfs_dist(start, goal):
        if start == goal:
            return 0
        if goal in obs or start in obs:
            return None
        qx, qy, qd = [start[0]], [start[1]], 0
        head = 0
        seen = {(start[0], start[1])}
        depth_limit = 12
        while head < len(qx):
            x, y = qx[head], qy[head]
            d = qd if head == 0 else None
            head += 1
        # Rebuild simple BFS with level tracking (deterministic, small grid)
        queue = [(start[0], start[1], 0)]
        seen = {(start[0], start[1])}
        while queue:
            x, y, d = queue.pop(0)
            if d > depth_limit:
                continue
            for dx, dy in deltas:
                nx, ny = x + dx, y + dy
                if not inb(nx, ny) or (nx, ny) in obs or (nx, ny) in seen:
                    continue
                if nx == goal[0] and ny == goal[1]:
                    return d + 1
                seen.add((nx, ny))
                queue.append((nx, ny, d + 1))
        return None

    def best_for_pos(px, py):
        if not resources:
            tx, ty = w // 2, h // 2
            return -man(px, py, tx, ty), man(px, py, tx, ty)
        best_val = None
        best_dist = 10**9
        best_res = None
        for rx, ry in resources:
            myd = bfs_dist((px, py), (rx, ry))
            if myd is None:
                continue
            opd = man(ox, oy, rx, ry)
            val = (opd - myd) * 1000 - myd  # strong preference for being able to take sooner
            if best_val is None or val > best_val or (val == best_val and (myd < best_dist or (myd == best_dist and (rx, ry) < best_res))):
                best_val, best_dist, best_res = val, myd, (rx, ry)
        if best_val is None:
            return -man(px, py, w // 2, h // 2), 10**9
        return best_val, best_dist

    order = deltas
    best_move = (0, 0)
    best_key = None
    for dx, dy in order:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        val, myd = best_for_pos(nx, ny)
        # tie-break: closer to resources; then deterministic smallest move in order
        key = (val, -myd, -nx, -ny, dx, dy)
        if best_key is None or key > best_key:
            best_key = key
            best_move = (dx, dy)
    return [best_move[0], best_move[1]]