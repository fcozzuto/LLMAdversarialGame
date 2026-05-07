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

    def md(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    scored = []
    for rx, ry in resources:
        sd = md(sx, sy, rx, ry)
        od = md(ox, oy, rx, ry)
        advantage = od - sd
        if od < sd:
            # Opponent closer: strongly prefer resources they can't take first.
            val = (advantage, -sd, -od, - (rx + 31 * ry))
        else:
            # Prefer us taking first, then nearer.
            val = (advantage + 1000, -sd, -od, - (rx + 31 * ry))
        scored.append((val, (rx, ry)))
    scored.sort(reverse=True)
    (val, tx_ty) = scored[0]
    tx, ty = tx_ty

    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)

    nx, ny = sx + dx, sy + dy
    if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
        # Try alternate axis step deterministically
        candidates = []
        if 0 <= sx + dx < w and (sx + dx, sy) not in obstacles:
            candidates.append(((sx + dx) - sx, 0))
        if 0 <= sy + dy < h and (sx, sy + dy) not in obstacles:
            candidates.append((0, (sy + dy) - sy))
        if not candidates:
            return [0, 0]
        return [int(candidates[0][0]), int(candidates[0][1])]

    return [int(dx), int(dy)]