def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles_raw = observation.get("obstacles", []) or []
    obstacles = set((p[0], p[1]) for p in obstacles_raw)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def blocked(x, y):
        return (not inb(x, y)) or ((x, y) in obstacles)

    def man(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx + dy

    def clamp_step(v):
        return -1 if v < 0 else (1 if v > 0 else 0)

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if not resources:
        # When no visible resources, head to a corner away from opponent as a deterministic fallback.
        tx, ty = (0, 0) if (sx + sy) > (ox + oy) else (w - 1, h - 1)
        return [clamp_step(tx - sx), clamp_step(ty - sy)]

    # Choose a contested-aware target (maximize advantage over opponent).
    best_target = resources[0]
    best_adv = -10**18
    for rx, ry in resources:
        ds = man(sx, sy, rx, ry)
        do = man(ox, oy, rx, ry)
        # Prefer resources we can reach earlier; if tied, prefer closer to us; add a mild "race" emphasis.
        adv = (do - ds) * 1000 + (do == ds) * 50 - ds
        # Slightly de-prioritize resources that are also close to opponent after one move.
        opp1 = min((man(rx, ry, ox + dx, oy + dy) for dx, dy in deltas if inb(ox + dx, oy + dy)), default=do)
        adv -= (do - opp1) * 10
        if adv > best_adv:
            best_adv = adv
            best_target = (rx, ry)

    tx, ty = best_target

    # One-step lookahead: evaluate next positions with a contested-aware score.
    best_move = [0, 0]
    best_score = -10**18
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if blocked(nx, ny):
            nx, ny = sx, sy
        score = 0
        # Distance-based contested score over all resources (kept cheap).
        for rx, ry in resources:
            ds = man(nx, ny, rx, ry)
            do = man(ox, oy, rx, ry)
            score += (do - ds) * 1000 - ds
        # Extra focus on chosen target to prevent drifting.
        score += 5000 - man(nx, ny, tx, ty) * 10
        if score > best_score:
            best_score = score
            best_move = [dx if not blocked(sx + dx, sy) else 0, dy if not blocked(sx, sy + dy) else 0]
            if blocked(sx + dx, sy + dy):
                best_move = [0, 0]

    # Ensure move stays within allowed deltas.
    if best_move[0] < -1:
        best_move[0] = -1
    if best_move[0] > 1:
        best_move[0] = 1
    if best_move[1] < -1:
        best_move[1] = -1
    if best_move[1] > 1:
        best_move[1] = 1
    return [int(best_move[0]), int(best_move[1])]