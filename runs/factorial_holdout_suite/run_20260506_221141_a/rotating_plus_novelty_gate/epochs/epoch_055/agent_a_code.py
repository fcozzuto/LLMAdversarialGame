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
    res_set = set()
    for p in observation.get("resources", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in blocked:
                if (x, y) not in res_set:
                    resources.append((x, y))
                    res_set.add((x, y))

    if not resources:
        return [0, 0]

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def kdist(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        return abs(dx) if abs(dx) > abs(dy) else abs(dy)

    # Pick a resource where we have the advantage in distance.
    best_res = resources[0]
    best_res_val = -10**18
    for rx, ry in resources:
        md = kdist(sx, sy, rx, ry)
        od = kdist(ox, oy, rx, ry)
        # Prefer winning races; then faster.
        val = (od - md) * 1000 - md
        if od == md:
            val += 200
        if (rx, ry) == (sx, sy):
            val += 10**7
        if val > best_res_val:
            best_res_val = val
            best_res = (rx, ry)

    rx, ry = best_res

    # Choose move maximizing advantage after move.
    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in blocked:
            nx, ny = sx, sy
        my_d = kdist(nx, ny, rx, ry)
        op_d = kdist(ox, oy, rx, ry)
        # Encourage moves that reduce our distance more than opponent's.
        val = (op_d - my_d) * 1200 - my_d
        if (nx, ny) == (sx, sy):
            val -= 1  # discourage dithering
        if val > best_val:
            best_val = val
            best_move = (nx - sx, ny - sy)

    return [int(best_move[0]), int(best_move[1])]