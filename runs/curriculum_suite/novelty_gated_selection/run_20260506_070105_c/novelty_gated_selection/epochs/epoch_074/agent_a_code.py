def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for o in observation.get("obstacles", []) or []:
        if o is not None and len(o) >= 2:
            obstacles.add((int(o[0]), int(o[1])))

    resources = []
    for r in observation.get("resources", []) or []:
        if r is not None and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if (rx, ry) not in obstacles:
                resources.append((rx, ry))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx + dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    cx, cy = (w - 1) // 2, (h - 1) // 2

    # If no resources, drift to center while moving away from opponent
    if not resources:
        best = None
        bestv = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                nx, ny = sx, sy
            v = -man(nx, ny, ox, oy) - 0.01 * man(nx, ny, cx, cy)
            if bestv is None or v > bestv:
                bestv = v
                best = [dx, dy]
        return best

    best_move = [0, 0]
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            nx, ny = sx, sy

        # Prefer moves that secure or deny resources where opponent is relatively close
        best_capture = -10**9
        for rx, ry in resources:
            ds = man(nx, ny, rx, ry)
            do = man(ox, oy, rx, ry)
            # Positive when we are closer than opponent; also prefer shorter actual distance
            val = (do - ds) * 10 - ds
            # Mild preference to move toward contested zones (where opponent is not too far)
            val += 2 if do <= 3 else (1 if do <= 4 else 0)
            if val > best_capture:
                best_capture = val

        # Secondary: reduce opponent distance and drift toward center
        score = best_capture - 0.05 * man(nx, ny, ox, oy) - 0.01 * man(nx, ny, cx, cy)

        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]
    return best_move