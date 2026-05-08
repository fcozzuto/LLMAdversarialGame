def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if inb(x, y): obs.add((x, y))
    if (sx, sy) in obs: return [0, 0]
    res = []
    for p in resources:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if inb(x, y) and (x, y) not in obs: res.append((x, y))
    if not res: return [0, 0]

    def md(a, b, c, d): return abs(a - c) + abs(b - d)
    # Predict opponent next position by moving toward its closest resource.
    best_r = None; best_d = 10**9
    for rx, ry in res:
        d = md(ox, oy, rx, ry)
        if d < best_d or (d == best_d and (rx, ry) < best_r):
            best_d = d; best_r = (rx, ry)
    tx, ty = best_r
    dxo = 0 if tx == ox else (1 if tx > ox else -1)
    dyo = 0 if ty == oy else (1 if ty > oy else -1)
    opnx, opny = ox + dxo, oy + dyo
    if not inb(opnx, opny) or (opnx, opny) in obs:
        opnx, opny = ox, oy

    # Interception: choose resource where we beat the opponent's predicted arrival earliest.
    target = None; best = (-10**9, 10**9)
    for rx, ry in res:
        d_me = md(sx, sy, rx, ry)
        d_op = md(opnx, opny, rx, ry)
        score = (d_op - d_me, -d_me)  # maximize: arrive earlier (bigger), tie by closer
        if score > best or (score == best and (rx, ry) < target):
            best = score; target = (rx, ry)
    tx, ty = target

    # Choose move that decreases distance to target most, avoiding obstacles; deterministic tie-break.
    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obs:
                dist = md(nx, ny, tx, ty)
                moves.append((dist, dx, dy))
    if not moves: return [0, 0]
    moves.sort(key=lambda t: (t[0], t[1], t[2]))
    return [moves[0][1], moves[0][2]]