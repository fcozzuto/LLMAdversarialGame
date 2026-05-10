def choose_move(observation):
    w = observation.get("grid_width", 0)
    h = observation.get("grid_height", 0)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))

    obstacles = observation.get("obstacles", [])
    obs = set((p[0], p[1]) for p in obstacles)

    un_list = observation.get("unclaimed_cells", None)
    if un_list is None:
        un_list = observation.get("unclaimed", [])
    un_set = set((p[0], p[1]) for p in un_list) if un_list else set()

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(a, b):
        ax, ay = a
        bx, by = b
        d1 = ax - bx
        if d1 < 0:
            d1 = -d1
        d2 = ay - by
        if d2 < 0:
            d2 = -d2
        return d1 if d1 >= d2 else d2

    target = None
    if un_set:
        best = None
        for t in un_set:
            d = cheb((sx, sy), t)
            if best is None or d < best[0]:
                best = (d, t)
        target = best[1]
    else:
        target = (ox, oy)

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1), (0, 0)]
    best_move = (0, 0)
    best_score = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        d = cheb((nx, ny), target)
        od = cheb((nx, ny), (ox, oy))
        # Prefer getting closer to target; small preference for farther from opponent when tying.
        score = d * 1000 + (-od)
        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]