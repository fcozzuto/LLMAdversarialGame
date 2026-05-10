def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [sx, sy]) or [sx, sy]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    unclaimed = []
    for p in observation.get("unclaimed_cells") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                unclaimed.append((x, y))

    if unclaimed:
        tx, ty = min(unclaimed, key=lambda q: (q[0] - sx) ** 2 + (q[1] - sy) ** 2)[0:2]
    elif in_bounds(ox, oy):
        tx, ty = ox, oy
    else:
        tx, ty = (w - 1) // 2, (h - 1) // 2

    def sign(a):
        return 1 if a > 0 else (-1 if a < 0 else 0)

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    bestd = 10 ** 18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny):
            continue
        d = (tx - nx) ** 2 + (ty - ny) ** 2
        if d < bestd:
            bestd = d
            best = (dx, dy)
    if best is None:
        for dx, dy in [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)]:
            if in_bounds(sx + dx, sy + dy):
                return [int(dx), int(dy)]
        return [0, 0]
    return [int(best[0]), int(best[1]]]