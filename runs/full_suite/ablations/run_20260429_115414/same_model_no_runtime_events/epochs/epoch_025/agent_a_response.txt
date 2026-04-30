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
    if not resources:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    remaining = observation.get("remaining_resource_count")
    if remaining is None:
        remaining = len(resources)
    remaining = int(remaining)

    # Target selection: prioritize resources where we are closer than opponent; if none, deny by going to far-from-opponent resources.
    best = None
    best_val = None
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        tie = (rx + 31 * ry)  # deterministic tie-break
        if remaining <= 6:
            val = (do - ds) * 10 + (do - 1)  # more denial late
        else:
            val = (do - ds) * 10 + (do) - (ds // 2)  # more direct contest earlier
        val -= tie * 1e-6
        if best is None or val > best_val:
            best_val = val
            best = (rx, ry)

    tx, ty = best

    # Move: greedy toward target, avoid obstacles; tie-break by maximizing distance from opponent.
    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_score = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        d_to_t = cheb(nx, ny, tx, ty)
        d_from_o = cheb(nx, ny, ox, oy)
        score = (d_to_t, -d_from_o, dx, dy)
        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]