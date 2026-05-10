def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    role = str(observation.get("self_role") or "").lower()
    evader = ("evader" in role) or ("escape" in role) or ("runner" in role)
    pursuer = ("pursuer" in role) or ("chaser" in role) or ("hunter" in role) or (not evader)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    obstacles = list(blocked)

    def dist2(ax, ay, bx, by):
        dx, dy = ax - bx, ay - by
        return dx * dx + dy * dy

    def obs_pen(nx, ny):
        if not obstacles:
            return 0
        md = 10**9
        for x, y in obstacles:
            d = dist2(nx, ny, x, y)
            if d < md:
                md = d
        # Close to obstacles is bad (more strongly when md is 0 or 1)
        return 20 if md == 0 else (8 if md == 1 else (4 if md < 4 else 0))

    best = None
    best_score = None
    # Deterministic tie-break ordering by (score, -dx, -dy) via explicit comparisons later
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in blocked:
            continue
        d = dist2(nx, ny, ox, oy)
        p = obs_pen(nx, ny)
        if pursuer:
            # Minimize distance to opponent, avoid obstacles.
            score = d * 10 + p * 50
        else:
            # Maximize distance; also avoid trapping into tight/obstacle proximity.
            score = (-d) * 10 + p * 50
        # Tie-break: prefer moves that reduce dx,dy lexicographically deterministically
        if best is None or (score < best_score if pursuer else score > best_score) or (score == best_score and (dx, dy) < best):
            best = (dx, dy)
            best_score = score

    if best is None:
        return [0, 0]
    return [best[0], best[1]]