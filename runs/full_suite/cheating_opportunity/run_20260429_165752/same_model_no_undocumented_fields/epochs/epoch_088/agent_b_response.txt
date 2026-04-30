def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    s = observation.get("self_position") or [0, 0]
    o = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    dirs.sort(key=lambda d: (d[0], d[1]))  # deterministic tie-break order
    if int(observation.get("turn_index") or 0) % 2:
        dirs = dirs[4:] + dirs[:4]

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    def king_dist(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def nearest_dist(x, y):
        if not resources:
            return 0
        md = 10**9
        for rx, ry in resources:
            d = king_dist(x, y, rx, ry)
            if d < md:
                md = d
        return md

    best_move = (0, 0)
    best_val = -10**18

    opp_near = nearest_dist(ox, oy)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        our_near = nearest_dist(nx, ny)

        # If we are on a resource, strongly prioritize (should be best anyway)
        on_res = 1 if (nx, ny) in set(resources) else 0

        # Value: smaller our distance is better; also try to keep ahead of opponent
        # Use deterministic small bias to prefer staying roughly towards center when tied.
        center_x = (w - 1) / 2.0
        center_y = (h - 1) / 2.0
        center_bias = -abs(nx - center_x) - abs(ny - center_y)

        val = (on_res * 10**6) + (opp_near - our_near) * 1000 + center_bias - (our_near * 5)

        if val > best_val:
            best_val = val
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]