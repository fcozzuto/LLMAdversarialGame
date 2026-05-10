def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for t in observation.get("obstacles") or []:
        if isinstance(t, (list, tuple)) and len(t) >= 2:
            x, y = int(t[0]), int(t[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    role = (observation.get("self_role") or "").lower()
    i_am_evader = ("evader" in role) or ("runner" in role) or ("evasion" in role) or ("escape" in role)

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0), (-1, -1), (-1, 1), (1, -1), (1, 1)]
    def dist2(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        return dx * dx + dy * dy

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    best = (None, None, None)  # (score, nx, ny)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d_now = dist2(nx, ny, ox, oy)

        # One-step lookahead to reduce getting boxed by local obstacles.
        best_next = None
        for ddx, ddy in dirs:
            nnx, nny = nx + ddx, ny + ddy
            if not valid(nnx, nny):
                continue
            d_next = dist2(nnx, nny, ox, oy)
            if best_next is None:
                best_next = d_next
            else:
                best_next = d_next if ((not i_am_evader) and d_next < best_next) or (i_am_evader and d_next > best_next) else best_next

        # Score: pursuer wants smaller distance; evader wants larger distance.
        if best_next is None:
            best_next = d_now
        score = best_next - (0.25 * d_now if i_am_evader else 0.25 * (-d_now))  # keep deterministic bias

        # Deterministic tie-break: prefer moves that progress in x, then y, then staying.
        pref = (0 if dx == 0 else 1, 0 if dy == 0 else 1, 1 if (dx == 0 and dy == 0) else 0)
        # For pursuer, higher score is worse; invert.
        if not i_am_evader:
            score = -score

        if best[0] is None or score > best[0] or (score == best[0] and (nx, ny, dx, dy) < (best[1], best[2], best[1] - sx, best[2] - sy)):
            best = (score, nx, ny)

    if best[0] is None:
        return [0, 0]

    # Convert chosen nx,ny back to a move (must be one step).
    nx, ny = best[1], best[2]
    dx, dy = nx - sx, ny - sy
    if dx < -1: dx = -1
    elif dx > 1: dx = 1
    if dy < -1: dy = -1
    elif dy > 1: dy = 1
    return [int(dx), int(dy)]