def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def legal(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        dy = ay - by
        dx = -dx if dx < 0 else dx
        dy = -dy if dy < 0 else dy
        return dx if dx > dy else dy

    def eval_from(px, py):
        if not resources:
            cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
            return -abs(px - cx) - abs(py - cy) * 0.01
        best = -10**9
        for tx, ty in resources:
            dm = cheb(px, py, tx, ty)
            do = cheb(ox, oy, tx, ty)
            # Favor resources where we can arrive earlier; tie-break by smaller distance
            win = 1 if dm < do else 0
            eq = 1 if dm == do else 0
            score = (win * 1000) + (eq * 50) - dm * 3 + do * 0.5
            # If we can't win this race, penalize the delay relative to opponent
            if dm >= do:
                score -= (dm - do) * 5
            if score > best:
                best = score
        return best

    best_move = (0, 0)
    best_val = -10**18
    best_secondary = 10**9
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        v = eval_from(nx, ny)
        # secondary: prefer closer to nearest resource if any, else closer to center
        if resources:
            sec = min(cheb(nx, ny, tx, ty) for tx, ty in resources)
        else:
            sec = int(abs(nx - (w - 1) // 2) + abs(ny - (h - 1) // 2))
        if v > best_val or (v == best_val and sec < best_secondary):
            best_val = v
            best_secondary = sec
            best_move = (dx, dy)

    dx, dy = best_move
    return [int(dx), int(dy)]