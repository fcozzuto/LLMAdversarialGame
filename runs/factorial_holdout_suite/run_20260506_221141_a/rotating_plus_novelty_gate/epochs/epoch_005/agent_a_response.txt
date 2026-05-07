def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs_set = set()
    for p in obstacles:
        x, y = int(p[0]), int(p[1])
        if 0 <= x < w and 0 <= y < h:
            obs_set.add((x, y))

    if not resources:
        return [0, 0]

    def cheb(a, b, c, d):
        dx = a - c
        dy = b - d
        return abs(dx) if abs(dx) > abs(dy) else abs(dy)

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obs_set:
            continue

        best_margin = None
        best_self_d = None

        for r in resources:
            rx, ry = int(r[0]), int(r[1])
            if (rx, ry) in obs_set:
                continue
            sd = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            margin = od - sd  # higher is better
            if best_margin is None or margin > best_margin or (margin == best_margin and sd < best_self_d):
                best_margin = margin
                best_self_d = sd

        if best_margin is None:
            continue

        # Prefer moves that keep winning pressure; break ties by closer approach and then lexicographic delta.
        cand = (best_margin, -best_self_d, -cheb(nx, ny, w - 1, h - 1))
        if best is None or cand > best[0] or (cand == best[0] and (dx, dy) < best[1]):
            best = (cand, (dx, dy))

    if best is None:
        return [0, 0]
    return [best[1][0], best[1][1]]