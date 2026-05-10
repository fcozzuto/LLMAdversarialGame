def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = map(int, observation.get("self_position") or (0, 0))
    ox, oy = map(int, observation.get("opponent_position") or (0, 0))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                obstacles.add((x, y))

    oppT = set()
    for p in observation.get("opponent_territory", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                oppT.add((x, y))

    unclaimed = observation.get("unclaimed_cells", []) or []
    unclaimed_set = set()
    for p in unclaimed:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y) and (x, y) not in obstacles:
                unclaimed_set.add((x, y))

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    moves = [(-1, 0), (0, -1), (0, 0), (0, 1), (1, 0), (-1, -1), (-1, 1), (1, -1), (1, 1)]
    best = None
    bestv = -10**18

    # Precompute a few nearest unclaimed targets to keep deterministic and cheap
    target_list = list(unclaimed_set)
    target_list.sort(key=lambda t: (abs(t[0] - sx) + abs(t[1] - sy), t[0], t[1]))
    top_targets = target_list[:8]

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        man_to_op = abs(nx - ox) + abs(ny - oy)
        center_dist = abs(nx - cx) + abs(ny - cy)

        # Greedy territory flip / pressure
        flip_gain = 0
        if (nx, ny) in oppT:
            flip_gain = 60

        # Encourage moving toward nearest unclaimed (likely expansion)
        unclaimed_gain = 0
        if top_targets:
            dbest = min(abs(nx - tx) + abs(ny - ty) for tx, ty in top_targets)
            unclaimed_gain = max(0, 30 - 2 * dbest)  # 30..0

        # Avoid being trapped right next to opponent (prevents oscillation)
        safety_pen = 0
        if man_to_op <= 1:
            safety_pen = 12
        if man_to_op == 0:
            safety_pen = 25

        # Slight bias to routes that reduce distance to opponent when we are not immediately penalized
        approach = 0
        if man_to_op >= 2:
            approach = max(0, 10 - man_to_op)

        v = flip_gain + unclaimed_gain + approach - safety_pen - center_dist * 0.2
        if v > bestv or (v == bestv and (dx, dy) < best):
            bestv = v
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]