def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    tleft = observation.get("turns_remaining", 0)

    obs_set = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs_set.add((p[0], p[1]))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs_set

    legal = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny):
                legal.append((dx, dy))
    if not legal:
        return [0, 0]

    if not resources:
        # step toward center while keeping away from opponent
        cx, cy = w // 2, h // 2
        best = None
        for dx, dy in legal:
            nx, ny = sx + dx, sy + dy
            s = -cheb(nx, ny, cx, cy) + 0.2 * cheb(nx, ny, ox, oy)
            if best is None or s > best[0]:
                best = (s, dx, dy)
        return [best[1], best[2]]

    # Choose target that we can reach no slower than opponent; otherwise least bad race.
    best_t = None
    best_score = None
    for tx, ty in resources:
        sd = cheb(sx, sy, tx, ty)
        od = cheb(ox, oy, tx, ty)
        # earlier is better; having an advantage is much better; avoid dead races
        s = (od - sd) * 3.0 - sd * 0.35 + (1.5 if sd <= od else -0.8) - (0.01 * (sd + od))
        if best_score is None or s > best_score:
            best_score = s
            best_t = (tx, ty)

    tx, ty = best_t

    # If very late, prioritize immediate capture (cheapest move to target).
    late = 0.25 if tleft > 0 else 1.0
    if tleft <= 2:
        late = 0.0

    best = None
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        sd = cheb(nx, ny, tx, ty)
        od = cheb(ox, oy, tx, ty)
        # prefer moves that reduce our distance; also prevent opponent getting much closer
        # (opponent stays fixed for this one-step heuristic).
        score = -sd * (1.2 + late) + (1.0 if sd <= od else -0.3) + 0.05 * cheb(nx, ny, ox, oy)
        if best is None or score > best[0]:
            best = (score, dx, dy)

    return [best[1], best[2]]