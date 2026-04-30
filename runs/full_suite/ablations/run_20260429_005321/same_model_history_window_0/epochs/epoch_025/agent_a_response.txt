def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation["resources"]
    obstacles = set(tuple(p) for p in observation["obstacles"])
    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
    else:
        best = None
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            ds = abs(rx - sx) + abs(ry - sy)
            do = abs(rx - ox) + abs(ry - oy)
            adv = do - ds
            val = (adv * 10) - ds * 0.1 - (1 if (rx == ox and ry == oy) else 0)
            if best is None or val > best[0]:
                best = (val, rx, ry)
        tx, ty = best[1], best[2] if best else ((w - 1) // 2, (h - 1) // 2)

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    # If blocked at current cell by obstacle, just try to move away deterministically.
    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    best_move = (0, 0)
    best_val = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue
        # Move quality: reduce distance to target, but also avoid walking into opponent.
        ds_next = abs(tx - nx) + abs(ty - ny)
        ds_now = abs(tx - sx) + abs(ty - sy)
        # Advantage vs opponent on the target cell
        do = abs(tx - ox) + abs(ty - oy)
        adv_next = do - ds_next
        opp_pen = 5 if (nx == ox and ny == oy) else 0
        step_pen = 0.1 if (dx == 0 and dy == 0) else 0
        val = (adv_next * 10) - ds_next - opp_pen - step_pen + (0.5 if ds_next < ds_now else 0)
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    # If all moves were invalid (shouldn't happen), stay.
    dx, dy = best_move
    if not isinstance(dx, int) or not isinstance(dy, int):
        dx, dy = 0, 0
    if dx not in (-1, 0, 1) or dy not in (-1, 0, 1):
        dx, dy = 0, 0
    return [dx, dy]