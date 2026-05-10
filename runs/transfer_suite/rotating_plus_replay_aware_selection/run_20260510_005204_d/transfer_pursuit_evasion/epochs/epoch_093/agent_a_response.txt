def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    role = str(observation.get("self_role", "")).lower()
    is_evader = ("evader" in role) or ("runner" in role) or ("evade" in role) or ("escape" in role)
    if "environment_name" in observation:
        env = str(observation.get("environment_name", "")).lower()
        if any(k in env for k in ["evader", "runner", "evade", "escape"]):
            is_evader = True

    blocked = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            blocked.add((int(p[0]), int(p[1])))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    # Prefer going toward/away a target corner when evading
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    def corner_score(c):
        cx, cy = c
        d = (sx - cx) * (sx - cx) + (sy - cy) * (sy - cy)
        return d

    target_corner = max(corners, key=corner_score) if is_evader else None

    def eval_move(dx, dy):
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in blocked:
            return None
        d2 = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
        if is_evader:
            # maximize distance from pursuer, then maximize distance from nearest obstacle, then toward target corner
            ob_pen = 0
            for bx, by in blocked:
                adx = abs(nx - bx)
                ady = abs(ny - by)
                if adx + ady <= 2:
                    ob_pen += (3 - (adx + ady))
            tc = target_corner
            extra = 0
            if tc is not None:
                extra = (nx - tc[0]) * (nx - tc[0]) + (ny - tc[1]) * (ny - tc[1])
            return d2 * 100 - ob_pen * 10 + extra
        else:
            # minimize distance to evader, then reduce distance to own corner to avoid being cornered
            d_away = (nx - corners[0][0]) * (nx - corners[0][0]) + (ny - corners[0][1]) * (ny - corners[0][1])
            # Secondary: prefer staying mobile (more free neighbors)
            free = 0
            for ddy in [-1, 0, 1]:
                for ddx in [-1, 0, 1]:
                    if ddx == 0 and ddy == 0:
                        continue
                    tx, ty = nx + ddx, ny + ddy
                    if inb(tx, ty) and (tx, ty) not in blocked:
                        free += 1
            return -d2 * 100 + free * 3 - d_away * 0.001

    best = None
    best_val = None
    for dx, dy in moves:
        v = eval_move(dx, dy)
        if v is None:
            continue
        if best_val is None or v > best_val:
            best_val = v
            best = [dx, dy]
    if best is None:
        return [0, 0]
    return best