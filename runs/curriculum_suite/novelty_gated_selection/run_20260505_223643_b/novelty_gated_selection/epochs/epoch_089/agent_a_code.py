def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    def best_resource_for(posx, posy):
        # Choose resource that is best for us from this position (tie-breaker: farther from opponent)
        best = None
        for rx, ry in resources:
            sd = man(posx, posy, rx, ry)
            od = man(ox, oy, rx, ry)
            score = (sd, -od, (rx == posx and ry == posy), rx, ry)
            if best is None or score < best:
                best = score
                best_cell = (rx, ry)
        return best_cell

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    best_move = (10**9, 10**9, 10**9, 0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        tx, ty = best_resource_for(nx, ny)
        sd = man(nx, ny, tx, ty)
        od = man(ox, oy, tx, ty)
        # Aggressive: prefer closer + make opponent relatively farther; also avoid being too close to opponent overall
        opp_self = man(nx, ny, ox, oy)
        # Deterministic tie-breaks by coordinates and move ordering
        cand = (sd - od, sd, -opp_self, dx, dy)
        if cand < best_move:
            best_move = cand

    # If all moves blocked, stay.
    if best_move[3] == 0 and best_move[4] == 0:
        return [0, 0]
    return [int(best_move[3]), int(best_move[4])]