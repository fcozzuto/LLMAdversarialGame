def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    blocked = set()
    for p in (observation.get("obstacles") or []):
        try:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))
        except:
            pass

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1), (0, 0)]

    resources = []
    for r in (observation.get("resources") or []):
        try:
            resources.append((int(r[0]), int(r[1])))
        except:
            pass
    unclaimed = []
    for c in (observation.get("unclaimed_cells") or []):
        try:
            unclaimed.append((int(c[0]), int(c[1])))
        except:
            pass

    if resources:
        target = min(resources, key=lambda p: abs(p[0] - sx) + abs(p[1] - sy))
    elif unclaimed:
        target = min(unclaimed, key=lambda p: abs(p[0] - sx) + abs(p[1] - sy))
    else:
        target = (w // 2, h // 2)

    def score_move(nx, ny):
        # Prefer moving toward target; add small repulsion from opponent; avoid blocked already filtered
        to_t = abs(nx - target[0]) + abs(ny - target[1])
        from_o = abs(nx - ox) + abs(ny - oy)
        return (to_t, -from_o, abs(nx - sx) + abs(ny - sy))

    best = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in blocked:
            continue
        sc = score_move(nx, ny)
        if best is None or sc < best[0]:
            best = (sc, dx, dy)

    if best is None:
        return [0, 0]
    return [best[1], best[2]]