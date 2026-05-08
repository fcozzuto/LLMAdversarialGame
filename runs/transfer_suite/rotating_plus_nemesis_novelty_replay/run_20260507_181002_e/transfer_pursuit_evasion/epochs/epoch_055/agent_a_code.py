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

    sr = str(observation.get("self_role", "")).lower()
    orr = str(observation.get("opponent_role", "")).lower()
    self_is_evader = ("evader" in sr) or ("runner" in sr) or (("pursuer" not in sr) and ("evader" in orr))

    moves = [(0, 0), (1, 1), (1, 0), (1, -1), (0, 1), (0, -1), (-1, 1), (-1, 0), (-1, -1)]
    def free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    # obstacle proximity (min Manhattan to any obstacle, capped)
    obs_list = list(obstacles)
    def safe_bonus(x, y):
        if not obs_list:
            return 0.0
        md = 10**9
        for (px, py) in obs_list:
            d = abs(x - px) + abs(y - py)
            if d < md:
                md = d
        # prefer staying away; large penalty near obstacles
        if md <= 0:
            return -5.0
        if md == 1:
            return -1.5
        if md == 2:
            return -0.6
        return 0.1

    best = None
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        d_after = man(nx, ny, ox, oy)
        # bias toward/away from opponent direction to break ties deterministically
        step_dx = 0 if ox == sx else (1 if ox > sx else -1)
        step_dy = 0 if oy == sy else (1 if oy > sy else -1)
        align = -(abs(dx - step_dx) + abs(dy - step_dy))  # closer to direct step => higher
        if self_is_evader:
            score = d_after + 0.2 * safe_bonus(nx, ny) + 0.05 * (-align)
        else:
            score = -d_after + 0.2 * safe_bonus(nx, ny) + 0.05 * align

        if best_score is None or score > best_score:
            best_score = score
            best = [dx, dy]
        elif score == best_score:
            # deterministic tie-break: prefer earlier in moves list
            if best is None:
                best = [dx, dy]
            else:
                if moves.index((dx, dy)) < moves.index((best[0], best[1])):
                    best = [dx, dy]

    return best if best is not None else [0, 0]