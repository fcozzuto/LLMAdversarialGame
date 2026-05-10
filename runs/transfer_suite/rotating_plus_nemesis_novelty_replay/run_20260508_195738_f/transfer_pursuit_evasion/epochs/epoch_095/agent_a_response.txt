def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    sr = str(observation.get("self_role", "")).lower()
    we_evader = ("evader" in sr) or ("runner" in sr) or ("escape" in sr)
    we_pursuer = ("pursuer" in sr) or ("chaser" in sr) or ("capture" in sr)
    mode = "evade" if we_evader and not we_pursuer else ("pursue" if we_pursuer and not we_evader else ("pursue" if abs(ox - sx) + abs(oy - sy) <= 6 else "evade"))

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def safe(x, y): return inb(x, y) and (x, y) not in obstacles
    def dist2(x, y, a, b):
        dx, dy = x - a, y - b
        return dx * dx + dy * dy

    best = None
    best_sc = None
    # Deterministic tie-breaker by fixed delta order.
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not safe(nx, ny):
            sc = -10**9 if mode == "pursue" else 10**9
        else:
            d = dist2(nx, ny, ox, oy)
            # small boundary avoidance for stability
            edge_pen = min(nx, ny, (w - 1) - nx, (h - 1) - ny)
            edge_pen = 0 if edge_pen < 1 else edge_pen / 10.0
            # nudge away from obstacles by proximity (only for pursuer too, to avoid dead-ends)
            obs_pen = 0.0
            for (px, py) in obstacles:
                ddx, ddy = nx - px, ny - py
                if abs(ddx) <= 1 and abs(ddy) <= 1:
                    obs_pen += 0.75 / (ddx * ddx + ddy * ddy + 1)
            if mode == "pursue":
                sc = -d + edge_pen - obs_pen
            else:
                # evade: maximize distance, also avoid edges a bit
                sc = d + edge_pen - obs_pen
        if best_sc is None or sc > best_sc:
            best_sc = sc
            best = (dx, dy)
    return [int(best[0]), int(best[1])]