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
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def free(x, y): return inb(x, y) and (x, y) not in obstacles
    self_role = (observation.get("self_role", "") or "").lower()
    evader = ("evader" in self_role) or ("runner" in self_role) or ("escape" in self_role)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def score(nx, ny):
        man = abs(nx - ox) + abs(ny - oy)
        cheb = max(abs(nx - ox), abs(ny - oy))
        # Prefer corner control for pursuer; flee from corners for evader
        corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        corner_md = min(abs(nx - cx) + abs(ny - cy) for cx, cy in corners)
        # Obstacle proximity penalty (only local to keep fast)
        near_obs = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                x, y = nx + ax, ny + ay
                if (x, y) in obstacles:
                    near_obs += 1
        # Small bias to keep moving (avoid staying unless best)
        stay_bias = 1 if (nx == sx and ny == sy) else 0

        if evader:
            # maximize distance, maximize corner safety (far from nearest corner)
            return (man * 10 + cheb * 5 + corner_md * 2) - (near_obs * 3) - (stay_bias * 0.5)
        else:
            # minimize distance, minimize corner closeness penalty (want closer to a corner)
            return -(man * 10 + cheb * 5) + (corner_md * -0.5) - (near_obs * 4) - (stay_bias * 0.25)

    best = None
    best_move = [0, 0]
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        sc = score(nx, ny)
        if best is None or sc > best:
            best = sc
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]