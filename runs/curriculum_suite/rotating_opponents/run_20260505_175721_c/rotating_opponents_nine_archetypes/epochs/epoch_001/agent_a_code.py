def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    resources = observation.get("resources", [])

    def dist(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    if resources:
        tx, ty = min(resources, key=lambda r: (dist(sx, sy, r[0], r[1]), r[1], r[0]))
    else:
        tx, ty = w // 2, h // 2

    best = None
    best_val = None
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if nx < 0 or nx >= w or ny < 0 or ny >= h:
                continue
            if (nx, ny) in obstacles:
                continue
            if (nx, ny) == (ox, oy):
                coll = 1
            else:
                coll = 0
            v = dist(nx, ny, tx, ty)
            o = dist(nx, ny, ox, oy)
            score = (v + 2 * coll, -o, dx, dy)
            if best_val is None or score < best_val:
                best_val = score
                best = (dx, dy)

    if best is None:
        return [0, 0]
    return [best[0], best[1]]