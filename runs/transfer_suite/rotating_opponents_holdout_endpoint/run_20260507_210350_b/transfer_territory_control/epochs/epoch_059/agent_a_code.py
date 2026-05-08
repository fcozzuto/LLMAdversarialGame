def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

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
            if 0 <= x < w and 0 <= y < h:
                resources.append((x, y))

    rem = observation.get("remaining_resource_count", None)
    try:
        rem = int(rem) if rem is not None else len(resources)
    except:
        rem = len(resources)

    def get_cells(key):
        out = []
        for t in observation.get(key) or []:
            if t and len(t) >= 2:
                x, y = int(t[0]), int(t[1])
                if 0 <= x < w and 0 <= y < h:
                    out.append((x, y))
        return out

    unclaimed = get_cells("unclaimed_cells")
    opp_terr = get_cells("opponent_territory")

    target_list = resources if rem > 0 and resources else (unclaimed if unclaimed else opp_terr)
    tx, ty = (ox, oy) if not target_list else min(target_list, key=lambda p: (p[0]-sx)*(p[0]-sx) + (p[1]-sy)*(p[1]-sy))

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1), (0, 0)]
    best = None
    best_d = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        d = (nx - tx) * (nx - tx) + (ny - ty) * (ny - ty)
        if best_d is None or d < best_d:
            best_d = d
            best = (dx, dy)
    if best is None:
        return [0, 0]
    return [best[0], best[1]]