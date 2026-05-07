def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]
    if (sx, sy) in resources:
        return [0, 0]

    def md(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    my = (sx, sy)
    opp = (ox, oy)

    better = []
    fallback = []
    for t in resources:
        dm = md(my, t)
        do = md(opp, t)
        # Prefer resources we can arrive strictly earlier (denier-focused).
        if dm < do:
            better.append((dm, do, t))
        else:
            # If none are strictly winnable, go where opponent is farthest relative to us.
            fallback.append((-(do - dm), dm, t))

    if better:
        better.sort(key=lambda x: (x[0], x[1], x[2][0], x[2][1]))
        target = better[0][2]
    else:
        fallback.sort()
        target = fallback[0][2]

    tx, ty = target
    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)

    nx, ny = sx + dx, sy + dy
    if (nx, ny) in obstacles or not (0 <= nx < w and 0 <= ny < h):
        # Try axis-aligned alternative toward the target.
        if dx != 0 and (sx + dx, sy) not in obstacles and 0 <= sx + dx < w:
            return [dx, 0]
        if dy != 0 and (sx, sy + dy) not in obstacles and 0 <= sy + dy < h:
            return [0, dy]
        return [0, 0]
    return [dx, dy]