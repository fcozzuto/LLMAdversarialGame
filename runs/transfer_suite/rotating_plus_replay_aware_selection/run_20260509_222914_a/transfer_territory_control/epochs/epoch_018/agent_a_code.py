def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    try:
        w = int(w)
        h = int(h)
    except:
        w, h = 8, 8

    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    try:
        sx, sy = int(sx), int(sy)
        ox, oy = int(ox), int(oy)
    except:
        sx, sy, ox, oy = 0, 0, w - 1, h - 1

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and inside(x, y):
                obstacles.add((x, y))

    self_terr = set(tuple(p) for p in observation.get("self_territory") or [])
    opp_terr = set(tuple(p) for p in observation.get("opponent_territory") or [])
    unclaimed = set(tuple(p) for p in observation.get("unclaimed_cells") or [])

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1), (0, 0)]
    best = None
    best_val = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obstacles:
            continue
        if (nx, ny) in self_terr and (dx, dy) != (0, 0):
            continue
        d_op = abs(nx - ox) + abs(ny - oy)
        val = 0
        if (nx, ny) in unclaimed:
            val += 6
        elif (nx, ny) in opp_terr:
            val += 3
        if (nx, ny) in self_terr:
            val -= 1
        val += (20 - d_op)
        if val > best_val:
            best_val = val
            best = [dx, dy]
    if best is None:
        return [0, 0]
    return best