def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (w - 1, h - 1)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def blocked(nx, ny):
        return nx < 0 or ny < 0 or nx >= w or ny >= h or (nx, ny) in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def score_target(tx, ty):
        # Prefer closer to target and farther from opponent slightly
        dx = tx - sx
        dy = ty - sy
        d = abs(dx) + abs(dy)
        od = abs(tx - ox) + abs(ty - oy)
        return -d + 0.05 * od

    if resources:
        tx, ty = min(resources, key=lambda p: abs(p[0] - sx) + abs(p[1] - sy))
    else:
        # Deterministic fallback: pick a corner (relative to opponent) then head there
        tx, ty = (w - 1, h - 1) if (ox + oy) <= (w - 1 + h - 1 - (ox + oy)) else (0, 0)

    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if blocked(nx, ny):
            continue
        # If opponent is very close, bias away
        close_op = abs(nx - ox) + abs(ny - oy)
        avoid = -20 if close_op <= 1 else 0
        # Move toward target
        toward = -(abs(tx - nx) + abs(ty - ny))
        val = toward + avoid
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]