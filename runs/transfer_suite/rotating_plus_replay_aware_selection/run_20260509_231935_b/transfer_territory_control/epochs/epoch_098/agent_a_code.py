def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obs.add((int(p[0]), int(p[1])))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def legal(nx, ny):
        return inside(nx, ny) and (nx, ny) not in obs

    resources = observation.get("resources") or []
    unclaimed = observation.get("unclaimed_cells") or []
    targets = unclaimed if unclaimed else [p for p in resources if isinstance(p, (list, tuple)) and len(p) == 2]

    tx, ty = None, None
    best = 10**9
    for p in targets:
        x, y = int(p[0]), int(p[1])
        if (x, y) == (sx, sy) or (x, y) in obs or not inside(x, y):
            continue
        d = abs(x - sx) + abs(y - sy)
        if d < best:
            best, tx, ty = d, x, y

    if tx is None:
        tx, ty = w // 2, h // 2

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_d = 10**18
    best_move = (0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        d = abs(tx - nx) + abs(ty - ny)
        adv = d + (abs(ox - nx) + abs(oy - ny)) // 5
        if adv < best_d:
            best_d = adv
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]