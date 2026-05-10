def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    w, h = observation.get("grid_width", 1), observation.get("grid_height", 1)

    obs_list = observation.get("obstacles") or []
    obstacles = set()
    for p in obs_list:
        try:
            obstacles.add((p[0], p[1]))
        except Exception:
            pass

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    best = None
    best_score = None

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    # If any provided "unclaimed_cells", prefer moving toward the closest.
    unclaimed = observation.get("unclaimed_cells") or []
    has_unclaimed = len(unclaimed) > 0

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        score = man(nx, ny, ox, oy)
        if has_unclaimed:
            # Find nearest unclaimed to this candidate (small sample for speed).
            k = min(8, len(unclaimed))
            local_best = None
            for i in range(k):
                c = unclaimed[i]
                cx, cy = c[0], c[1]
                d = man(nx, ny, cx, cy)
                if local_best is None or d < local_best:
                    local_best = d
            score = score * 10 + (local_best if local_best is not None else 0)
        # tie-break deterministically by dx,dy order
        if best_score is None or score < best_score or (score == best_score and (dx, dy) == best):
            best_score = score
            best = (dx, dy)

    if best is None:
        # fallback: try staying put if blocked, otherwise move left deterministically
        if inb(sx, sy) and (sx, sy) not in obstacles:
            return [0, 0]
        # find any in-bounds non-obstacle single step
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                return [dx, dy]
        return [0, 0]

    return [best[0], best[1]]