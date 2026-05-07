def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    res = observation.get("resources", []) or []
    obs = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                obs.add((x, y))
        elif isinstance(p, dict):
            x, y = p.get("x"), p.get("y")
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    resources = []
    for p in res:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int):
                resources.append((x, y))
        elif isinstance(p, dict):
            x, y = p.get("x"), p.get("y")
            if isinstance(x, int) and isinstance(y, int):
                resources.append((x, y))

    def blocked(x, y):
        return (x, y) in obs or not (0 <= x < w and 0 <= y < h)

    def man(a, b, c, d):
        dx = a - c
        if dx < 0:
            dx = -dx
        dy = b - d
        if dy < 0:
            dy = -dy
        return dx + dy

    target = None
    best_d = 10**9
    for x, y in resources:
        if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
            d = man(sx, sy, x, y)
            if d < best_d:
                best_d = d
                target = (x, y)

    oppd = man(sx, sy, ox, oy)
    moves = [(1, 0), (-1, 0), (0, 1), (0, -1), (0, 0)]
    best_move = (0, 0)
    best_score = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if blocked(nx, ny):
            continue
        if target is not None:
            td = man(nx, ny, target[0], target[1])
            moved_opp = man(nx, ny, ox, oy)
            on_res = 1 if (nx, ny) == target else 0
            score = -td + 5 * on_res + 0.1 * moved_opp
        else:
            moved_opp = man(nx, ny, ox, oy)
            score = moved_opp
        if score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move