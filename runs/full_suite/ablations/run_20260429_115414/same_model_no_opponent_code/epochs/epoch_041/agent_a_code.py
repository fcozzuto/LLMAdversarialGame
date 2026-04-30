def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def mdist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    if not resources:
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best_move = (0, 0)
        best_val = -10**9
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                val = -mdist((nx, ny), (cx, cy))
                if val > best_val:
                    best_val, best_move = val, (dx, dy)
        return [int(best_move[0]), int(best_move[1])]

    resources_sorted = sorted(resources, key=lambda r: (mdist((sx, sy), r), r[0], r[1]))
    targets = resources_sorted[:3]
    center = ((w - 1) / 2.0, (h - 1) / 2.0)

    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        our_d = min(mdist((nx, ny), t) for t in targets)
        # Choose the target that minimizes opponent distance (to contest them)
        opp_d = min(mdist((ox, oy), t) for t in targets if t in targets)
        # Fallback if something odd happens (shouldn't)
        if opp_d is None:
            opp_d = mdist((ox, oy), targets[0])
        # Encourage slightly toward center to reduce dead-ends
        center_bias = -((nx - center[0]) ** 2 + (ny - center[1]) ** 2) * 0.01
        val = (-our_d) + 0.9 * (-opp_d) + center_bias
        # Deterministic tie-break: prefer smaller dx,dy ordering via coordinate
        if val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val, best_move = val, (dx, dy)

    return [int(best_move[0]), int(best_move[1])]