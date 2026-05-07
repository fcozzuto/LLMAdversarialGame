def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obst = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obst:
                resources.append((x, y))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    def best_target():
        if not resources:
            return None
        best = None
        for rx, ry in resources:
            ds = cheb(sx, sy, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # Prefer resources we're closer to; add small tie-break for higher "urgency" to finish sooner
            score = (do - ds) * 100 - ds
            if best is None or score > best[0]:
                best = (score, rx, ry)
        return (best[1], best[2]) if best else None

    target = best_target()
    # Candidate moves (including stay)
    moves = [(0, 0), (-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]
    best_move = (0, 0)
    best_val = None

    # If no resources, drift to center
    tx, ty = (w // 2, h // 2) if target is None else (target[0], target[1])

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h): 
            continue
        if (nx, ny) in obst:
            continue
        # Value: go closer to target; also discourage stepping "behind" opponent wave
        dself = cheb(nx, ny, tx, ty)
        dob = cheb(ox, oy, tx, ty)
        v = -dself * 10 + (dob - dself)  # higher when we remain advantaged
        # small preference to avoid cycles near edges
        v -= (nx == 0 or nx == w - 1) + (ny == 0 or ny == h - 1)
        if best_val is None or v > best_val:
            best_val = v
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]