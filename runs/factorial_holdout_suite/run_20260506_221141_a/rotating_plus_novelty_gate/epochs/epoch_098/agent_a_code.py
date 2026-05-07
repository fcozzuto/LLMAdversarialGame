def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    blocked = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in blocked:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def kdist(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # Consider only the closest few resources to keep deterministic and fast
    resources.sort(key=lambda r: (kdist(sx, sy, r[0], r[1]), r[0], r[1]))
    resources = resources[:5]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_val = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0: nx = 0
        if nx >= w: nx = w - 1
        if ny < 0: ny = 0
        if ny >= h: ny = h - 1
        if (nx, ny) in blocked:
            nx, ny = sx, sy  # engine would keep in place

        val = 0
        # Primary: maximize advantage (opponent slower vs us); also prefer shorter our distance
        for rx, ry in resources:
            sd = kdist(nx, ny, rx, ry)
            od = kdist(ox, oy, rx, ry)
            if sd == 0:
                val += 1000000  # immediate pickup
            # Encourage winning race; discourage giving opponent a faster win
            val += (od - sd) * 1000 - sd
        # Deterministic tie-break by value then move lexicographic
        if val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]