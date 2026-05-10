def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)

    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]) if len(sp) > 0 else 0, int(sp[1]) if len(sp) > 1 else 0
    ox, oy = int(op[0]) if len(op) > 0 else 0, int(op[1]) if len(op) > 1 else 0

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            try:
                obstacles.add((int(p[0]), int(p[1])))
            except:
                pass

    resources = []
    for p in observation.get("resources", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            try:
                resources.append((int(p[0]), int(p[1])))
            except:
                pass

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    best = None
    bestv = None

    def score(nx, ny):
        dres = 0
        if resources:
            dres = min(abs(nx - rx) + abs(ny - ry) for rx, ry in resources)
        else:
            dres = 999999
        dopp = abs(nx - ox) + abs(ny - oy)
        return (-(dres), dopp)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        v = score(nx, ny)
        if bestv is None or v > bestv or (v == bestv and (dx, dy) < best):
            bestv = v
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]