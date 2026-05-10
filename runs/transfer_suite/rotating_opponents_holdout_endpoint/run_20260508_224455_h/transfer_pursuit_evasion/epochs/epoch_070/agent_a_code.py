def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obs = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, dict):
            x, y = p.get("x", -1), p.get("y", -1)
        else:
            x, y = (p[0] if len(p) > 0 else -1), (p[1] if len(p) > 1 else -1)
        try:
            x, y = int(x), int(y)
        except:
            continue
        if 0 <= x < w and 0 <= y < h:
            obs.add((x, y))

    role = str(observation.get("self_role") or observation.get("role") or "")
    is_evader = ("evad" in role.lower()) or ("escape" in role.lower())

    resources = observation.get("resources") or []
    res_pos = []
    for r in resources:
        if isinstance(r, dict):
            x, y = r.get("x", -1), r.get("y", -1)
        else:
            x, y = (r[0] if len(r) > 0 else -1), (r[1] if len(r) > 1 else -1)
        try:
            x, y = int(x), int(y)
        except:
            continue
        if 0 <= x < w and 0 <= y < h:
            res_pos.append((x, y))

    moves = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1), (0, 0)]
    best = None
    best_val = None

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obs:
            continue
        dist_op = man(nx, ny, ox, oy)

        if res_pos:
            dres = min(man(nx, ny, rx, ry) for rx, ry in res_pos)
            val = (-dres if not is_evader else -0.5 * dres) + (dist_op if is_evader else -dist_op)
        else:
            val = (dist_op if is_evader else -dist_op)

        corner_bias = (nx == 0) + (nx == w - 1) + (ny == 0) + (ny == h - 1)
        val += (corner_bias if is_evader else -corner_bias) * 0.01

        if best is None or (val > best_val) or (val == best_val and (dx, dy) < best):
            best, best_val = (dx, dy), val

    if best is None:
        return [0, 0]
    return [best[0], best[1]]