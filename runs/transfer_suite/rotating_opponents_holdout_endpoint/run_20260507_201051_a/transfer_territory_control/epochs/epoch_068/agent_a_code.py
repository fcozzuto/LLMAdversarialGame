def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    unclaimed = []
    for p in observation.get("unclaimed_cells") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            unclaimed.append((int(p[0]), int(p[1])))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    dirs = [(1, 0), (0, 1), (-1, 0), (0, -1), (0, 0)]
    if unclaimed:
        tx, ty = min(unclaimed, key=lambda c: abs(c[0] - sx) + abs(c[1] - sy))
    else:
        tx, ty = ox, oy

    best = None
    best_score = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obstacles:
            continue
        d_t = abs(nx - tx) + abs(ny - ty)
        d_o = abs(nx - ox) + abs(ny - oy)
        score = (-2 * d_t) + (d_o)
        if best is None or score > best_score:
            best_score = score
            best = [dx, dy]

    return best if best is not None else [0, 0]