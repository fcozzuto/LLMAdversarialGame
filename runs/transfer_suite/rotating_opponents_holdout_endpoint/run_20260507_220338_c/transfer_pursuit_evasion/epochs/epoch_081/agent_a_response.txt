def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    role_s = str(observation.get("self_role", "")).lower()
    i_am_evader = not any(k in role_s for k in ("pursuer", "chaser", "catch", "pursuit"))

    obstacles = observation.get("obstacles") or []
    blocked = set()
    for p in obstacles:
        if p and len(p) >= 2:
            bx, by = int(p[0]), int(p[1])
            if 0 <= bx < w and 0 <= by < h:
                blocked.add((bx, by))

    def clamp_in(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in blocked

    def cheb(x, y):
        dx = abs(x - ox)
        dy = abs(y - oy)
        return dx if dx >= dy else dy

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    far_corner = max(corners, key=lambda c: abs(c[0] - sx) + abs(c[1] - sy))
    def man_to_corner(x, y, c):
        return abs(c[0] - x) + abs(c[1] - y)

    candidates = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    best_val = None
    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        if not clamp_in(nx, ny):
            continue
        if i_am_evader:
            # maximize distance; also head toward a far corner deterministically
            val = (cheb(nx, ny), -man_to_corner(nx, ny, far_corner), -((nx == sx and ny == sy)), -nx, -ny)
            if best_val is None or val > best_val:
                best_val, best = val, (dx, dy)
        else:
            # minimize distance; break ties by steering away from our own corners less aggressively
            val = (-cheb(nx, ny), -man_to_corner(nx, ny, far_corner), nx, ny)
            if best_val is None or val > best_val:
                best_val, best = val, (dx, dy)

    if best is None:
        # fall back to any valid step (prefer staying still if blocked not possible)
        for dx, dy in candidates:
            nx, ny = sx + dx, sy + dy
            if clamp_in(nx, ny):
                best = (dx, dy)
                break
        if best is None:
            best = (0, 0)
    return [int(best[0]), int(best[1])]