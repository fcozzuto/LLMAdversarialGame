def choose_move(observation):
    w = int(observation.get("grid_width", 0) or 0)
    h = int(observation.get("grid_height", 0) or 0)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def md(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    # Pick a resource we can reach earlier (tie-break toward shortest self distance).
    best_t = None
    best_key = None
    for tx, ty in resources:
        sd = md(sx, sy, tx, ty)
        od = md(ox, oy, tx, ty)
        key = (sd - od, sd, tx, ty)
        if best_key is None or key < best_key:
            best_key = key
            best_t = (tx, ty)

    tx, ty = best_t
    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    best_m = (0, 0)
    best_score = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        if (nx, ny) == (tx, ty):
            score = -1000000
        else:
            # Prefer reducing distance to target; small bias toward not letting opponent land on our target.
            score = md(nx, ny, tx, ty) * 10 + md(nx, ny, ox, oy) + (0 if md(ox, oy, tx, ty) >= md(nx, ny, tx, ty) else 3)
        if best_score is None or score < best_score:
            best_score = score
            best_m = (dx, dy)

    return [int(best_m[0]), int(best_m[1])]