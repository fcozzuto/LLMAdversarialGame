def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obs_list = observation.get("obstacles", []) or []
    obstacles = set()
    for p in obs_list:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx >= dy else dy

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1), (0, 0)]
    legal = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            legal.append((dx, dy, nx, ny))
    if not legal or not resources:
        return [0, 0]

    # Heuristic: after moving, pick the best resource maximizing relative advantage over opponent.
    # If no advantage exists, still choose the closest resource to reduce opponent race chances.
    best = None
    for dx, dy, nx, ny in legal:
        local_best = -10**9
        for r in resources:
            rx, ry = int(r[0]), int(r[1])
            sd = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            adv = od - sd  # positive if we are closer (faster to capture)
            val = adv * 100 - sd
            if val > local_best:
                local_best = val
        # Slight tie-break toward moving to center to avoid dead-ends
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        dist_center = abs(nx - cx) + abs(ny - cy)
        val2 = local_best * 100 - dist_center
        if best is None or val2 > best[0] or (val2 == best[0] and (abs(dx) + abs(dy) < best[1])):
            best = (val2, abs(dx) + abs(dy), dx, dy)

    return [int(best[2]), int(best[3])]