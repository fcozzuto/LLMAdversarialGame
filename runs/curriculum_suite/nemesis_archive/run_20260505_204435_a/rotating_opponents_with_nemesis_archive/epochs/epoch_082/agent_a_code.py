def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))

    sx, sy = int(sx), int(sy)
    ox, oy = int(ox), int(oy)

    obstacles = observation.get("obstacles", []) or []
    blocked = set()
    for p in obstacles:
        if isinstance(p, dict):
            q = p.get("position")
        else:
            q = p
        if isinstance(q, (list, tuple)) and len(q) >= 2:
            x, y = int(q[0]), int(q[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    resources = observation.get("resources", []) or []
    rpos = []
    for r in resources:
        if isinstance(r, dict):
            q = r.get("position")
        else:
            q = r
        if isinstance(q, (list, tuple)) and len(q) >= 2:
            x, y = int(q[0]), int(q[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in blocked:
                rpos.append((x, y))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    if not rpos:
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in blocked:
                return [dx, dy]
        return [0, 0]

    best = None
    best_move = [0, 0]
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in blocked:
            continue
        dres = min(abs(nx - rx) + abs(ny - ry) for rx, ry in rpos)
        dout = abs(nx - ox) + abs(ny - oy)
        score = (-dres, -dout, dx, dy)
        if best is None or score > best:
            best = score
            best_move = [dx, dy]
    return best_move