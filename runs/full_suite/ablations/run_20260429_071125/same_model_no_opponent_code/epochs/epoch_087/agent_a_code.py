def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    if not valid(sx, sy):
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if valid(nx, ny):
                return [dx, dy]
        return [0, 0]

    # Pick target: nearest resource if any, else opponent position
    if resources:
        target = min(resources, key=lambda r: abs(r[0] - sx) + abs(r[1] - sy))
        tx, ty = target
        # score candidate by closeness to target; tie-break by closeness to opponent
        def cand_score(nx, ny):
            return (abs(tx - nx) + abs(ty - ny)) * 10 + (abs(ox - nx) + abs(oy - ny))
    else:
        tx, ty = ox, oy
        def cand_score(nx, ny):
            # try to reduce distance to opponent
            return (abs(tx - nx) + abs(ty - ny))

    best = None
    best_move = (0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if valid(nx, ny):
            sc = cand_score(nx, ny)
            if best is None or sc < best or (sc == best and (dx, dy) < best_move):
                best = sc
                best_move = (dx, dy)

    dx, dy = best_move
    return [int(dx), int(dy)]