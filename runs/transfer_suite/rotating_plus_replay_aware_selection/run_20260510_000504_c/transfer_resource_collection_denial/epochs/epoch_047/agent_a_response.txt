def choose_move(observation):
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))
        elif isinstance(p, dict):
            pos = p.get("position")
            if isinstance(pos, (list, tuple)) and len(pos) >= 2:
                obstacles.add((int(pos[0]), int(pos[1])))
            elif "x" in p and "y" in p:
                obstacles.add((int(p["x"]), int(p["y"])))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            resources.append((int(r[0]), int(r[1])))
        elif isinstance(r, dict):
            pos = r.get("position")
            if isinstance(pos, (list, tuple)) and len(pos) >= 2:
                resources.append((int(pos[0]), int(pos[1])))
            elif "x" in r and "y" in r:
                resources.append((int(r["x"]), int(r["y"])))

    if not resources:
        return [0, 0]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def step_toward(tx, ty):
        best = None
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not inside(nx, ny) or (nx, ny) in obstacles:
                continue
            md = max(abs(tx - nx), abs(ty - ny))
            if best is None or md < best[0] or (md == best[0] and (dx, dy) < best[1]):
                best = (md, (dx, dy))
        return [best[1][0], best[1][1]] if best else [0, 0]

    # Score resources by my progress advantage over opponent; tie-break deterministically.
    best_t = None
    for tx, ty in resources:
        if (tx, ty) in obstacles:
            continue
        my_d = max(abs(tx - sx), abs(ty - sy))
        op_d = max(abs(tx - ox), abs(ty - oy))
        # smaller is better; strong preference for resources opponent can't reach as fast
        # add tiny bias toward closer resources when contested
        val = (my_d - op_d * 0.9, my_d + 0.001 * (abs(tx - w // 2) + abs(ty - h // 2)), tx, ty)
        if best_t is None or val < best_t[0]:
            best_t = (val, tx, ty)

    _, tx, ty = best_t
    move = step_toward(tx, ty)
    if move == [0, 0]:
        # If stuck by obstacles, go to a neighboring cell that maximizes distance from opponent while staying valid.
        best = None
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not inside(nx, ny) or (nx, ny) in obstacles:
                continue
            score = (max(abs(nx - ox), abs(ny - oy)), -max(abs(tx - nx), abs(ty - ny)), dx, dy)
            if best is None or score > best[0]:
                best = (score, (dx, dy))
        return [best[1][0], best[1][1]] if best else [0, 0]

    return move