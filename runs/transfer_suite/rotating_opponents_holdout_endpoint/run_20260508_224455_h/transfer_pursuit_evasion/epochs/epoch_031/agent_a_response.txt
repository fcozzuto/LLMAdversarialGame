def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obs = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    role = (observation.get("self_role") or "").lower()
    is_evader = ("evader" in role) or ("evade" in role) or ("runner" in role) or ("escape" in role)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs

    def manhattan(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def mobility(x, y):
        c = 0
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if valid(nx, ny):
                c += 1
        return c

    best = (0, 0)
    best_score = -10**18 if is_evader else 10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d = manhattan(nx, ny, ox, oy)
        mob = mobility(nx, ny)
        # Primary: distance (evader wants maximize, pursuer wants minimize)
        # Secondary: mobility, helps avoid dead-ends / obstacle traps
        # Tertiary: prefer moving toward/away in a consistent lexicographic way by iteration order
        score = d * (1 if is_evader else -1) + mob * (1 if is_evader else -0.5)
        if is_evader:
            if score > best_score:
                best_score = score
                best = (dx, dy)
        else:
            if score < best_score:
                best_score = score
                best = (dx, dy)

    dx, dy = best
    return [int(dx), int(dy)]