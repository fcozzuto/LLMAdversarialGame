def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for o in observation.get("obstacles", []) or []:
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            x, y = int(o[0]), int(o[1])
        elif isinstance(o, dict) and "x" in o and "y" in o:
            x, y = int(o["x"]), int(o["y"])
        else:
            continue
        if 0 <= x < w and 0 <= y < h:
            obstacles.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def free(x, y):
        return inb(x, y) and (x, y) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    legal = []
    for dx, dy in moves:
        if free(sx + dx, sy + dy):
            legal.append((dx, dy))
    if not legal:
        return [0, 0]

    role = (observation.get("self_role", "") or "").lower()
    is_evader = ("evader" in role) or ("runner" in role) or ("escape" in role) or ("evade" in role)

    resources = observation.get("resources", []) or []
    best_t = None
    best_d = None
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
        elif isinstance(r, dict) and "x" in r and "y" in r:
            x, y = int(r["x"]), int(r["y"])
        else:
            continue
        if not free(x, y):
            continue
        d = abs(sx - x) + abs(sy - y)
        if best_d is None or d < best_d:
            best_d, best_t = d, (x, y)

    if best_t is not None:
        tx, ty = best_t
        want_min = True
    else:
        tx, ty = (ox, oy)
        want_min = not is_evader

    def md(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    best_move = legal[0]
    best_val = None
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        val = md(nx, ny, tx, ty)
        if best_val is None:
            best_val = val
            best_move = (dx, dy)
        else:
            if want_min:
                if val < best_val:
                    best_val, best_move = val, (dx, dy)
            else:
                if val > best_val:
                    best_val, best_move = val, (dx, dy)
    return [best_move[0], best_move[1]]