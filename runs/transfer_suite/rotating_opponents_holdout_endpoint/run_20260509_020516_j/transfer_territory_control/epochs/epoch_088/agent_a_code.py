def choose_move(observation):
    W = int(observation.get("grid_width", 8) or 8)
    H = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (W - 1, H - 1)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    blocked = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H:
                blocked.add((x, y))

    def inside(x, y):
        return 0 <= x < W and 0 <= y < H and (x, y) not in blocked

    def dist2(a, b):
        return (a[0] - b[0]) * (a[0] - b[0]) + (a[1] - b[1]) * (a[1] - b[1])

    resources = [tuple(p[:2]) for p in (observation.get("resources") or []) if p and len(p) >= 2]
    unclaimed = [tuple(p[:2]) for p in (observation.get("unclaimed_cells") or []) if p and len(p) >= 2]
    oppT = [tuple(p[:2]) for p in (observation.get("opponent_territory") or []) if p and len(p) >= 2]

    if resources:
        target = min(resources, key=lambda t: dist2((sx, sy), t))
    elif unclaimed:
        target = min(unclaimed, key=lambda t: dist2((sx, sy), t))
    else:
        # deterministic fallback: push toward opponent if no other guidance
        target = (ox, oy) if oppT == [] else min(oppT, key=lambda t: dist2((sx, sy), t))

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1), (0, 0)]
    best = None
    bestv = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        v = dist2((nx, ny), target)
        if bestv is None or v < bestv or (v == bestv and (dx, dy) < best):
            bestv = v
            best = (dx, dy)

    if best is not None:
        return [int(best[0]), int(best[1])]

    # if somehow no move is valid, stay put
    return [0, 0]