def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x = int(p[0]); y = int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x = int(r[0]); y = int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def md(tx, ty, ax, ay):
        dx = tx - ax
        if dx < 0: dx = -dx
        dy = ty - ay
        if dy < 0: dy = -dy
        return dx + dy

    if not resources:
        # No visible resources: move to a corner away from opponent if possible
        corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        tx, ty = max(corners, key=lambda c: md(c[0], c[1], ox, oy) - md(c[0], c[1], sx, sy))
    else:
        # Pick best resource by (1) my speed, (2) ensure I'm not much behind opponent, (3) tie-break by position
        best = None
        best_key = None
        for rx, ry in resources:
            myd = md(rx, ry, sx, sy)
            opd = md(rx, ry, ox, oy)
            # want myd small; strong penalty if I'm behind; slight reward if I'm ahead
            key = (myd, -(opd - myd), rx + ry * 0.001)
            # For more aggressive "race", compare relative advantage
            key = (myd + (0 if myd <= opd else (opd - myd) * 2), -(opd - myd), rx + ry)
            if best_key is None or key < best_key:
                best_key = key
                best = (rx, ry)
        tx, ty = best

    dx = tx - sx
    if dx > 0: step_x = 1
    elif dx < 0: step_x = -1
    else: step_x = 0
    dy = ty - sy
    if dy > 0: step_y = 1
    elif dy < 0: step_y = -1
    else: step_y = 0

    # If target cell is blocked, try alternative steps deterministically
    cand = []
    for mx in (-1, 0, 1):
        for my in (-1, 0, 1):
            if mx == 0 and my == 0:
                continue
            nx, ny = sx + mx, sy + my
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                cand.append((nx, ny, mx, my))
    if not cand:
        return [0, 0]

    # Evaluate candidate by decrease in distance to target, with a small push to keep away from opponent
    bestm = (0, 0, 0)
    best_score = None
    for nx, ny, mx, my in cand:
        dist = md(tx, ty, nx, ny)
        opp = md(nx, ny, ox, oy)
        # Prefer moving closer; if tied, prefer farther from opponent
        score = (dist, -opp, (nx + ny))
        if best_score is None or score < best_score:
            best_score = score
            bestm = (mx, my, dist)

    return [int(bestm[0]), int(bestm[1])]