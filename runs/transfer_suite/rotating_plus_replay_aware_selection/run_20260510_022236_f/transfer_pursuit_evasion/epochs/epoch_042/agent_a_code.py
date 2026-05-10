def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    role = str(observation.get("self_role", "") or "").lower()
    is_evader = "evader" in role

    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def clamp_inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def wall_dist(x, y):
        return min(x, y, (w - 1) - x, (h - 1) - y)

    def score_cell(nx, ny):
        d = abs(nx - ox) + abs(ny - oy)
        # obstacle avoidance
        if (nx, ny) in obs:
            return -10**9 if not is_evader else -10**9
        pen_obs = 0
        for ax, ay in obs:
            md = abs(nx - ax) + abs(ny - ay)
            if md == 0:
                pen_obs += 1000
            elif md == 1:
                pen_obs += 25
            elif md == 2:
                pen_obs += 8
        # border preference to avoid getting cornered as evader; less important as pursuer
        wd = wall_dist(nx, ny)
        border_pen = 0 if wd >= 1 else 20
        if is_evader:
            # maximize distance; prefer slightly central and avoid obstacles
            return d * 10 - pen_obs - border_pen
        else:
            # minimize distance; prefer moving toward opponent while avoiding obstacles
            return -(d * 10) - pen_obs - (0 if wd >= 1 else 2)

    # Deterministic tie-break: prefer (0,0) then lexicographic dx,dy
    ordered = []
    for dx, dy in moves:
        if dx == 0 and dy == 0:
            ordered.append((dx, dy))
    for dx, dy in moves:
        if not (dx == 0 and dy == 0):
            ordered.append((dx, dy))

    best = None
    best_move = (0, 0)
    for dx, dy in ordered:
        nx, ny = sx + dx, sy + dy
        if not clamp_inside(nx, ny):
            continue
        if (nx, ny) in obs:
            continue
        s = score_cell(nx, ny)
        if best is None or s > best:
            best = s
            best_move = (dx, dy)

    if best is None:
        # fallback: ignore obstacles, only bounds
        for dx, dy in ordered:
            nx, ny = sx + dx, sy + dy
            if not clamp_inside(nx, ny):
                continue
            s = -10**9 if (nx, ny) in obs else score_cell(nx, ny)
            if best is None or s > best:
                best = s
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]