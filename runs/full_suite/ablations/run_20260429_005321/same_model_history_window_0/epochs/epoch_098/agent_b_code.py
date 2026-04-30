def choose_move(observation):
    W = observation["grid_width"]
    H = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    def in_bounds(x, y):
        return 0 <= x < W and 0 <= y < H

    def dist(a, b):
        ax, ay = a
        bx, by = b
        dx = ax - bx
        dy = ay - by
        return dx * dx + dy * dy

    # If no resources, just move to center-ish deterministically while avoiding obstacles
    if not resources:
        target = (W // 2, H // 2)
    else:
        best = None
        # Target resource that we can reach sooner, also considering opponent closeness
        for r in resources:
            rx, ry = r
            sd = dist((sx, sy), (rx, ry))
            od = dist((ox, oy), (rx, ry))
            score = (od - sd, -sd, rx, ry)  # prefer big advantage, then nearer
            if best is None or score > best[0]:
                best = (score, (rx, ry))
        target = best[1]

    tx, ty = target
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    # Deterministic move choice: go step that minimizes distance to target, avoiding obstacles
    best_move = (0, 0)
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue
        d = dist((nx, ny), (tx, ty))
        # If resources exist, slightly prefer moves that also reduce opponent-to-target distance
        opp_d = dist((ox, oy), (tx, ty))
        key = (d, opp_d, dx, dy)  # lexicographic; smaller d is better
        if best_key is None or key < best_key:
            best_key = key
            best_move = (dx, dy)

    # If all moves blocked (rare), stay put
    return [int(best_move[0]), int(best_move[1])]