def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles", []) or []))
    if not resources:
        return [0, 0]

    def man(x1, y1, x2, y2):
        dx = x1 - x2; dx = -dx if dx < 0 else dx
        dy = y1 - y2; dy = -dy if dy < 0 else dy
        return dx + dy

    def clamp(x, lo, hi):
        return lo if x < lo else hi if x > hi else x

    # Pick a contested resource: prefer ones we can reach sooner; otherwise contest the closest one.
    best = None
    for rx, ry in resources:
        ds = man(sx, sy, rx, ry)
        do = man(ox, oy, rx, ry)
        # If tie, prefer the one that is closer to us (larger advantage key uses -ds)
        key = (ds > do, ds - do, ds, rx, ry)  # primary: we want ds<=do, then most negative (we win sooner), then nearest
        if best is None or key < best[0]:
            best = (key, rx, ry, ds, do)
    _, tx, ty, ds, do = best

    # Decide goal cell:
    # If we can arrive no later than opponent, go directly to the resource.
    # Else, intercept: move toward the cell just ahead of opponent on the path to the resource.
    if ds <= do:
        gx, gy = tx, ty
    else:
        stepx = 0 if ox == tx else (1 if tx > ox else -1)
        stepy = 0 if oy == ty else (1 if ty > oy else -1)
        ix, iy = ox + stepx, oy + stepy
        # Prefer the intercept if it's valid and not an obstacle; otherwise step toward resource (still deterministic).
        if 0 <= ix < w and 0 <= iy < h and (ix, iy) not in obstacles:
            gx, gy = ix, iy
        else:
            gx, gy = ox + stepx, oy  # fallback
            if not (0 <= gx < w and 0 <= gy < h) or (gx, gy) in obstacles:
                gx, gy = ox, oy + stepy
                if not (0 <= gx < w and 0 <= gy < h) or (gx, gy) in obstacles:
                    gx, gy = tx, ty

    # Convert goal cell to one-step delta toward it (diagonal allowed).
    dx = 0 if gx == sx else (1 if gx > sx else -1)
    dy = 0 if gy == sy else (1 if gy > sy else -1)
    nx, ny = sx + dx, sy + dy
    if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
        return [dx, dy]

    # If blocked, try axis-aligned deterministic alternatives.
    for adx, ady in ((dx, 0), (0, dy), (-dx, 0), (0, -dy), (0, 0)):
        nx, ny = sx + adx, sy + ady
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            return [adx, ady]
    return [0, 0]