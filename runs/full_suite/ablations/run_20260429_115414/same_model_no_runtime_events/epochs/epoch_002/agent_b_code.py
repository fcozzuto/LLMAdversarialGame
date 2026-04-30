def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in observation.get("obstacles", []) or [])
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def man(a, b): return abs(a[0] - b[0]) + abs(a[1] - b[1])
    def step(v): return 1 if v > 0 else -1 if v < 0 else 0
    if not resources:
        return [0, 0]

    best = None
    best_key = None
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        sd = abs(rx - sx) + abs(ry - sy)
        od = abs(rx - ox) + abs(ry - oy)
        # Prefer resources we're strictly closer to; otherwise prefer smallest gap while still decent.
        gap = od - sd
        # Parity/weight to create a materially different deterministic tie-break.
        parity = ((rx + ry) - (sx + sy)) & 1
        key = (gap, -sd, -parity, -((rx * 17 + ry * 31) % 997))
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best
    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    desired_dx, desired_dy = step(tx - sx), step(ty - sy)

    best_move = (0, 0)
    best_val = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        ourd = abs(tx - nx) + abs(ty - ny)
        oppd = abs(tx - ox) + abs(ty - oy)
        # Encourage approaching target, discourage giving opponent better access, also separate from opponent.
        opp_agent_d = abs(ox - nx) + abs(oy - ny)
        align = -((desired_dx - dx) * (desired_dx - dx) + (desired_dy - dy) * (desired_dy - dy))
        val = (-(ourd), (oppd - ourd), opp_agent_d, align, -((nx * 13 + ny * 19) % 997))
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]