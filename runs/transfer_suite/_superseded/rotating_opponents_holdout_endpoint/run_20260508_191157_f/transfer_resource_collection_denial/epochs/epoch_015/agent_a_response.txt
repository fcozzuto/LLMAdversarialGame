def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    if not resources:
        return [0, 0]

    obs = set((p[0], p[1]) for p in obstacles)
    moves = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1), (0, 0)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    best_target = None
    best_val = None
    for rx, ry in resources:
        sd = man(sx, sy, rx, ry)
        od = man(ox, oy, rx, ry)
        # Prefer resources we're closer to; if we're not closer, allow only if opponent is far enough.
        # Tie-break deterministically by our distance then coordinates.
        val = 2 * (od - sd) - sd
        if best_val is None or val > best_val or (val == best_val and (sd < best_target[2] or (sd == best_target[2] and (rx, ry) < (best_target[0], best_target[1])))):
            best_target = (rx, ry, sd)
            best_val = val

    tx, ty, _ = best_target

    best_move = (0, 0)
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        sd2 = man(nx, ny, tx, ty)
        od2 = man(ox, oy, tx, ty)
        lead = od2 - sd2
        # Move towards target; primary objective is improving race lead for that target.
        key = (lead, -sd2, -(dx * dx + dy * dy), dx, dy)
        if best_key is None or key > best_key:
            best_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]