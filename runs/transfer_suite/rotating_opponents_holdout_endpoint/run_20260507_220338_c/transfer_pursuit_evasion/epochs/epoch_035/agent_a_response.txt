def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            blocked.add((int(p[0]), int(p[1])))

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    role = str(observation.get("self_role", "") or "").lower()
    is_evader = ("evad" in role) or ("run" in role) or ("away" in role) or ("escape" in role)

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    def clamp_step(val):
        if val > 0:
            return 1
        if val < 0:
            return -1
        return 0

    # Predict opponent "zigzag" by reflecting its current relative direction with turn parity.
    rx, ry = ox - sx, oy - sy
    px, py = ox + clamp_step(rx), oy + clamp_step(ry)

    # If predicted outside grid or blocked, fall back to current opponent position.
    if not (0 <= px < w and 0 <= py < h) or (px, py) in blocked:
        px, py = ox, oy
    # Parity tweak to avoid getting stuck against oscillatory policies.
    parity = int(observation.get("turn_index", 0) or 0) & 1
    if parity and ok(ox - clamp_step(rx), oy - clamp_step(ry)):
        px, py = ox - clamp_step(rx), oy - clamp_step(ry)

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    # Penalty for being adjacent to obstacles (helps both pursuer/evader).
    def obstacle_adj(x, y):
        c = 0
        for ax, ay in deltas:
            nx, ny = x + ax, y + ay
            if (nx, ny) in blocked:
                c += 1
        return c

    # Score: pursuer wants distance to predicted opponent to decrease; evader wants increase.
    # Also bias toward "center" when distances are equal to reduce dithering.
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    best_move = (0, 0)
    best_score = -10**18 if not is_evader else 10**18
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        d = cheb(nx, ny, px, py)
        center = abs(nx - cx) + abs(ny - cy)
        obs_pen = obstacle_adj(nx, ny)
        # Capturing is handled by engine (capture_radius=0), but minimizing d is still critical.
        score = (-d if not is_evader else d) - (0.05 * center) - (0.2 * obs_pen)
        if (not is_evader and score > best_score) or (is_evader and score < best_score):
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]