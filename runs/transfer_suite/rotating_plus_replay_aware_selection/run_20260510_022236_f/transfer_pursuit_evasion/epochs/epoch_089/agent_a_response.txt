def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    role = str(observation.get("self_role", "") or "").lower()
    is_evader = any(k in role for k in ("evader", "runner", "escape", "flee"))

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def blocked(x, y):
        return (x, y) in obstacles or x < 0 or x >= w or y < 0 or y >= h

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    far_corner = max(corners, key=lambda c: abs(c[0] - ox) + abs(c[1] - oy))
    near_corner = min(corners, key=lambda c: abs(c[0] - ox) + abs(c[1] - oy))

    def free_neighbors(x, y):
        cnt = 0
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if inb(nx, ny):
                cnt += 1
        return cnt

    def corner_dist(x, y):
        return abs(x - far_corner[0]) + abs(y - far_corner[1])

    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if blocked(nx, ny):
            nx, ny = sx, sy
            dx, dy = 0, 0

        md = abs(nx - ox) + abs(ny - oy)
        fn = free_neighbors(nx, ny)
        cd = corner_dist(nx, ny)
        # Deterministic ordering tie-break: prefer consistent spatial bias
        spatial = (nx * 31 + ny * 17) % 997

        if is_evader:
            # Keep distance, also drift toward farthest corner (corner-running opponent).
            val = (md, cd, fn, -spatial)
        else:
            # Chase to capture: minimize distance, but avoid dead-ends; also drift toward near-corner.
            nd_corner = abs(nx - near_corner[0]) + abs(ny - near_corner[1])
            val = (-md, -nd_corner, fn, -spatial)

        if best is None or val > best[0]:
            best = (val, [dx, dy])

    return best[1]