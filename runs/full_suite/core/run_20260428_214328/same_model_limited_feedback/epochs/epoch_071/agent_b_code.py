def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = observation.get("obstacles", [])
    blocked = set()
    for p in obstacles:
        blocked.add((p[0], p[1]))
    resources = observation.get("resources", [])
    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    def cheb2(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        return dx * dx + dy * dy

    candidates = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny):
            candidates.append((dx, dy, nx, ny))
    if not candidates:
        return [0, 0]

    if not resources:
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best = min(candidates, key=lambda t: cheb2(t[2], t[3], cx, cy))
        return [best[0], best[1]]

    best_move = candidates[0]
    best_val = None
    for dx, dy, nx, ny in candidates:
        best_for_resource = None
        # Prefer resources we can reach sooner while keeping opponent farther to that same resource
        for r in resources:
            rx, ry = r[0], r[1]
            v = -cheb2(nx, ny, rx, ry) + cheb2(ox, oy, rx, ry)
            if best_for_resource is None or v > best_for_resource:
                best_for_resource = v
        # Tie-break deterministically: closer to center, then lower dx/dy lexicographically
        cx, cy = (w - 1) // 2, (h - 1) // 2
        tie = (cheb2(nx, ny, cx, cy), dx, dy)
        val = (best_for_resource, -tie[0], tie[1], tie[2])
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy, nx, ny)
    return [best_move[0], best_move[1]]