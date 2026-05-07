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

    def cheb(a, b, c, d):
        dx = abs(a - c); dy = abs(b - d)
        return dx if dx > dy else dy

    def score_target(tx, ty):
        if (tx, ty) in obstacles:
            return 10**9
        sd = cheb(sx, sy, tx, ty)
        od = cheb(ox, oy, tx, ty)
        # Prefer resources where we arrive earlier; add slight bias to closer overall.
        return (sd - 0.92 * od) + 0.01 * (sd + cheb(ox, oy, tx, ty))

    if resources:
        best = None
        for tx, ty in resources:
            sc = score_target(tx, ty)
            if best is None or sc < best[0]:
                best = (sc, tx, ty)
        _, tx, ty = best
    else:
        # No visible resources: move toward the most promising remaining count corner bias.
        corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        tx, ty = corners[(sx + sy + int(observation.get("turn_index", 0) or 0)) % 4]

    # Try direct step; if invalid (obstacle/out), try alternative steps that still reduce target distance.
    dirs = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    preferred = []
    for dx, dy in dirs:
        nx = sx + dx; ny = sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        dcur = cheb(sx, sy, tx, ty)
        dnext = cheb(nx, ny, tx, ty)
        # Tie-break: also consider opponent advantage after the move.
        odnext = cheb(ox, oy, tx, ty)
        val = (dnext - 0.92 * odnext) + 0.001 * dnext + 0.0001 * (abs(dx) + abs(dy))
        preferred.append((dnext, val, dx, dy))
    if not preferred:
        return [0, 0]
    preferred.sort(key=lambda t: (t[0], t[1]))
    return [int(preferred[0][2]), int(preferred[0][3])]