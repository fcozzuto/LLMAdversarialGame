def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", (0, 0)) or (0, 0)
    op = observation.get("opponent_position", (0, 0)) or (0, 0)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

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

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def manhattan(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    cx, cy = (w - 1) // 2, (h - 1) // 2
    best_move = (0, 0)
    best_score = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            nx, ny = sx, sy  # mirror engine rejection deterministically

        # Center bias (prevents getting corner-locked) + resource race advantage
        center_pen = 0.02 * manhattan(nx, ny, cx, cy)

        my_best = -10**9
        for rx, ry in resources:
            myd = manhattan(nx, ny, rx, ry)
            opd = manhattan(ox, oy, rx, ry)
            # Prefer resources where we are closer than opponent; avoid too-distant targets
            adv = (opd - myd)
            score = adv - 0.01 * myd
            if score > my_best:
                my_best = score

        # Also discourage moves that step away from "race leader" too much
        myd_from_current = min(manhattan(nx, ny, rx, ry) for rx, ry in resources)
        score = my_best - center_pen - 0.03 * myd_from_current

        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]