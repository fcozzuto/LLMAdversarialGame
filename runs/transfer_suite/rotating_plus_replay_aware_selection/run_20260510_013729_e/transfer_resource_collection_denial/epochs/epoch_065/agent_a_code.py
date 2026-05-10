def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    if not resources:
        return [0, 0]

    obst = {(x, y) for x, y in obstacles}
    cand = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def cheb(x1, y1, x2, y2):
        dx = x2 - x1
        if dx < 0:
            dx = -dx
        dy = y2 - y1
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    resources_sorted = sorted(resources, key=lambda p: (p[0] * 8 + p[1], p[0], p[1]))
    best_val = -10**18
    best_move = [0, 0]

    for dx, dy in cand:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obst:
            continue

        # Evaluate by the best resource we can pressure next turn
        v = -10**18
        for rx, ry in resources_sorted:
            sd = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            cap = 5.0 if sd == 0 else 0.0
            lead = od - sd  # bigger => we are closer than opponent
            # Also consider "denial" by favoring resources where opponent is close but we can intercept
            score = cap + 1.8 * lead - 0.25 * sd
            if score > v:
                v = score

        # Small deterministic tie-break: prefer moves that reduce distance to the best target center
        if v > best_val:
            best_val = v
            best_move = [dx, dy]

    return best_move