def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for o in obstacles:
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            ax, ay = int(o[0]), int(o[1])
            if 0 <= ax < w and 0 <= ay < h:
                obs.add((ax, ay))

    resources = observation.get("resources", []) or []
    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obs:
                res.append((rx, ry))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def md(a, b, c, d):
        return abs(a - c) + abs(b - d)

    best_move = [0, 0]
    best_val = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        if res:
            my_best = -10**18
            for rx, ry in res:
                my_d = md(nx, ny, rx, ry)
                op_d = md(ox, oy, rx, ry)
                my_best = max(my_best, op_d - my_d)
            # Prefer also closer-than-opponent resources; small tie-break to reduce my distance
            tie = -min(md(nx, ny, rx, ry) for rx, ry in res)
            val = my_best * 1000 + tie
        else:
            # No resources: maximize distance from opponent
            val = md(nx, ny, ox, oy)

        if val > best_val:
            best_val = val
            best_move = [dx, dy]

    return best_move