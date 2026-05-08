def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [sx, sy])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obs = set()
    for o in observation.get("obstacles", []) or []:
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            x, y = int(o[0]), int(o[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def manh(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    best_move = (0, 0)
    best_val = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obs:
            nx, ny, dx, dy = sx, sy, 0, 0

        cur_best = -10**18
        for rx, ry in resources:
            sd = manh(nx, ny, rx, ry)
            od = manh(ox, oy, rx, ry)
            adv = od - sd  # positive means we are closer than opponent
            # prefer immediate advantage, then closer for ourselves
            val = adv * 1000 - sd
            if val > cur_best:
                cur_best = val
        # slight bias: if we tie, move that keeps us closer to our own best resource
        if cur_best > best_val:
            best_val = cur_best
            best_move = (dx, dy)
        elif cur_best == best_val:
            if manh(sx + dx, sy + dy, resources[0][0], resources[0][1]) < manh(sx + best_move[0], sy + best_move[1], resources[0][0], resources[0][1]):
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]