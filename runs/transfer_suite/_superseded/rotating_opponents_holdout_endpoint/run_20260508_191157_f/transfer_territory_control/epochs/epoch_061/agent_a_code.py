def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    obs = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def pick_target(cells):
        best = None
        for p in cells:
            if p and len(p) >= 2:
                x, y = int(p[0]), int(p[1])
                if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                    d = (x - sx) * (x - sx) + (y - sy) * (y - sy)
                    if best is None or d < best[0] or (d == best[0] and (x, y) < best[1]):
                        best = (d, (x, y))
        return best[1] if best else None

    t = pick_target(observation.get("unclaimed_cells") or [])
    if t is None:
        t = pick_target(observation.get("resources") or [])
    if t is None:
        t = (w // 2, h // 2)

    tx, ty = t
    candidates = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs:
            dist = (nx - tx) * (nx - tx) + (ny - ty) * (ny - ty)
            candidates.append((dist, abs(dx) + abs(dy), nx, ny, dx, dy))

    if not candidates:
        return [0, 0]

    candidates.sort()
    return [int(candidates[0][4]), int(candidates[0][5])]