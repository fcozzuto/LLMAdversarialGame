def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obstacles.add((int(p[0]), int(p[1])))

    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    sr = str(observation.get("self_role", "")).lower()
    self_is_evader = ("evader" in sr) or ("runner" in sr)

    def free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    if self_is_evader:
        # run to maximize distance (and prefer safer/center-cushioning deterministically)
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        best = None
        best_val = -10**18
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not free(nx, ny):
                continue
            if nx == ox and ny == oy:
                val = -10**12
            else:
                d = dist(nx, ny, ox, oy)
                center = -((nx - cx) ** 2 + (ny - cy) ** 2)  # closer to center slightly preferred
                val = d * 1000 + center
            if val > best_val:
                best_val = val
                best = [dx, dy]
        return best if best is not None else [0, 0]
    else:
        # pursuer: worst-case 1-step opponent response assuming they maximize distance
        best = None
        best_val = 10**18
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not free(nx, ny):
                continue
            if nx == ox and ny == oy:
                return [dx, dy]
            worst = -1
            for odx, ody in moves:
                mx, my = ox + odx, oy + ody
                if not free(mx, my):
                    continue
                if mx == nx and my == ny:
                    d = -1  # capture would occur; worst for us is avoided, so treat as very bad
                else:
                    d = dist(nx, ny, mx, my)
                if d > worst:
                    worst = d
            # tie-break: also prefer moves that keep opponent "in front" by reducing max L_inf-ish spread
            cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
            tie = -((nx - cx) ** 2 + (ny - cy) ** 2)
            val = worst * 1000 + (-tie)
            if val < best_val:
                best_val = val
                best = [dx, dy]
        return best if best is not None else [0, 0]