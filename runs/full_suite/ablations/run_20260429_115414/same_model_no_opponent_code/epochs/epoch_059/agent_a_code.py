def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def king(a, b):
        ax, ay = a
        bx, by = b
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    if not resources:
        return [0, 0]

    best_r = None
    best_score = -10**18
    for rx, ry in resources:
        myd = king((sx, sy), (rx, ry))
        opd = king((ox, oy), (rx, ry))
        score = (opd - myd) * 100 - myd - (1 if (rx, ry) == (w - 1 - sx, h - 1 - sy) else 0)
        if score > best_score:
            best_score = score
            best_r = (rx, ry)

    rx, ry = best_r
    best_mv = (0, 0)
    best_mv_score = -10**18

    # Prefer moves that get closer to target and keep ahead of opponent, with obstacle avoidance.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        myd = king((nx, ny), (rx, ry))
        opd = king((ox, oy), (rx, ry))
        # Small bias to reduce being blocked: avoid stepping next to obstacles when possible.
        adj_obs = 0
        for ax, ay in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            tx, ty = nx + ax, ny + ay
            if 0 <= tx < w and 0 <= ty < h and (tx, ty) in obstacles:
                adj_obs += 1
        mv_score = (opd - myd) * 120 - myd * 3 - adj_obs * 2 - (1 if (dx == 0 and dy == 0) else 0)
        if mv_score > best_mv_score:
            best_mv_score = mv_score
            best_mv = (dx, dy)

    return [int(best_mv[0]), int(best_mv[1])]