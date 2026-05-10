def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    sr = str(observation.get("self_role") or "").lower()
    self_is_evader = ("evader" in sr) or ("runner" in sr)
    self_is_pursuer = not self_is_evader

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    def dist2(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        return dx * dx + dy * dy

    best = None
    best_val = None
    best_step = None

    # tie-break: prefer moving (avoid 0,0), then prefer smallest lex move
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d = dist2(nx, ny, ox, oy)
        # pursuer wants smaller distance; evader wants larger distance
        score = -d if self_is_pursuer else d
        move_pref = 0 if (dx == 0 and dy == 0) else 1
        # incorporate slight preference for staying aligned with a deterministic "zigzag" rhythm
        rhythm = (observation.get("turn_index", 0) or 0) & 1
        align = (dx == 0 or dy == 0)  # axis move
        score += (0.02 if move_pref else 0) + (0.01 if align and (rhythm == 0) else 0)

        if best_val is None or score > best_val:
            best_val = score
            best = (nx, ny)
            best_step = (dx, dy)
        elif score == best_val:
            cand = (0 if (dx == 0 and dy == 0) else -1, dx, dy)
            cur = (0 if (best_step[0] == 0 and best_step[1] == 0) else -1, best_step[0], best_step[1])
            if cand < cur:
                best_step = (dx, dy)

    if best_step is None:
        return [0, 0]
    return [int(best_step[0]), int(best_step[1])]