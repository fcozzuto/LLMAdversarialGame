def choose_move(observation):
    W = int(observation.get("grid_width") or 8)
    H = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [W - 1, H - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H and (x, y) not in obstacles:
                resources.append((x, y))

    if any(rx == sx and ry == sy for rx, ry in resources):
        return [0, 0]

    def valid(x, y):
        return 0 <= x < W and 0 <= y < H and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    best_key = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            nx, ny = sx, sy
        if not resources:
            # Fallback: move toward opponent to force contesting resources indirectly
            move = [0, 0]
            if ox != nx or oy != ny:
                ddx = 0 if ox == nx else (1 if ox > nx else -1)
                ddy = 0 if oy == ny else (1 if oy > ny else -1)
                move = [ddx, ddy]
            return move

        # For each resource, compute "win likelihood" = opponent distance minus our distance (bigger is better).
        # Prefer moves that create the biggest margin on at least one reachable resource.
        local_best = -10**9
        chosen_r = None
        for rx, ry in resources:
            sd = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            # Strongly avoid giving opponent an immediate advantage; break ties by smaller self distance.
            margin = od - sd
            # Mild tie-break: prefer resources closer to us as long as margin isn't worse.
            val = margin * 1000 - sd
            if val > local_best:
                local_best = val
                chosen_r = (rx, ry)

        rx, ry = chosen_r
        sd = cheb(nx, ny, rx, ry)
        od = cheb(ox, oy, rx, ry)
        # Secondary: if we can reach much sooner than opponent, prioritize; otherwise, still keep margin.
        key = (local_best, (od - sd), -sd, -cheb(nx, ny, sx, sy), dx, dy)
        if best_key is None or key > best_key:
            best_key = key
            best = (dx, dy)

    return [int(best[0]), int(best[1])]