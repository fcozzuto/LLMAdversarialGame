def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (w - 1, h - 1)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def step_options():
        return [(0, 0), (-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    best_move = [0, 0]
    if resources:
        tx, ty = min(resources, key=lambda r: man(sx, sy, r[0], r[1]))
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        pref = {(dx, dy)}
        tried = set()
        for m in step_options():
            if m in pref:
                tried.add(m)
        # ensure we don't get stuck if pref invalid; we'll evaluate all moves deterministically anyway
        best_score = -10**18
        for mx, my in step_options():
            if (mx, my) in tried:
                pass
            nx, ny = sx + mx, sy + my
            if not valid(nx, ny):
                continue
            score = -man(nx, ny, tx, ty)
            if (nx, ny) == (tx, ty):
                score += 100000
            ox_dist = man(nx, ny, ox, oy)
            score += ox_dist * 0.01
            if score > best_score:
                best_score = score
                best_move = [mx, my]
        return best_move

    # No resources: move away from opponent if possible, else stay
    best_score = -10**18
    for mx, my in step_options():
        nx, ny = sx + mx, sy + my
        if not valid(nx, ny):
            continue
        score = man(nx, ny, ox, oy)
        if score > best_score:
            best_score = score
            best_move = [mx, my]
    return best_move