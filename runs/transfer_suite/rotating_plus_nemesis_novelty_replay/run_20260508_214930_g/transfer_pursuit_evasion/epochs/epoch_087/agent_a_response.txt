def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    role = (observation.get("self_role", "") or "").lower()
    is_evader = any(k in role for k in ("evader", "runner", "fugitive"))
    is_pursuer = any(k in role for k in ("pursuer", "hunter", "seeker"))
    if not is_evader and not is_pursuer:
        is_pursuer = True

    obstacles = set()
    for b in observation.get("obstacles") or []:
        if isinstance(b, (list, tuple)) and len(b) >= 2:
            x, y = int(b[0]), int(b[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist2(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        return dx * dx + dy * dy

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    far_corner = max(corners, key=lambda c: dist2(c[0], c[1], ox, oy))
    if is_evader:
        tx, ty = far_corner
        best_score = -10**18
        best = (0, 0)
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not inside(nx, ny):
                continue
            # prioritize fleeing from pursuer, but also drift toward far corner
            s = dist2(nx, ny, ox, oy) * 10 - dist2(nx, ny, tx, ty)
            # avoid moving adjacent to obstacles too often (2 obstacles only; keep simple)
            if obstacles:
                for bx, by in obstacles:
                    if dist2(nx, ny, bx, by) <= 1:
                        s -= 25
            if s > best_score:
                best_score = s
                best = (dx, dy)
        return [int(best[0]), int(best[1])]

    # pursuer
    # If direct greedy step is blocked by obstacles, bias toward perpendicular sidestep by local scoring
    best_score = 10**18
    best = (0, 0)
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        s = dist2(nx, ny, ox, oy)
        # obstacle proximity penalty and discourage hugging
        if obstacles:
            for bx, by in obstacles:
                d = dist2(nx, ny, bx, by)
                if d == 0:
                    s += 10**9
                elif d == 1:
                    s += 15
                elif d <= 4:
                    s += 5
        # slight preference to keep moving in general direction
        s += (0 if (dx == 0 and dy == 0) else -0.2)
        if s < best_score:
            best_score = s
            best = (dx, dy)
    return [int(best[0]), int(best[1])]