def choose_move(observation):
    x, y = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)

    def sign(a):
        return 0 if a == 0 else (1 if a > 0 else -1)

    def in_bounds(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = x + dx, y + dy
            if in_bounds(nx, ny) and (nx, ny) not in obstacles:
                moves.append((dx, dy))

    if not resources:
        dx = sign(ox - x)
        dy = sign(oy - y)
        # step away from opponent if possible
        best = (0, 0)
        bestv = -10**9
        for dxm, dym in moves:
            nx, ny = x + dxm, y + dym
            v = -(abs(nx - ox) + abs(ny - oy))
            if v > bestv:
                bestv = v
                best = (dxm, dym)
        return [best[0], best[1]]

    t = observation.get("turn_index", 0)
    best_res = None
    best_val = -10**18
    for rx, ry in resources:
        ds = abs(rx - x) + abs(ry - y)
        do = abs(rx - ox) + abs(ry - oy)
        if (rx, ry) == (x, y):
            best_res = (rx, ry)
            break
        val = (do - ds) * 2 - ds
        # deterministic tie-break with turn parity
        val += 0.01 * ((rx + ry + t) % 10)
        if val > best_val:
            best_val = val
            best_res = (rx, ry)

    tx, ty = best_res
    md = abs(tx - x) + abs(ty - y)
    desired = (sign(tx - x), sign(ty - y))

    candidates = []
    for dxm, dym in moves:
        nx, ny = x + dxm, y + dym
        d = abs(tx - nx) + abs(ty - ny)
        # prefer reducing distance; slight bias toward desired direction; avoid moving closer to opponent too much
        v = (md - d) * 10
        if (dxm, dym) == desired:
            v += 3
        v -= 0.2 * (abs(nx - ox) + abs(ny - oy))
        if (nx, ny) == (tx, ty):
            v += 50
        candidates.append((v, dxm, dym))

    candidates.sort(key=lambda z: (-z[0], z[1], z[2]))
    return [int(candidates[0][1]), int(candidates[0][2])]