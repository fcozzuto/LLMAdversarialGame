def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obst = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obst.add((int(p[0]), int(p[1])))

    role = (observation.get("self_role") or "").lower()
    evader = any(k in role for k in ("evader", "escape", "runner", "flee", "evade"))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    def dist2(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        return dx * dx + dy * dy

    # Limited BFS to choose next step deterministically around obstacles
    def best_step(target_foe, maximize):
        # target_foe: (tx, ty)
        horizon = 6
        best = None
        best_s = -10**18 if maximize else 10**18
        for dx0, dy0 in dirs:
            nx, ny = sx + dx0, sy + dy0
            if not inb(nx, ny):
                continue
            q = [(nx, ny, 0)]
            seen = {(nx, ny)}
            score = None
            while q:
                x, y, d = q.pop(0)
                # evaluation at first time reaching horizon (deterministic tie-break)
                if d == horizon:
                    s = dist2(x, y, target_foe[0], target_foe[1])
                    if score is None or (maximize and s > score) or ((not maximize) and s < score):
                        score = s
                    continue
                # Expand in deterministic direction order
                for ddx, ddy in dirs:
                    xx, yy = x + ddx, y + ddy
                    if (xx, yy) in seen or not inb(xx, yy):
                        continue
                    seen.add((xx, yy))
                    q.append((xx, yy, d + 1))
            if score is None:
                score = dist2(nx, ny, target_foe[0], target_foe[1])
            # slight preference for moving (0,0) only if tie
            move_pen = 0 if (dx0 == 0 and dy0 == 0) else 1
            if maximize:
                cand = score * 100 + move_pen
                if cand > best_s or (cand == best_s and (dx0, dy0) < best):
                    best_s = cand
                    best = (dx0, dy0)
            else:
                cand = (-score) * 100 + move_pen
                if cand > best_s or (cand == best_s and (dx0, dy0) < best):
                    best_s = cand
                    best = (dx0, dy0)
        if best is None:
            return [0, 0]
        return [best[0], best[1]]

    if evader:
        # maximize distance from pursuer
        return best_step((ox, oy), maximize=True)

    # pursuer: minimize distance (try to head toward evader)
    return best_step((ox, oy), maximize=False)