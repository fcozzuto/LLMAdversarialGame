def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def man(a, b, c, d):
        dx = a - c
        if dx < 0:
            dx = -dx
        dy = b - d
        if dy < 0:
            dy = -dy
        return dx + dy

    best = None
    best_val = None
    # If we have resources, bias to a resource that we can reach sooner than opponent.
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        if not resources:
            # Fall back: move away from opponent to control access lanes, prefer toward center.
            cx, cy = (w - 1) // 2, (h - 1) // 2
            val = man(nx, ny, ox, oy) - 0.1 * (man(nx, ny, cx, cy))
        else:
            val = 10**9
            for rx, ry in resources:
                d_me = man(nx, ny, rx, ry)
                d_op = man(ox, oy, rx, ry)
                # Prefer capturing/contesting: lower is better.
                # If opponent closer, heavily penalize; if tie, slightly prefer.
                contest = (d_me - d_op)
                score = d_me + 3.5 * (contest if contest > 0 else 0) - 0.4 * (contest if contest <= 0 else 0)
                # Small tie-break: prefer nearer to board center to keep options.
                cx, cy = (w - 1) // 2, (h - 1) // 2
                score += 0.03 * man(nx, ny, cx, cy)
                if score < val:
                    val = score
        # Deterministic tie-break: prefer lexicographically smaller move among equals by fixed order.
        if best_val is None or val < best_val - 1e-9:
            best_val = val
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]