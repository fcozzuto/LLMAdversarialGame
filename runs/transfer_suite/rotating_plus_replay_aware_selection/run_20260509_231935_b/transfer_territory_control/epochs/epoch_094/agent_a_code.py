def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    sx, sy = int(sx), int(sy)
    obs = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles") or []) if isinstance(p, (list, tuple)) and len(p) == 2)
    un = [(int(p[0]), int(p[1])) for p in (observation.get("unclaimed_cells") or []) if isinstance(p, (list, tuple)) and len(p) == 2]
    opp_t = [(int(p[0]), int(p[1])) for p in (observation.get("opponent_territory") or []) if isinstance(p, (list, tuple)) and len(p) == 2]
    opp_set = set(opp_t)

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    def inside(x, y):
        return 0 <= x < w and 0 <= y < h
    def man(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx + dy
    def legal(nx, ny):
        return inside(nx, ny) and (nx, ny) not in obs

    # Pick target deterministically: unclaimed if available, else opponent territory, else center.
    targets = un if un else (opp_t if opp_t else [])
    if targets:
        tx, ty = min(targets, key=lambda t: (man(sx, sy, t[0], t[1]) + 0.35 * man(int(cx), int(cy), t[0], t[1]), t[1], t[0]))
    else:
        tx, ty = int(round(cx)), int(round(cy))

    dirs = [(-1, 0), (0, -1), (0, 0), (1, 0), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1)]
    best_score = None
    best_move = [0, 0]
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        score = 0
        if (nx, ny) in un:
            score += 100000
        if (nx, ny) in opp_set:
            score += 50000
        score += 2000 - 4 * man(nx, ny, tx, ty)
        score += int(-man(nx, ny, int(cx), int(cy)) * 3)
        # Prefer reducing distance to target; tie-break toward center, then lexicographic.
        if best_score is None or score > best_score or (score == best_score and (man(nx, ny, int(cx), int(cy)), nx, ny) < (man(best_move[0] + sx, best_move[1] + sy, int(cx), int(cy)), best_move[0] + sx, best_move[1] + sy)):
            best_score = score
            best_move = [dx, dy]
    return [int(best_move[0]), int(best_move[1])]