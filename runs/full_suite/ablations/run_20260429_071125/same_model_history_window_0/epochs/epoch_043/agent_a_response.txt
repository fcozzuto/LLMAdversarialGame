def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    dirs = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def dist(a, b): return abs(a[0]-b[0]) + abs(a[1]-b[1])
    if resources:
        # Material change: alternate between "contested grab" and "direct nearest"
        best = None
        for rx, ry in resources:
            if (rx, ry) in obstacles: 
                continue
            d_us = dist((sx, sy), (rx, ry))
            d_op = dist((ox, oy), (rx, ry))
            if observation["turn_index"] % 2 == 0:
                # Contested: prefer where we are closer; small tie-break to move forward
                key = (d_us - d_op, d_us, -rx - ry)
            else:
                # Direct: prefer nearest reachable-ish by Manhattan
                key = (d_us, abs(rx - (w//2)) + abs(ry - (h//2)))
            if best is None or key < best[0]:
                best = (key, (rx, ry))
        tx, ty = best[1]
        # Greedy step toward target that avoids obstacles and bounds; also avoid stepping next to opponent on contested turns
        prefer_avoid = (observation["turn_index"] % 2 == 0)
        best_step = None
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles: 
                continue
            # Engine allows staying; if blocked all around, staying will be the only option (handled below)
            new_d = dist((nx, ny), (tx, ty))
            opp_d = dist((nx, ny), (ox, oy))
            score = (new_d, -opp_d if prefer_avoid else opp_d)
            if best_step is None or score < best_step[0]:
                best_step = (score, (dx, dy))
        if best_step is not None:
            return [best_step[1][0], best_step[1][1]]
    # No resources (or all blocked): go to center while not colliding with obstacles
    cx, cy = w//2, h//2
    best_step = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        score = dist((nx, ny), (cx, cy)), -dist((nx, ny), (ox, oy))
        if best_step is None or score < best_step[0]:
            best_step = (score, (dx, dy))
    if best_step is None:
        return [0, 0]
    return [best_step[1][0], best_step[1][1]]