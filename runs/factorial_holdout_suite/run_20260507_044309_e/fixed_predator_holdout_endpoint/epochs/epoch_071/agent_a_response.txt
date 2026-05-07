def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            px, py = int(p[0]), int(p[1])
            if 0 <= px < w and 0 <= py < h:
                obstacles.add((px, py))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obstacles:
                resources.append((rx, ry))
    if not resources:
        return [0, 0]

    def md(a, b, c, d):
        return abs(a - c) + abs(b - d)

    self_closest = min(resources, key=lambda cell: md(sx, sy, cell[0], cell[1]))
    opp_closest = min(resources, key=lambda cell: md(ox, oy, cell[0], cell[1]))

    sd = md(sx, sy, self_closest[0], self_closest[1])
    od = md(ox, oy, opp_closest[0], opp_closest[1])

    # If opponent has a clear tempo advantage, deny by moving toward their nearest resource.
    target = opp_closest if od + 1 <= sd else self_closest

    tx, ty = target
    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    best_key = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue
        dist_to_target = md(nx, ny, tx, ty)
        # Prefer reaching target faster; also slightly prefer moves that avoid giving opponent an edge.
        opp_dist_after = md(nx, ny, ox + (1 if tx > ox else (-1 if tx < ox else 0)), oy + (1 if ty > oy else (-1 if ty < oy else 0)))
        key = (dist_to_target, opp_dist_after)
        if best_key is None or key < best_key:
            best_key = key
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]