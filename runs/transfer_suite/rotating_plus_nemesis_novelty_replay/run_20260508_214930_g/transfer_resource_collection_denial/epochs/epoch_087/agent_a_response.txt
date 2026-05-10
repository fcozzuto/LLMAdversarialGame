def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(a, b):
        dx = a[0] - b[0]
        if dx < 0: dx = -dx
        dy = a[1] - b[1]
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # Pick resource where we are relatively closer than opponent.
    best = None
    best_key = None
    for rx, ry in resources:
        sd = cheb((sx, sy), (rx, ry))
        od = cheb((ox, oy), (rx, ry))
        # Prefer: maximize margin (od-sd), then minimize our distance, then prefer earlier in scan deterministically.
        key = (od - sd, -sd, -rx, -ry)
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)

    rx, ry = best
    # Choose a move that reduces distance to the chosen target, while avoiding obstacles if possible.
    candidates = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if nx < 0 or nx >= w or ny < 0 or ny >= h:
                continue
            hit = (nx, ny) in obstacles
            nd = cheb((nx, ny), (rx, ry))
            # Prefer reducing our distance; penalize hitting obstacle; tie-break by closeness to target margin.
            # Also slightly prefer moving toward improving contest on the same resource.
            self_d = cheb((nx, ny), (rx, ry))
            opp_d = cheb((ox, oy), (rx, ry))
            key = (not hit, (opp_d - self_d), -nd, -dx * dx - dy * dy, dx, dy)
            candidates.append((key, [dx, dy]))
    candidates.sort(reverse=True, key=lambda t: t[0])
    return candidates[0][1] if candidates else [0, 0]