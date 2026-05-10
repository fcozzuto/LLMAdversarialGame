def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for a in observation.get("obstacles", []) or []:
        if isinstance(a, (list, tuple)) and len(a) >= 2:
            obstacles.add((int(a[0]), int(a[1])))

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0),  (0, 0), (1, 0),
             (-1, 1),  (0, 1), (1, 1)]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = abs(x1 - x2)
        dy = abs(y1 - y2)
        return dx if dx > dy else dy

    def adj_obst_pen(x, y):
        p = 0
        for dx, dy in moves:
            if (x + dx, y + dy) in obstacles:
                p += 1
        return p

    def opponent_step(tgtx, tgty):
        cx, cy = ox, oy
        best = None
        bestd = 10**9
        for dx, dy in moves:
            nx, ny = cx + dx, cy + dy
            if not ok(nx, ny):
                continue
            d = cheb(nx, ny, tgtx, tgty)
            if d < bestd:
                bestd = d
                best = (nx, ny, dx, dy)
            elif d == bestd and best is not None:
                # tie-break deterministically: prefer diagonal, then +dx, then +dy, then lex
                cur_diag = (dx != 0 and dy != 0)
                best_dx, best_dy = best[2], best[3]
                best_diag = (best_dx != 0 and best_dy != 0)
                if cur_diag != best_diag:
                    if cur_diag:
                        best = (nx, ny, dx, dy)
                elif dx != best_dx:
                    if dx > best_dx:
                        best = (nx, ny, dx, dy)
                elif dy != best_dy:
                    if dy > best_dy:
                        best = (nx, ny, dx, dy)
                elif (nx, ny) < (best[0], best[1]):
                    best = (nx, ny, dx, dy)
        if best is None:
            return (ox, oy)
        return (best[0], best[1])

    candidates = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        nox, noy = opponent_step(nx, ny)
        dist_after = cheb(nx, ny, nox, noy)
        # prefer large distance, avoid tight obstacle clusters, deterministic tie-bias by turn index
        score = dist_after * 1000 - adj_obst_pen(nx, ny) * 7
        score += (0.01 if ((observation.get("turn_index", 0) + nx + ny) & 1) == 0 else 0.0)
        candidates.append((score, dx, dy, dist_after, nx, ny))

    if not candidates:
        return [0, 0]
    candidates.sort(key=lambda t: (t[0], t[3], -t[4], -t[5], t[1], t[2]), reverse=True)
    _, dx, dy, _, _, _ = candidates[0]
    return [int(dx), int(dy)]