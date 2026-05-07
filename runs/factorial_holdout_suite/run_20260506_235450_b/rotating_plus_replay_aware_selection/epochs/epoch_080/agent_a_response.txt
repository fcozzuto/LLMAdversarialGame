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

    def dist(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    if not resources:
        return [0, 0]

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    # Local one-step lookahead: choose move that improves being first to resources.
    # Deterministic: consider resources in fixed order, and tie-break by move.
    ordered_resources = []
    for r in resources:
        rx, ry = int(r[0]), int(r[1])
        # Prefer nearer resources to reduce dithering, stable by coordinates
        ordered_resources.append((dist(sx, sy, rx, ry), rx, ry))
    ordered_resources.sort()

    best = None
    best_val = None
    for dx, dy, nx, ny in legal:
        # Evaluate up to a few closest resources for speed and stability.
        val = -10**9
        for i in range(min(5, len(ordered_resources))):
            _, rx, ry = ordered_resources[i]
            sd = dist(nx, ny, rx, ry)
            od = dist(ox, oy, rx, ry)
            # Positive if we are closer; larger margin is better.
            # Extra push for smaller self distance to avoid chasing far denial targets.
            margin = od - sd
            score = margin * 10 - sd
            # If we are already at the resource, extremely good.
            if nx == rx and ny == ry:
                score += 10**6
            if score > val:
                val = score
        # Deterministic tie-break: prefer smaller |dx| then smaller |dy| then lexicographic.
        tb = (abs(dx) + abs(dy), abs(dx), abs(dy), dx, dy)
        key = (val, -tb[0], -tb[1], -tb[2], -tb[3], -tb[4])
        if best_val is None or key > best_val:
            best_val = key
            best = (dx, dy)

    return [int(best[0]), int(best[1])]