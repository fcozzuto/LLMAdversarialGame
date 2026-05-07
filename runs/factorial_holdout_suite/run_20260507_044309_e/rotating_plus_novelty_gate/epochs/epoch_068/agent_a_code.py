def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    if not (0 <= sx < w and 0 <= sy < h):
        return [0, 0]

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    valid = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            valid.append((dx, dy, nx, ny))
    if not valid:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2; dx = -dx if dx < 0 else dx
        dy = y1 - y2; dy = -dy if dy < 0 else dy
        return dx if dx > dy else dy

    res_set = set(tuple(r) for r in resources)
    for dx, dy, nx, ny in valid:
        if (nx, ny) in res_set:
            return [dx, dy]

    if not resources:
        # fallback: move toward opponent corner (deny by positioning)
        tx, ty = (w - 1, h - 1) if (ox <= sx and oy <= sy) else (0, 0)
        best = None
        bestd = None
        for dx, dy, nx, ny in valid:
            d = cheb(nx, ny, tx, ty)
            if bestd is None or d < bestd:
                bestd = d; best = (dx, dy)
        return [best[0], best[1]] if best is not None else [0, 0]

    best_score = None
    best_t = None
    for rx, ry in resources:
        dme = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        lead = do - dme  # positive means I arrive sooner
        # Prefer resources where I can get a meaningful lead; also prefer closer ones as tie-break
        score = lead * 12 - dme * 1 - (1 if (rx, ry) in res_set else 0)
        # Small bias to sweep across toward top/bottom depending on where opponent is
        score += 2 if (ry == oy) else 0
        # If opponent is closer or equal, de-prioritize strongly
        if lead < 0:
            score -= 15
        if best_score is None or score > best_score:
            best_score = score
            best_t = (rx, ry)

    tx, ty = best_t
    # Choose move that best improves distance to target, with obstacle-aware tiebreaks
    best = None
    best_key = None
    for dx, dy, nx, ny in valid:
        d = cheb(nx, ny, tx, ty)
        do_next = cheb(ox, oy, tx, ty)
        lead_next = do_next - d
        key = (lead_next, -d, -(abs(nx - tx) + abs(ny - ty)), -((nx, ny) in res_set))
        if best_key is None or key > best_key:
            best_key = key; best = (dx, dy)
    return [best[0], best[1]] if best is not None else [0, 0]