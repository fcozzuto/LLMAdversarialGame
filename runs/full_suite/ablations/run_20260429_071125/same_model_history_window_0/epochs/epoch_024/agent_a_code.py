def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation["resources"]; obstacles = set(tuple(p) for p in observation["obstacles"])
    best_r = None; best_val = -10**9
    for rx, ry in resources:
        sd = abs(rx - sx) + abs(ry - sy)
        od = abs(rx - ox) + abs(ry - oy)
        # Prefer resources we are closer to; otherwise still consider but penalize.
        closeness = (od - sd)  # positive if we're closer
        val = closeness * 100 - sd
        # If resource is at or near center-ish, slightly boost deterministically
        val += -0.01 * (abs(rx - (w-1)/2) + abs(ry - (h-1)/2))
        if val > best_val:
            best_val = val; best_r = (rx, ry)
    if best_r is None:
        return [0, 0]
    tx, ty = best_r

    def clamp(v, lo, hi):
        return lo if v < lo else hi if v > hi else v

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx = clamp(sx + dx, 0, w - 1)
            ny = clamp(sy + dy, 0, h - 1)
            if (nx, ny) in obstacles:
                continue
            # Avoid moving too close to opponent unless it also advances strongly.
            sd_next = abs(tx - nx) + abs(ty - ny)
            sd_now = abs(tx - sx) + abs(ty - sy)
            ndist_opp = abs(ox - nx) + abs(oy - ny)
            opp_close_pen = 0
            if ndist_opp <= 1:
                opp_close_pen = 120
            elif ndist_opp == 2:
                opp_close_pen = 35
            # Mild penalty for stepping into positions that reduce our progress.
            prog = sd_now - sd_next
            val = prog * 30 - sd_next - opp_close_pen
            # Prefer diagonal progress when it matches target direction
            if dx != 0 and dy != 0:
                val += 2
            moves.append((val, dx, dy))
    if not moves:
        return [0, 0]
    moves.sort(key=lambda t: (-t[0], t[1], t[2]))
    return [moves[0][1], moves[0][2]]