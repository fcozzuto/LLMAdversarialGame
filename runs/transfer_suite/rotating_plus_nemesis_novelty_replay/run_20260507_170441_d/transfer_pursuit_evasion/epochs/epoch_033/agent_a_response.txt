def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    obstacles = set()
    for o in (observation.get("obstacles", []) or []):
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            x, y = int(o[0]), int(o[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def best_opponent_move(px, py):
        best = None
        best_val = -10**18
        for dx, dy in dirs:
            nx, ny = px + dx, py + dy
            if not ok(nx, ny):
                continue
            val = man(nx, ny, sx2, sy2)  # maximize distance from our hypothetical next pos
            if val > best_val:
                best_val = val
                best = (dx, dy)
        return best if best is not None else (0, 0)

    corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
    far_corner = max(corners, key=lambda c: man(sx, sy, c[0], c[1]))

    best_move = (0, 0)
    best_score = 10**18

    # Predict: choose our move that minimizes our distance after opponent evasion step.
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        sx2, sy2 = nx, ny  # for best_opponent_move closure
        odx, ody = best_opponent_move(ox, oy)
        nox, noy = ox + odx, oy + ody
        if not ok(nox, noy):
            nox, noy = ox, oy
        dist_after = man(nx, ny, nox, noy)

        # Tie-breakers: (1) reduce opponent's distance to farthest corner from us
        # (2) keep us closer to that corner to cut off
        corner_pressure = man(nox, noy, far_corner[0], far_corner[1]) - man(nx, ny, far_corner[0], far_corner[1])

        score = dist_after * 100 + corner_pressure
        if score < best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]