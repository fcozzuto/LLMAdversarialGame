def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            blocked.add((p[0], p[1]))

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    res_list = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            res_list.append((r[0], r[1]))

    if not res_list:
        tx, ty = w // 2, h // 2
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if valid(nx, ny):
                return [dx, dy] if (abs(nx - tx) + abs(ny - ty)) < (abs(sx - tx) + abs(sy - ty)) else [0, 0]
        return [0, 0]

    def move_value(nx, ny):
        on_res = 0
        if any(rx == nx and ry == ny for rx, ry in res_list):
            on_res = -20  # strong prefer pick-up
        best = None
        for rx, ry in res_list:
            sd = man(nx, ny, rx, ry)
            od = man(ox, oy, rx, ry)
            # Prefer resources where we are not behind; also deny if opponent is closer.
            rel = sd - od
            # Slight bias toward center to avoid drifting into corners/edges wastefully.
            center_bias = (abs(rx - (w - 1) / 2) + abs(ry - (h - 1) / 2)) * 0.03
            val = (sd + 0.25 * od + center_bias) + (0.75 * max(0, rel)) - (0.35 * max(0, -rel))
            if best is None or val < best:
                best = val
        return on_res + best

    best_move = (0, 0)
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        v = move_value(nx, ny)
        if best_val is None or v < best_val or (v == best_val and (dx, dy) < best_move):
            best_val = v
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]