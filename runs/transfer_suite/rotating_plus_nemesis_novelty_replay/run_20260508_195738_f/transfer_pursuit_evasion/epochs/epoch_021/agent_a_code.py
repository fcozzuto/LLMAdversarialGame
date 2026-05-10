def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = set()
    for p in observation.get("obstacles", []):
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obstacles.add((p[0], p[1]))

    self_role = str(observation.get("self_role", "")).lower()
    opp_role = str(observation.get("opponent_role", "")).lower()
    self_is_evader = ("evader" in self_role) or ("evader" in opp_role and "purs" not in self_role)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def man(x, y, a, b):
        dx, dy = x - a, y - b
        return (dx if dx >= 0 else -dx) + (dy if dy >= 0 else -dy)

    def clamp_target(tx, ty):
        if tx < 0: tx = 0
        elif tx >= w: tx = w - 1
        if ty < 0: ty = 0
        elif ty >= h: ty = h - 1
        return tx, ty

    corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
    tx, ty = None, None

    if self_is_evader:
        # Evader: aim for the corner farthest from the pursuer, but avoid steps that approach immediately.
        bestd = -1
        for cx, cy in corners:
            d = man(ox, oy, cx, cy)
            if d > bestd:
                bestd = d
                tx, ty = cx, cy
        tx, ty = clamp_target(tx, ty)
        best_score = None
        best = (0, 0)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            d_opp_now = man(nx, ny, ox, oy)
            d_goal = man(nx, ny, tx, ty)
            score = (d_opp_now * 10) + d_goal  # maximize distance from pursuer, also progress to safe corner
            if best_score is None or score > best_score or (score == best_score and (dx, dy) == (0, 0)):
                best_score = score
                best = (dx, dy)
        return [best[0], best[1]]
    else:
        # Pursuer: greedy shortest step to opponent with obstacle-aware tie-breaking.
        best_score = None
        best = (0, 0)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            d = man(nx, ny, ox, oy)
            # Prefer moving toward opponent; tie-break toward keeping x/y aligned deterministically.
            align = 0
            if nx == ox: align += 1
            if ny == oy: align += 1
            score = (-d * 10) + align
            if best_score is None or score > best_score or (score == best_score and (dx, dy) < best):
                best_score = score
                best = (dx, dy)
        return [best[0], best[1]]