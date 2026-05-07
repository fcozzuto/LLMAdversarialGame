def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def manh(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    if not resources:
        return [0, 0]

    best = None
    best_key = None
    for p in resources:
        tx, ty = int(p[0]), int(p[1])
        if not (0 <= tx < w and 0 <= ty < h):
            continue
        if (tx, ty) in obs:
            continue
        ds = manh(sx, sy, tx, ty)
        do = manh(ox, oy, tx, ty)
        # Strongly prefer resources where we arrive earlier; otherwise best "race"
        key = ((do - ds), -(ds), -((tx + ty) & 1), -tx, -ty)
        if best_key is None or key > best_key:
            best_key = key
            best = (tx, ty)

    if best is None:
        return [0, 0]
    tx, ty = best

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    bestm = None
    bestm_key = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obs:
            continue
        nd = manh(nx, ny, tx, ty)
        # Prefer moves that reduce distance to target; break ties toward center-ish and x-y ordering deterministically
        key = (-(nd), -((nx + ny) & 1), -nx, -ny, -dx, -dy)
        if bestm_key is None or key > bestm_key:
            bestm_key = key
            bestm = (dx, dy)

    if bestm is None:
        return [0, 0]
    return [int(bestm[0]), int(bestm[1])]