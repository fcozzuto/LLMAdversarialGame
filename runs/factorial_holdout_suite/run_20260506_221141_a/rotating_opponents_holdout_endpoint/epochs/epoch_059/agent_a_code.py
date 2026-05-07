def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    opp_near = True if any(cheb(ox, oy, rx, ry) <= cheb(sx, sy, rx, ry) for rx, ry in resources) else False

    # Pick target: strongly prefer resources we can reach no later than opponent; otherwise closest-to-us.
    best = None
    for rx, ry in resources:
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        adv = od - sd  # positive if we are closer or equal
        # If opponent is aggressively competitive, favor higher advantage; else favor smaller distance.
        key = (-adv, sd, rx, ry) if opp_near else (sd, -adv, rx, ry)
        if best is None or key < best[0]:
            best = (key, rx, ry)
    _, tx, ty = best[0], best[1], best[2]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    # Deterministically evaluate: maximize (opponent progress disadvantage) and our progress; avoid stepping into obstacles/out of bounds.
    best_move = (0, 0)
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny):
            continue
        sd_now = cheb(sx, sy, tx, ty)
        sd_next = cheb(nx, ny, tx, ty)
        od_now = cheb(ox, oy, tx, ty)
        od_next = cheb(ox, oy, tx, ty)  # opponent doesn't move this turn in evaluation

        # Prefer bigger reduction in our distance; tie-break by being at least as good relative to opponent.
        progress = sd_now - sd_next
        advantage = (od_next - sd_next)
        # Small penalty for moving away from target.
        score = (-(sd_next), -(-advantage), -progress, dx, dy)
        # Actually compare by a tuple that prefers closer, higher advantage, higher progress.
        score = (sd_next, -advantage, -progress, dx, dy)

        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]