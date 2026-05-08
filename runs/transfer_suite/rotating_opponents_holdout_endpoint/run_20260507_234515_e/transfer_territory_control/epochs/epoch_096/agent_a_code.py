def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    sx, sy = int(sx), int(sy)
    ox, oy = observation.get("opponent_position") or (w - 1, h - 1)
    ox, oy = int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        try:
            obstacles.add((int(p[0]), int(p[1])))
        except Exception:
            pass

    self_t = set()
    for p in observation.get("self_territory") or []:
        try:
            self_t.add((int(p[0]), int(p[1])))
        except Exception:
            pass

    opp_t = set()
    for p in observation.get("opponent_territory") or []:
        try:
            opp_t.add((int(p[0]), int(p[1])))
        except Exception:
            pass

    unclaimed = set()
    for p in observation.get("unclaimed_cells") or []:
        try:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                unclaimed.add((x, y))
        except Exception:
            pass

    dirs = [(-1, 0), (0, -1), (0, 0), (1, 0), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def neigh_obs(x, y):
        # penalize stepping into tight obstacle corridors
        c = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                if (x + ax, y + ay) in obstacles:
                    c += 1
        return c

    best_move = (0, 0)
    best_score = -10**9

    # Bias progress towards opponent corner (w-1,h-1), but deny proximity
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue

        # Base: progress along diagonal + stay alive (avoid opponent)
        progress = (nx / (w - 1 if w > 1 else 1)) + (ny / (h - 1 if h > 1 else 1))
        d_opp = abs(nx - ox) + abs(ny - oy)

        # Territory outcome on entry
        if (nx, ny) in opp_t:
            outcome = 6.0  # flipping is enabled
        elif (nx, ny) in unclaimed:
            outcome = 3.2
        elif (nx, ny) in self_t:
            outcome = 1.0
        else:
            outcome = 0.8  # safety fallback

        # Avoid moving into obstacle-adjacent cells; also prefer expanding away from opponent line
        obs_pen = 0.7 * neigh_obs(nx, ny)
        edge_pen = 0.15 * (min(nx, w - 1 - nx) + min(ny, h - 1 - ny)) / 1.0

        score = 2.2 * outcome + 1.4 * progress - 0.06 * d_opp - obs_pen - edge_pen
        # Tiny deterministic tie-breaker favor towards (w-1,h-1)
        score += 1e-4 * (dx * (w - 1) + dy * (h - 1))

        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]