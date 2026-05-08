def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    self_role = (observation.get("self_role") or "").lower()
    opp_role = (observation.get("opponent_role") or "").lower()
    is_evader = ("evader" in self_role) or ("evasion" in self_role) or ("escape" in self_role)
    is_pursuer = ("pursuer" in self_role) or ("pursue" in self_role) or ("pursuit" in self_role)
    if not is_evader and not is_pursuer:
        is_evader = ("evader" in opp_role) or ("evasion" in opp_role) or ("escape" in opp_role) == False
        is_pursuer = not is_evader

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p is not None and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def blocked(x, y):
        return (x, y) in obstacles

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    best = None
    best_val = None
    # Deterministic tie-break: fixed dir order, choose first with best value.
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or blocked(nx, ny):
            nx, ny = sx, sy
            dx, dy = 0, 0
        d = abs(nx - ox) + abs(ny - oy)
        # Favor corner/axis separation for evasion_corner archetype; bias away from opponent.
        if is_evader:
            # Choose a "run corner" opposite to opponent's quadrant.
            runx = 0 if ox >= w / 2 else w - 1
            runy = 0 if oy >= h / 2 else h - 1
            corner_bias = abs(nx - runx) + abs(ny - runy)
            # Keep distance priority, then maximize corner_bias to keep heading outward.
            val = d * 1000 + corner_bias
        else:
            # Pursuer: greedy chase; add a small penalty for being near obstacles to avoid getting stuck.
            obs_pen = 0
            for (px, py) in obstacles:
                md = abs(px - nx) + abs(py - ny)
                if md == 0:
                    obs_pen = 10**6
                    break
                if md == 1:
                    obs_pen += 20
            val = -(d * 1000 - obs_pen)
        if best_val is None or val > best_val:
            best_val = val
            best = (dx, dy)

    # Safety fallback (shouldn't happen)
    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]