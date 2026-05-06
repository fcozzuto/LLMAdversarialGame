def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    resources = []
    for p in observation.get("resources", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            resources.append((int(p[0]), int(p[1])))

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    moves8 = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    if not (0 <= sx < w and 0 <= sy < h):
        return [0, 0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist2(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        return dx * dx + dy * dy

    if not resources:
        return [0, 0]

    best_target = None
    best_key = None
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        ds = dist2(sx, sy, rx, ry)
        do = dist2(ox, oy, rx, ry)
        # Prefer close resources for us, but far from opponent
        key = (ds, -do, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best_target = (rx, ry)

    tx, ty = best_target if best_target is not None else resources[0]

    best_move = (0, 0)
    best_score = None
    for dx, dy in moves8:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue
        # Primary: move toward chosen target
        ds = dist2(nx, ny, tx, ty)
        # Secondary: avoid squares that make us too easy to contest (near opponent)
        opp_close = dist2(nx, ny, ox, oy)
        # Tertiary: encourage leaving room (stay away from obstacles slightly)
        obs_pen = 0
        for (bx, by) in obstacles:
            d = abs(nx - bx) + abs(ny - by)
            if d == 0:
                obs_pen = 10**9
                break
            if d <= 2:
                obs_pen += (3 - d)
        if obs_pen >= 10**8:
            continue
        # Combine deterministically
        score = (ds, -opp_close, obs_pen, dx, dy)
        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]