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

    if not resources:
        return [0, 0]

    def dist(a, b, c, d):
        dx = a - c
        dy = b - d
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx + dy

    # Prefer collecting resources where we are at least as close as opponent; else deny their likely target.
    best = None  # (score, tx, ty)
    for tx, ty in resources:
        ds = dist(sx, sy, tx, ty)
        do = dist(ox, oy, tx, ty)
        # score: prioritize "we beat them"; tie-break by absolute closeness and avoid unsafe detours
        if ds <= do:
            score = (10.0 * (do - ds) + 3.0) - 0.1 * ds
        else:
            score = (2.0 * (do - ds)) - 0.25 * ds  # still consider as a denial move
        if best is None or score > best[0] or (score == best[0] and ds < best[0] * 0 - ds):
            best = (score, tx, ty)

    _, tx, ty = best

    # Step toward target with diagonal if it reduces distance; avoid stepping onto obstacles (engine would keep us, but avoid it).
    candidates = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == 0 and dy == 0:
                candidates.append((0, 0, sx, sy))
                continue
            nx = sx + dx
            ny = sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                ds_next = dist(nx, ny, tx, ty)
                # also slightly prefer moving away from opponent to reduce contesting
                do_next = dist(nx, ny, ox, oy)
                candidates.append((-(ds_next) + 0.02 * do_next, dx, dy, nx, ny))

    # Deterministic pick: max score, then prefer smaller ds_next, then stable order by dx,dy.
    if not candidates:
        return [0, 0]
    candidates.sort(key=lambda t: (t[0], -dist(sx, sy, ox, oy), -t[1], -t[2]), reverse=True)
    _, dx, dy, nx, ny = candidates[0]
    if (nx, ny) == (sx, sy):
        return [0, 0]
    return [int(dx), int(dy)]