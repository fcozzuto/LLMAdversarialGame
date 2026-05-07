def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def md(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    # Prefer resources where we are at least as fast as opponent; tie-break by shorter self distance.
    best = None
    for rx, ry in resources:
        sd = md(sx, sy, rx, ry)
        od = md(ox, oy, rx, ry)
        # Higher is better for us: (od - sd) positive means we can arrive first.
        key = (-(od - sd), sd, od, rx, ry)  # minimize tuple: i.e., maximize (od-sd)
        if best is None or key < best[0]:
            best = (key, rx, ry)
    _, tx, ty = best

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_m = None
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        nsd = md(nx, ny, tx, ty)
        nod = md(nx, ny, ox, oy)  # discourage stepping into opponent proximity
        # Also bias toward collecting: if resource at next cell, strongly prefer.
        on_res = 1 if (nx, ny) in resources else 0
        key = (0 if on_res else 1, nsd, -nod, abs((nx - tx) - (sx - tx)) + abs((ny - ty) - (sy - ty)), dx, dy)
        if best_key is None or key < best_key:
            best_key, best_m = key, (dx, dy)

    if best_m is None:
        return [0, 0]
    return [int(best_m[0]), int(best_m[1])]