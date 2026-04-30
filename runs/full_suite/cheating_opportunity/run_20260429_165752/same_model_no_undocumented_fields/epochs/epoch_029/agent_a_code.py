def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    s = observation.get("self_position", [0, 0]) or [0, 0]
    o = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

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

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = [0, 0]
    best_val = -10**18

    my_paths = observation.get("self_path")
    opp_paths = observation.get("opponent_path")
    recent_bias = 0
    if my_paths is None:
        recent_bias = 0
    else:
        recent_bias = 0

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        val = 0.0

        # Tie-break: prefer forward progress on average toward center if resources empty
        if not resources:
            cx, cy = w // 2, h // 2
            val = -cheb(nx, ny, cx, cy) + 0.0001 * (dx == 0 and dy == 0)
        else:
            for rx, ry in resources:
                d_me = cheb(nx, ny, rx, ry)
                d_op = cheb(ox, oy, rx, ry)
                # Prefer resources where we are closer than opponent (or will close the gap).
                gain = d_op - d_me
                if gain > 0:
                    val += 3.5 * gain
                else:
                    val += 0.6 * gain - 0.2 * d_me
            # Subtle safety: avoid stepping into cells adjacent to obstacles heavily blocked (local check)
            adj_block = 0
            for ax in (-1, 0, 1):
                for ay in (-1, 0, 1):
                    if ax == 0 and ay == 0:
                        continue
                    tx, ty = nx + ax, ny + ay
                    if 0 <= tx < w and 0 <= ty < h and (tx, ty) in obstacles:
                        adj_block += 1
            val -= 0.05 * adj_block

        val += recent_bias
        if val > best_val:
            best_val = val
            best = [dx, dy]

    return [int(best[0]), int(best[1])]