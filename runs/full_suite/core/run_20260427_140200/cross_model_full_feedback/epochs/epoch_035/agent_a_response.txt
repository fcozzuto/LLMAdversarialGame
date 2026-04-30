def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    me = observation.get("self_position") or [0, 0]
    opp = observation.get("opponent_position") or [0, 0]
    sx, sy = int(me[0]), int(me[1])
    ox, oy = int(opp[0]), int(opp[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def legal(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    def best_for_move(nx, ny):
        if not resources:
            # Stay near center-ish; also slightly prefer moving toward opponent for contest pressure.
            center = (w // 2, h // 2)
            return -man(nx, ny, center[0], center[1]) + 0.1 * (man(nx, ny, ox, oy))
        best = None
        for rx, ry in resources:
            d_me = man(nx, ny, rx, ry)
            d_opp = man(ox, oy, rx, ry)
            # Higher is better: prevent opponent from reaching sooner, while still advancing.
            val = (d_opp - d_me) * 5 - d_me + 0.01 * (rx - nx) - 0.01 * (ry - ny)
            if best is None or val > best:
                best = val
        return best if best is not None else -10**9

    candidates = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if legal(nx, ny):
            candidates.append((best_for_move(nx, ny), dx, dy))

    if not candidates:
        return [0, 0]

    # Deterministic tie-break: highest value, then minimal distance to nearest resource, then fixed direction order.
    def nearest_dist(dx, dy):
        nx, ny = sx + dx, sy + dy
        if not resources:
            return 0
        return min(man(nx, ny, rx, ry) for rx, ry in resources)

    candidates.sort(key=lambda t: (-t[0], nearest_dist(t[1], t[2]), t[1], t[2]))
    _, dx, dy = candidates[0]
    return [int(dx), int(dy)]