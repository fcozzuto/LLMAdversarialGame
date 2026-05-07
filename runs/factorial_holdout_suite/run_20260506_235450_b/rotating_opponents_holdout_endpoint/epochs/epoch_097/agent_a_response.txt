def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    ap = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(ap[0]), int(ap[1])

    blocked = set()
    for ob in (observation.get("obstacles") or []):
        if isinstance(ob, (list, tuple)) and len(ob) >= 2:
            x, y = int(ob[0]), int(ob[1])
        elif isinstance(ob, dict):
            if "x" in ob and "y" in ob:
                x, y = int(ob["x"]), int(ob["y"])
            else:
                p = ob.get("position")
                if not (isinstance(p, (list, tuple)) and len(p) >= 2):
                    continue
                x, y = int(p[0]), int(p[1])
        else:
            continue
        if 0 <= x < w and 0 <= y < h:
            blocked.add((x, y))

    resources = observation.get("resources") or []
    if not resources:
        return [0, 0]

    def d(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    best = None
    best_key = None
    for r in resources:
        if not (isinstance(r, (list, tuple)) and len(r) >= 2):
            if isinstance(r, dict) and "x" in r and "y" in r:
                x, y = int(r["x"]), int(r["y"])
            else:
                continue
        else:
            x, y = int(r[0]), int(r[1])
        if not (0 <= x < w and 0 <= y < h):
            continue
        sd = d(sx, sy, x, y)
        od = d(ox, oy, x, y)
        # Prefer resources we can reach earlier; otherwise maximize distance advantage.
        margin = od - sd
        win_pref = 0 if sd <= od else 1
        key = (win_pref, -margin, sd, x, y)
        if best_key is None or key < best_key:
            best_key, best = key, (x, y)

    tx, ty = best

    step_order = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, -1), (1, -1), (-1, 1)]
    dx_pref = 0 if tx == sx else (1 if tx > sx else -1)
    dy_pref = 0 if ty == sy else (1 if ty > sy else -1)

    target_steps = []
    if dx_pref != 0 or dy_pref != 0:
        target_steps.append((dx_pref, dy_pref))
        if dx_pref != 0:
            target_steps.append((dx_pref, 0))
        if dy_pref != 0:
            target_steps.append((0, dy_pref))
    target_steps += step_order

    for dx, dy in target_steps:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in blocked:
            return [int(dx), int(dy)]
    return [0, 0]