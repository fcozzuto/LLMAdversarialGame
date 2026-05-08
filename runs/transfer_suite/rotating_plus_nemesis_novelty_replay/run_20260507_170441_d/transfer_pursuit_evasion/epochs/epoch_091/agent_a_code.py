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
        nx, ny = sx + dx, sy + dy
        if free(nx, ny):
            legal.append((dx, dy))
    if not legal:
        return [0, 0]

    role = (observation.get("self_role", "") or "").lower()
    is_evader = ("evader" in role) or ("runner" in role) or ("escape" in role) or ("evade" in role)

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    best_corner = None
    best_cd = -10**18
    for cx, cy in corners:
        cd = (cx - ox) * (cx - ox) + (cy - oy) * (cy - oy)
        if cd > best_cd:
            best_cd = cd
            best_corner = (cx, cy)

    def nearest_obs_d2(x, y):
        md = 10**18
        for (px, py) in obstacles:
            dd = (x - px) * (x - px) + (y - py) * (y - py)
            if dd < md:
                md = dd
        return md if obstacles else 10**12

    tcx, tcy = best_corner
    best_score = None
    best_move = [0, 0]

    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        dist2 = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
        obs_d2 = nearest_obs_d2(nx, ny)
        toward_corner = (nx - tcx) * (nx - tcx) + (ny - tcy) * (ny - tcy)

        if is_evader:
            score = dist2 * 1000 + obs_d2 - toward_corner
        else:
            score = -dist2 * 1000 + obs_d2 * 0.1 - toward_corner * 0.01

        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move