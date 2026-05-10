def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if inb(x, y):
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if inb(x, y) and (x, y) not in obstacles:
                resources.append((x, y))

    legal = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                legal.append((dx, dy))
    if not legal:
        return [0, 0]

    def mdist(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx + dy

    if resources:
        best_move = None
        best_key = None
        for dx, dy in legal:
            nsx, nsy = sx + dx, sy + dy
            # Evaluate move by potential to beat opponent on the best remaining resource.
            best_for_move = None
            for rx, ry in resources:
                self_d = mdist(nsx, nsy, rx, ry)
                opp_d = mdist(ox, oy, rx, ry)
                # Key: maximize advantage, then prefer closer self, then prefer closer to center.
                adv = opp_d - self_d
                self_center = mdist(nsx, nsy, (w - 1) // 2, (h - 1) // 2)
                key = (adv, -self_d, -self_center)
                if best_for_move is None or key > best_for_move:
                    best_for_move = key
            if best_key is None or best_for_move > best_key:
                best_key = best_for_move
                best_move = (dx, dy)
        return [int(best_move[0]), int(best_move[1])]

    # No visible resources: move deterministically toward center.
    cx, cy = (w - 1) // 2, (h - 1) // 2
    best_move = (0, 0)
    best_d = None
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        d = mdist(nx, ny, cx, cy)
        if best_d is None or d < best_d or (d == best_d and (dx, dy) < best_move):
            best_d = d
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]