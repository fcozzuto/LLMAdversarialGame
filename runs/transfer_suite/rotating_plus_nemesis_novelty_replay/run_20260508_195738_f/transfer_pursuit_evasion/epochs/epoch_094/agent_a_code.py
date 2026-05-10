def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    sr = str(observation.get("self_role", "")).lower()
    orr = str(observation.get("opponent_role", "")).lower()
    # If we are pursuer, try to reduce distance; if evader, try to increase distance.
    we_are_evader = ("evader" in sr) or ("runner" in sr) or ("escape" in sr)
    we_are_pursuer = ("pursuer" in sr) or ("chaser" in sr) or ("capture" in sr)
    if we_are_evader:
        mode = "evade"
    elif we_are_pursuer:
        mode = "pursue"
    else:
        # Fallback: if opponent looks like evader, we likely pursue; otherwise evade.
        mode = "pursue" if ("evader" in orr or "runner" in orr or "escape" in orr) else "evade"

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def wall_tight_pen(x, y):
        d = min(x, y, (w - 1) - x, (h - 1) - y)
        return 0.0 if d >= 2 else (2 - d) * 0.6

    def obs_near_pen(x, y):
        if (x, y) in obstacles:
            return 1e9
        cnt = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax or ay:
                    if (x + ax, y + ay) in obstacles:
                        cnt += 1
        return cnt * 1.2

    best = None
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        md = abs(nx - ox) + abs(ny - oy)
        # Greedy score: evade wants large md; pursue wants small md.
        base = md if mode == "evade" else -md

        # Add mild deterministic shaping: avoid walls/obstacles.
        val = base - wall_tight_pen(nx, ny) - obs_near_pen(nx, ny) * (1.0 if mode == "evade" else 0.6)

        # Tie-break deterministically toward staying put, then toward reducing coordinates.
        if best is None:
            best, best_val = (dx, dy), val
        else:
            if val > best_val + 1e-9:
                best, best_val = (dx, dy), val
            elif abs(val - best_val) <= 1e-9:
                # Prefer (0,0), then smallest lex (dx,dy)
                if (dx, dy) == (0, 0):
                    best, best_val = (dx, dy), val
                else:
                    bdx, bdy = best
                    if (bdx, bdy) != (0, 0) and (dx, dy) < (bdx, bdy):
                        best, best_val = (dx, dy), val

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]