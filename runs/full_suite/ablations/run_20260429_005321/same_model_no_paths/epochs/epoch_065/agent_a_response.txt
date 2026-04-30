def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [0, 0])
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

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

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    def near_obst_score(x, y):
        c = 0
        for dx in (-1, 0, 1):
            nx = x + dx
            if nx < 0 or nx >= w:
                continue
            for dy in (-1, 0, 1):
                ny = y + dy
                if (nx, ny) in obstacles:
                    c += 1
        return c

    # Pick a target that we can reach earlier, also prefer making opponent later.
    best_r = None
    best_v = -10**9
    for rx, ry in resources:
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        v = (od - sd) * 3 - sd - near_obst_score(rx, ry)
        # small deterministic tiebreak: nearer to center
        cx, cy = w / 2.0 - 0.5, h / 2.0 - 0.5
        v -= (abs(rx - cx) + abs(ry - cy)) * 0.01
        if v > best_v:
            best_v = v
            best_r = (rx, ry)
    rx, ry = best_r

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    # Greedy one-step: maximize (opp being delayed) while reducing own distance.
    best_m = (0, 0)
    best_s = -10**9
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        nsd = cheb(nx, ny, rx, ry)
        nod = cheb(ox, oy, rx, ry)
        # If we step onto a resource, prioritize strongly.
        take = 1 if (nx, ny) == (rx, ry) else 0
        # Slightly avoid tight obstacle adjacency at the move location.
        ms = take * 1000 - nsd * 5 + (nod - nod) * 0 - near_obst_score(nx, ny) * 0.1
        # Extra: if we can get closer while also increasing opponent distance to chosen target by stepping into line toward it,
        # approximate by rewarding moves that reduce our cheb more than opponent's (static opponent).
        if best_m == (0, 0):
            pass
        if ms > best_s:
            best_s = ms
            best_m = (dx, dy)

    # If all moves were invalid (shouldn't happen), stay still.
    if not valid(sx, sy):
        return [0, 0]
    return [int(best_m[0]), int(best_m[1])]