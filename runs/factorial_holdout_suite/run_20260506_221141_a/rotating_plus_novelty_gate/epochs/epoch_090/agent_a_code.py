def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    blocked = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in blocked:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def kdist(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # Choose target with race advantage; deterministic tie-break by (x,y)
    best = None
    best_val = -10**18
    res_sorted = sorted(resources)
    for rx, ry in res_sorted:
        sd = kdist(sx, sy, rx, ry)
        od = kdist(ox, oy, rx, ry)
        if sd == 0:
            return [0, 0]
        race = od - sd  # positive => we are closer or equal
        val = race * 10000 - sd * 3
        if race <= 0:
            val -= (0 - race) * 50  # still consider, but heavily prefer winning races
        if val > best_val:
            best_val = val
            best = (rx, ry)

    rx, ry = best

    # One-step greedy with obstacle avoidance
    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in blocked:
                moves.append((dx, dy))
    if not moves:
        return [0, 0]

    # Deterministic tie-break: minimize distance, then lexicographic dx,dy
    best_step = None
    best_step_dist = 10**18
    for dx, dy in sorted(moves):
        nx, ny = sx + dx, sy + dy
        d = kdist(nx, ny, rx, ry)
        if d < best_step_dist:
            best_step_dist = d
            best_step = (dx, dy)
        elif d == best_step_dist and best_step is not None:
            if (dx, dy) < best_step:
                best_step = (dx, dy)

    return [int(best_step[0]), int(best_step[1])]