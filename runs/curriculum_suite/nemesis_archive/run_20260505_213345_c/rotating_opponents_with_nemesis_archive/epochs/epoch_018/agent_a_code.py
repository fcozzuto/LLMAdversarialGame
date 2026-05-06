def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = (observation.get("self_position", [0, 0]) or [0, 0])[:2]
    ox, oy = (observation.get("opponent_position", [0, 0]) or [0, 0])[:2]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

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

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def man(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]

    best_move = (0, 0)
    best_score = -10**18
    res_set = set(resources)
    opp_row = None
    for x, y in resources:
        if y == oy:
            opp_row = oy
            break

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        score = 0
        if (nx, ny) in res_set:
            score += 1000000
        if opp_row is not None and ny == opp_row:
            score += 2000
        d_self = min(man(nx, ny, rx, ry) for rx, ry in resources)
        d_opp = min(man(ox, oy, rx, ry) for rx, ry in resources)
        score += (d_opp - d_self) * 50
        score -= man(nx, ny, ox, oy) * 5
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    if ok(sx, sy):
        if best_move == (0, 0):
            return [0, 0]
    if ok(sx + best_move[0], sy + best_move[1]):
        return [best_move[0], best_move[1]]

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if ok(nx, ny):
            return [dx, dy]
    return [0, 0]