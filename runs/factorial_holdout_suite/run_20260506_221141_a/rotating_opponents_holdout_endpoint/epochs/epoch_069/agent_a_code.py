def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    sx, sy = int(sx), int(sy)
    ox, oy = observation.get("opponent_position", [0, 0])
    ox, oy = int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    candidates = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def cheb(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    rem = int(observation.get("remaining_resource_count", len(resources)) or 0)
    time_left = int(observation.get("turns_remaining", 0) or 0)
    urgency = 0.6 if time_left > 20 else 1.2
    closeness = 0.25 if rem > 6 else 0.65

    best_move = [0, 0]
    best_val = -10**9

    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        # Evaluate by predicted advantage to the best next target
        max_adv = -10**9
        for rx, ry in resources:
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # Positive when we reach earlier (or at least not later)
            adv = (do - ds) * urgency
            # Encourage reducing distance to some resource even if not winning it
            adv += -ds * closeness
            if adv > max_adv:
                max_adv = adv

        # Mild anti-stall: prefer moves that reduce distance to the closest resource
        # (keeps determinism without full search)
        min_ds = 10**9
        for rx, ry in resources:
            ds0 = cheb(sx, sy, rx, ry)
            ds1 = cheb(nx, ny, rx, ry)
            if ds1 < min_ds:
                min_ds = ds1
        val = max_adv - min_ds * 0.05
        if val > best_val:
            best_val = val
            best_move = [dx, dy]

    return best_move