def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        try:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))
        except:
            pass

    resources = []
    for r in observation.get("resources") or []:
        try:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
        except:
            pass

    if not resources:
        return [0, 0]

    def md(a, b, c, d):
        return abs(a - c) + abs(b - d)

    def clamp(x, lo, hi):
        return lo if x < lo else (hi if x > hi else x)

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    # Choose a target that we can contest: prefer resources where we are not worse; tie-break by closest advantage.
    scored_targets = []
    for rx, ry in resources:
        sd = md(sx, sy, rx, ry)
        od = md(ox, oy, rx, ry)
        rel = od - sd
        scored_targets.append((rel, sd + od, rx, ry))
    scored_targets.sort(reverse=True)
    target = (scored_targets[0][2], scored_targets[0][3])

    tx, ty = target
    best_move = (0, 0)
    best_val = -10**18

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        nx, ny = clamp(nx, 0, w - 1), clamp(ny, 0, h - 1)
        if (nx, ny) in obstacles:
            continue
        sd_new = md(nx, ny, tx, ty)
        od = md(ox, oy, tx, ty)
        rel_new = od - sd_new
        # Mildly prefer moves that reduce own distance when contesting is tight; and avoid edging away.
        val = rel_new * 100 - sd_new
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]