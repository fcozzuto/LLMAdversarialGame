def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
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

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def md(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx + dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    cx, cy = (w - 1) // 2, (h - 1) // 2

    best_move = (0, 0)
    best_val = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        val = 0
        if resources:
            # Favor resources we can reach sooner than opponent; penalize those they can grab first.
            for rx, ry in resources:
                ds = md(nx, ny, rx, ry)
                do = md(ox, oy, rx, ry)
                diff = do - ds  # positive: we are closer
                # Diminish value with distance; strongly weight being ahead.
                local = diff * 20 - ds
                # Mild tie-break: prefer resources closer to opponent disadvantage (more spread).
                local += (diff * diff) // 5
                # If opponent is much closer, discourage.
                if diff < -2:
                    local -= (-diff) * 10
                if local > val:
                    val = local
        else:
            val = -md(nx, ny, cx, cy)

        # Small preference for staying near our overall progress: reduce distance to best attainable resource.
        # Deterministic "progress" term using current positions (not future rollout).
        if resources:
            cur_best = 10**9
            for rx, ry in resources:
                d = md(sx, sy, rx, ry)
                if d < cur_best:
                    cur_best = d
            val -= md(nx, ny, sx, sy) // 2
            val += (cur_best - md(nx, ny, sx, sy)) // 4

        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]