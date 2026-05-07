def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = {(p[0], p[1]) for p in (observation.get("obstacles") or [])}

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    valid = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            valid.append((dx, dy, nx, ny))

    if not valid:
        return [0, 0]

    if not resources:
        tx, ty = w // 2, h // 2
        best = None
        for dx, dy, nx, ny in valid:
            d = max(abs(nx - tx), abs(ny - ty))
            od = max(abs(ox - nx), abs(oy - ny))
            cand = (d, od)
            if best is None or cand < best:
                best = (dx, dy)
        return [best[0], best[1]]

    def val(rx, ry):
        sd = abs(rx - sx) + abs(ry - sy)
        od = abs(rx - ox) + abs(ry - oy)
        on = 1 if (sx == rx and sy == ry) else 0
        # Favor resources we're closer to; if opponent is closer, strongly de-prioritize.
        # Also prefer farther-away opponent for safety (denial opponents).
        return (sd - 0.9 * od - 50 * on, sd, -od)

    target = min(resources, key=lambda r: val(r[0], r[1]))
    tx, ty = target[0], target[1]

    best = None
    for dx, dy, nx, ny in valid:
        # Use same valuation but from the hypothetical next position
        sd = abs(tx - nx) + abs(ty - ny)
        od = abs(tx - ox) + abs(ty - oy)
        on = 1 if (nx == tx and ny == ty) else 0
        cand = (sd - 0.9 * od - 50 * on, sd, abs(ox - nx) + abs(oy - ny))
        if best is None or cand < best:
            best = (dx, dy)
    return [best[0], best[1]]