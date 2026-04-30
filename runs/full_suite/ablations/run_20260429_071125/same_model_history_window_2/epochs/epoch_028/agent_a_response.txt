def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) == 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def mdist(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx + dy

    def inside_free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_val = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside_free(nx, ny):
            continue

        if resources:
            cand = -10**18
            for rx, ry in resources:
                myd = mdist(nx, ny, rx, ry)
                opd = mdist(ox, oy, rx, ry)
                # Prefer resources where we are ahead; strong penalty if behind.
                val = (opd - myd)
                if opd <= myd:
                    val -= 2 * (myd - opd + 1)
                # Slight bias toward nearer and earlier/upper-left determinism
                val -= 0.03 * myd
                val -= 0.001 * (rx + ry)
                if val > cand:
                    cand = val
            val = cand
        else:
            cx, cy = w // 2, h // 2
            val = -(mdist(nx, ny, cx, cy))

        # Deterministic tie-break: lexicographically smaller (dx,dy) for same val
        if val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)

    dx, dy = best_move
    return [int(dx), int(dy)]