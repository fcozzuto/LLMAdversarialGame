def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    for rx, ry in resources:
        if rx == sx and ry == sy:
            return [0, 0]

    def cheb(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # Pick target resource where we are relatively closer than opponent (deterministic tie-break)
    best_t = None
    best_key = None
    for rx, ry in resources:
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        key = (sd - od, sd, rx, ry)  # prioritize advantage, then closer, then deterministic position
        if best_key is None or key < best_key:
            best_key = key
            best_t = (rx, ry)
    tx, ty = best_t

    dirs = (-1, 0, 1)
    best_move = [0, 0]
    best_val = None
    time_left = int(observation.get("turns_remaining", 0) or 0)
    urgency = 1.2 if time_left < 20 else 1.0

    for dx in dirs:
        for dy in dirs:
            nx, ny = sx + dx, sy + dy
            if nx < 0 or nx >= w or ny < 0 or ny >= h:
                continue
            if (nx, ny) in obstacles:
                continue

            # Value: progress to target, plus avoid giving opponent advantage nearby, deterministic tie-break
            self_d = cheb(nx, ny, tx, ty)
            opp_d = cheb(ox, oy, tx, ty)
            val = (self_d * urgency - (opp_d - cheb(ox, oy, nx, ny)) * 0.0)

            # If move would land on a resource, heavily prefer it
            if (nx, ny) in resources:
                val -= 1000

            key = (val, cheb(nx, ny, sx, sy), dx, dy)  # prefer smaller val, then less wandering
            if best_val is None or key < best_val:
                best_val = key
                best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]