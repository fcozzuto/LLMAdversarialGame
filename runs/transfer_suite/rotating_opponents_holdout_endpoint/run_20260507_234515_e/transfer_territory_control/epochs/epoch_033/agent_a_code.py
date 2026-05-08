def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    def to_set(key):
        s = set()
        for p in observation.get(key) or []:
            if p and len(p) >= 2:
                s.add((int(p[0]), int(p[1])))
        return s

    obstacles = to_set("obstacles")
    resources = to_set("resources")
    unclaimed = to_set("unclaimed_cells")
    oppT = to_set("opponent_territory")
    inside = lambda x, y: 0 <= x < w and 0 <= y < h

    if resources:
        tx, ty = min(resources, key=lambda p: (abs(p[0] - sx) + abs(p[1] - sy), p[0], p[1]))
    elif unclaimed:
        tx, ty = min(unclaimed, key=lambda p: (abs(p[0] - sx) + abs(p[1] - sy), p[0], p[1]))
    elif oppT:
        # go to an unclaimed/edge near opponent territory if possible
        best = None
        for ax, ay in oppT:
            for nx, ny in ((ax, ay - 1), (ax, ay + 1), (ax - 1, ay), (ax + 1, ay),
                           (ax - 1, ay - 1), (ax + 1, ay - 1), (ax - 1, ay + 1), (ax + 1, ay + 1)):
                if inside(nx, ny) and ((nx, ny) not in obstacles):
                    if best is None or (abs(nx - sx) + abs(ny - sy), nx, ny) < (best[0], best[1], best[2]):
                        best = (abs(nx - sx) + abs(ny - sy), nx, ny)
        if best:
            tx, ty = best[1], best[2]
        else:
            tx, ty = ox, oy
    else:
        tx, ty = ox, oy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_score = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obstacles:
            continue
        # prefer moving toward target; slightly prefer getting closer to opponent
        score = (abs(nx - tx) + abs(ny - ty), abs(nx - ox) + abs(ny - oy), dx, dy)
        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)
    dx, dy = best_move
    return [int(dx), int(dy)]