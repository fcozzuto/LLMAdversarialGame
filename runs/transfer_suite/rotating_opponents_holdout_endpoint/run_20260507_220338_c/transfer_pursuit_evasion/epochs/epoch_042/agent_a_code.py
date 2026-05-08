def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            blocked.add((int(p[0]), int(p[1])))

    role_s = str(observation.get("self_role", "") or "").lower()
    is_pursuer = ("purs" in role_s) or ("chase" in role_s) or ("hunter" in role_s)
    is_evader = ("evad" in role_s) or ("run" in role_s) or ("away" in role_s) or ("escape" in role_s) or ("runner" in role_s)
    if not (is_pursuer or is_evader):
        is_pursuer = True

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    def bfs_dist(start, goal, maxd=7):
        if start == goal:
            return 0
        q = [(start[0], start[1], 0)]
        seen = {(start[0], start[1])}
        head = 0
        while head < len(q):
            x, y, d = q[head]
            head += 1
            if d >= maxd:
                continue
            nd = d + 1
            for dx, dy in deltas:
                nx, ny = x + dx, y + dy
                if inb(nx, ny) and (nx, ny) not in seen:
                    if (nx, ny) == goal:
                        return nd
                    seen.add((nx, ny))
                    q.append((nx, ny, nd))
        return None

    best = None
    best_move = [0, 0]
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            nx, ny = sx, sy
        d_opp = bfs_dist((nx, ny), (ox, oy), maxd=7)
        if d_opp is None:
            d_opp = 99
        step_center = (abs(nx - (w - 1) / 2.0) + abs(ny - (h - 1) / 2.0))
        # Evader tries to go away; pursuer tries to go close.
        if is_pursuer:
            val = (-d_opp * 10) + (-step_center)
        else:
            # Prefer moves that also keep distance from walls: wall-runner evasion.
            wall_pen = (min(nx, w - 1 - nx) + min(ny, h - 1 - ny))
            val = (d_opp * 10) + (wall_pen) - (step_center * 0.5)

        # Deterministic tie-break: smaller lexicographic [dx,dy] wins.
        if best is None or val > best or (val == best and (dx, dy) < (best_move[0], best_move[1])):
            best = val
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]