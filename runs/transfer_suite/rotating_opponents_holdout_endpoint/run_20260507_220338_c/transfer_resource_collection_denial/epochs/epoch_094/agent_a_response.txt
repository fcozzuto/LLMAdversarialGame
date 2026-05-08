def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))

    obst = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obst:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx >= dy else dy

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    legal = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obst:
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    tr = int(observation.get("turns_remaining", 0))
    urgent = 1 if tr <= 4 else 0

    # Target selection: prefer resources where we can arrive sooner than opponent.
    best = None
    best_key = None
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # Lower is better: prioritize winning race to resource; when close to end, go strictly nearest.
        race = (ds - do)  # negative means we are ahead
        k = 0.0 if urgent else 1.0
        val = (ds if urgent else ds + k * max(0, race) + 0.25 * (race))
        # Deterministic tie-break: by ds then coordinates.
        key = (val, ds, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry)

    rx, ry = best

    # Move choice: greedy to target with local avoidance of opponent.
    best_move = None
    best_move_val = None
    for dx, dy, nx, ny in legal:
        d_to_target = cheb(nx, ny, rx, ry)
        # Strongly discourage moving onto/near opponent when it would likely steal.
        d_op = cheb(nx, ny, ox, oy)
        # If we are very close to end, focus only on reaching target.
        opp_pen = 0.0 if urgent else (2.2 / (d_op + 1))  # smaller d_op => larger penalty
        # Tiny deterministic preference to reduce oscillation: prefer dx then dy ordering via key.
        val = d_to_target + opp_pen + 0.001 * (abs(dx) + abs(dy))
        if best_move_val is None or val < best_move_val:
            best_move_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]