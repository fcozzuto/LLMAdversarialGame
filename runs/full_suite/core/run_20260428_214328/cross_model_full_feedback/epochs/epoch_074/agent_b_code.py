def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = (int(x) for x in observation.get("self_position", [0, 0]))
    ox, oy = (int(x) for x in observation.get("opponent_position", [w - 1, h - 1]))
    # obstacles set
    obst = set()
    for p in observation.get("obstacles") or []:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))
    # resources near us (prefer gathering)
    resources = []
    for p in observation.get("resources") or []:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obst:
                resources.append((x, y))
    # If there is a resource, go towards nearest by Chebyshev distance
    if resources:
        best = None
        bestd = None
        for rx, ry in resources:
            d = max(abs(rx - sx), abs(ry - sy))
            if best is None or d < bestd or (d == bestd and (rx, ry) < best):
                best = (rx, ry)
                bestd = d
        dx = 0 if best[0] == sx else (1 if best[0] > sx else -1)
        dy = 0 if best[1] == sy else (1 if best[1] > sy else -1)
        return [dx, dy]
    # No resources: move to reduce distance to center while avoiding obstacles
    cx, cy = w // 2, h // 2
    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst
    best_move = (0, 0)
    bestv = -10**9
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        v = -(abs(nx - cx) + abs(ny - cy))
        # discourage moving toward opponent to avoid collision
        odist = max(abs(nx - ox), abs(ny - oy))
        v -= odist * 0.01
        if v > bestv or (v == bestv and (dx, dy) < best_move):
            bestv = v
            best_move = (dx, dy)
    return [best_move[0], best_move[1]]