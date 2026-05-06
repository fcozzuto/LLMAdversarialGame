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

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    # Decide whether we have a guaranteed edge on any resource.
    viable = []
    for tx, ty in resources:
        sd = man(sx, sy, tx, ty)
        od = man(ox, oy, tx, ty)
        if sd < od:
            viable.append(((sd - od), tx, ty))  # more negative => bigger edge
    has_edge = len(viable) > 0

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        # Evaluate best target under this move; different objective depending on edge status.
        best_move_val = None
        for tx, ty in resources:
            sd = man(nx, ny, tx, ty)
            od = man(ox, oy, tx, ty)
            if has_edge:
                # Push for resources we're closer to than opponent; reward winning margin, penalize distance.
                val = (od - sd) * 120 - sd * 3
            else:
                # No edge: deny by pushing toward resources where opponent advantage shrinks most; penalize self distance.
                val = (sd - od) * -110 - sd * 2  # larger when sd is closer than od, even if still behind
            if best_move_val is None or val > best_move_val:
                best_move_val = val

        # Small tie-break: prefer moving that reduces distance to nearest resource.
        nearest = min(man(nx, ny, rx, ry) for rx, ry in resources)
        key = (best_move_val, -nearest if has_edge else -nearest, -abs(nx - sx) - abs(ny - sy))
        if best is None or key > best[0]:
            best = (key, dx, dy)

    return [best[1], best[2]] if best else [0, 0]