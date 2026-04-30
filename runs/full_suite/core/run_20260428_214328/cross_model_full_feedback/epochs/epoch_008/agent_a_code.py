def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles", []) or []))
    resources = [(r[0], r[1]) for r in (observation.get("resources", []) or [])]
    def inside(x, y): return 0 <= x < w and 0 <= y < h
    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    def bfs_step(tx, ty):
        if (tx, ty) in obstacles or (tx, ty) == (ox, oy): return None
        from_x, from_y = sx, sy
        if (from_x, from_y) == (tx, ty): return (0, 0)
        q = [(from_x, from_y)]
        parent = {(from_x, from_y): None}
        qi = 0
        while qi < len(q):
            x, y = q[qi]; qi += 1
            if (x, y) == (tx, ty): break
            for dx, dy in moves:
                nx, ny = x + dx, y + dy
                if not inside(nx, ny): continue
                if (nx, ny) in obstacles: continue
                if (nx, ny) == (ox, oy): continue
                if (nx, ny) in parent: continue
                parent[(nx, ny)] = (x, y)
                q.append((nx, ny))
        if (tx, ty) not in parent: return None
        cur = (tx, ty)
        while parent[cur] is not None and parent[cur] != (from_x, from_y):
            cur = parent[cur]
        if parent[cur] is None: return None
        px, py = parent[cur]
        dx, dy = cur[0] - px, cur[1] - py
        if dx < -1 or dx > 1 or dy < -1 or dy > 1: return None
        return (dx, dy)
    # Choose best reachable resource: shortest path, tie by manhattan then coords.
    best = None
    for rx, ry in resources:
        if not inside(rx, ry): continue
        step = bfs_step(rx, ry)
        if step is None: continue
        d = abs(rx - sx) + abs(ry - sy)
        key = (d, rx, ry)
        if best is None or key < best[0]:
            best = (key, step)
    if best is not None:
        return [int(best[1][0]), int(best[1][1])]
    # Fallback: maximize distance from opponent; tie by closeness to center; avoid obstacles/opponent.
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    def dist2(x1, y1, x2, y2):
        dx = x1 - x2; dy = y1 - y2
        return dx*dx + dy*dy
    best_move = (0, 0); best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny): continue
        if (nx, ny) in obstacles: continue
        if (nx, ny) == (ox, oy): continue
        v = (dist2(nx, ny, ox, oy), -((nx - cx)*(nx - cx) + (ny - cy)*(ny - cy)), -abs(dx) - abs(dy), -nx, -ny)
        if best_val is None or v > best_val:
            best_val = v; best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]