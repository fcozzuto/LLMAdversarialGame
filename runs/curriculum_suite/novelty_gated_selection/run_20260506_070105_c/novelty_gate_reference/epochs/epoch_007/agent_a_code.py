def choose_move(observation):
    w = observation.get("grid_width", 0)
    h = observation.get("grid_height", 0)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            blocked.add((p[0], p[1]))

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    if not resources:
        tx, ty = (w // 2, h // 2)
    else:
        best = None
        for rx, ry in resources:
            sd = man(sx, sy, rx, ry)
            od = man(ox, oy, rx, ry)
            score = (sd - od * 0.9, sd, -od, rx, ry)
            if best is None or score < best[0]:
                best = (score, rx, ry)
        tx, ty = best[1], best[2]

    best_move = None
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        self_d = man(nx, ny, tx, ty)
        opp_d = man(nx, ny, ox, oy)
        on_res = any((isinstance(p, (list, tuple)) and len(p) >= 2 and p[0] == nx and p[1] == ny) for p in resources)
        # Prefer moving onto a resource; otherwise reduce distance to target while increasing opponent distance
        key = (0 if on_res else 1, self_d, -opp_d, dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best_move = [dx, dy]

    if best_move is not None:
        return best_move

    # No valid moves found (edge case): stay put if valid, else clamp to nearest valid among 1-step options
    if valid(sx, sy):
        return [0, 0]
    for dx, dy in moves:
        if valid(sx + dx, sy + dy):
            return [dx, dy]
    return [0, 0]