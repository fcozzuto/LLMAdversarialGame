def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
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

    def dist(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx + dy

    moves = [(-1, 0), (0, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1)]
    cx, cy = w // 2, h // 2

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    # Predict opponent next step toward its nearest resource (greedy).
    if resources:
        tr = min(resources, key=lambda rr: (dist(ox, oy, rr[0], rr[1]), dist(cx, cy, rr[0], rr[1])))
        best_step = (0, 0)
        best_d = 10**9
        for dx, dy in moves:
            nx, ny = ox + dx, oy + dy
            if not valid(nx, ny): 
                continue
            d = dist(nx, ny, tr[0], tr[1])
            if d < best_d:
                best_d = d
                best_step = (dx, dy)
        nox, noy = ox + best_step[0], oy + best_step[1]
    else:
        nox, noy = ox, oy

    best_move = (0, 0)
    best_val = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        if not resources:
            val = -dist(nx, ny, cx, cy)
        else:
            val = -dist(nx, ny, cx, cy) * 0.01
            for rx, ry in resources:
                myd = dist(nx, ny, rx, ry)
                opd = dist(nox, noy, rx, ry)
                # Strong preference for resources we can reach first; moderate defense for contested ones.
                if myd < opd:
                    val += 20.0 / (1.0 + myd)
                elif myd == opd:
                    val += 4.0 / (1.0 + myd)
                else:
                    val -= 18.0 / (1.0 + myd) + 0.5 / (1.0 + opd)
        if val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]