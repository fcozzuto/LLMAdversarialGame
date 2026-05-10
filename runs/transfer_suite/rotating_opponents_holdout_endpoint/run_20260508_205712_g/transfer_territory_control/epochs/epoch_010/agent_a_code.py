def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0)) or (0, 0)
    ox, oy = observation.get("opponent_position", (0, 0)) or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def pts_from(key):
        out = []
        for p in observation.get(key, []) or []:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                x, y = int(p[0]), int(p[1])
                if 0 <= x < w and 0 <= y < h:
                    out.append((x, y))
        return out

    unclaimed = pts_from("unclaimed_cells")
    resources = pts_from("resources")

    dirs = [(-1, 0), (0, -1), (1, 0), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1), (0, 0)]
    order = dirs

    def manh(x, y, tx, ty):
        dx = x - tx
        if dx < 0: dx = -dx
        dy = y - ty
        if dy < 0: dy = -dy
        return dx + dy

    def best_target(points):
        bt = None
        bd = 10**9
        for x, y in points[:200]:
            if (x, y) in obstacles:
                continue
            d = manh(sx, sy, x, y)
            if d < bd:
                bd = d
                bt = (x, y)
        return bt

    target = best_target(unclaimed)
    if target is None:
        target = best_target(resources)

    if target is None:
        target = (ox, oy)

    tx, ty = int(target[0]), int(target[1])

    best_move = (0, 0)
    best_score = 10**18
    for dx, dy in order:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        score = manh(nx, ny, tx, ty)
        if score < best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]